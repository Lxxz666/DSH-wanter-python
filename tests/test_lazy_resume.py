"""懒加载续聊（第二版）端到端测试。

覆盖 server 的「跨重启恢复 + 首次发消息按需 resume」链路：
1. 实例 A：创建会话、发消息、flush 持久化（JSONL 落盘）。
2. 实例 B（模拟重启，同一持久化目录）：_restore_sessions 恢复会话元数据，
   但不启动 agent driver（避免自动跑 turn）。
3. 通过 /api/sessions/{id}/messages 首次发消息 → 懒加载 resume agent（续聊），
   历史事件完整保留、新消息追加、agent 恢复运行。
"""
import asyncio
import os

from fastapi.testclient import TestClient

from dsh.boot import boot
from dsh.server.app import build_app, _restore_sessions


def _persist_patch(tmp_path):
    """把持久化目录隔离到 tmp_path，避免污染 ~/.dsh/sessions。"""
    return [([{"id": "persistence",
               "config": {"dir": str(tmp_path / "sessions")}}],
             "test-persist-dir")]


async def test_lazy_resume_second_edition(tmp_path):
    # ---- 实例 A：创建会话并持久化 ----
    ctx_a, tree_a = await boot(profile="headless", workspace=str(tmp_path),
                               mock_llm=True,
                               extra_patches=_persist_patch(tmp_path))
    try:
        app_a = build_app(ctx_a)
        client_a = TestClient(app_a)
        # 创建会话
        res = client_a.post("/api/sessions")
        assert res.status_code == 200
        sid = res.json()["id"]
        # 发消息（agent 运行）
        res = client_a.post(f"/api/sessions/{sid}/messages",
                            json={"content": "第一轮：你好"})
        assert res.status_code == 200
        # 等待 agent 完成 turn 并 flush 持久化
        agent = ctx_a.agents.get(sid)
        assert agent is not None
        await agent.when_idle()
        session = ctx_a.sessions.get(sid)
        await ctx_a.sessions.flush(session)
        # 确认 JSONL 已落盘
        pdir = tmp_path / "sessions"
        files = [f for f in os.listdir(pdir) if f.endswith(".jsonl")]
        assert len(files) == 1
    finally:
        await tree_a.dispose()

    # ---- 实例 B：模拟重启，恢复会话（懒加载） ----
    ctx_b, tree_b = await boot(profile="headless", workspace=str(tmp_path),
                               mock_llm=True,
                               extra_patches=_persist_patch(tmp_path))
    try:
        await _restore_sessions(ctx_b)
        # 会话元数据已恢复，但 agent 未启动（懒加载）
        restored = ctx_b.sessions.get(sid)
        assert restored is not None
        assert ctx_b.agents.get(sid) is None  # 未 resume，无 agent driver

        app_b = build_app(ctx_b)
        client_b = TestClient(app_b)
        # 事件端点：历史事件完整可见
        events = client_b.get(f"/api/sessions/{sid}/events").json()["events"]
        assert len(events) >= 1
        assert any(e["type"] == "user/message" for e in events)

        # 首次发消息 → 懒加载 resume agent（续聊）
        res = client_b.post(f"/api/sessions/{sid}/messages",
                            json={"content": "第二轮：续聊"})
        assert res.status_code == 200
        agent_b = ctx_b.agents.get(sid)
        assert agent_b is not None  # 已懒加载 resume
        await agent_b.when_idle()

        # 新消息已追加到会话，历史保留
        session_b = ctx_b.sessions.get(sid)
        types = [e.type for e in session_b.events]
        assert types.count("user/message") >= 2
        contents = [e.data.get("content") for e in session_b.events
                    if e.type == "user/message"]
        assert "第一轮：你好" in contents
        assert "第二轮：续聊" in contents
    finally:
        await tree_b.dispose()


async def test_lazy_resume_unknown_session_404(tmp_path):
    """懒加载：不存在的会话 id 发消息 → 404（不误建）。"""
    ctx, tree = await boot(profile="headless", workspace=str(tmp_path),
                           mock_llm=True,
                           extra_patches=_persist_patch(tmp_path))
    try:
        await _restore_sessions(ctx)
        app = build_app(ctx)
        client = TestClient(app)
        res = client.post("/api/sessions/ghost/messages",
                          json={"content": "hi"})
        assert res.status_code == 404
    finally:
        await tree.dispose()
