"""dsh.llm.messages 投影回归测试。

覆盖 messages_to_openai 的 OpenAI/火山方舟兼容投影：
- tool-call 块必须进 assistant 消息顶层 ``tool_calls`` 数组（方舟 400 修复案）；
- tool-result 块折叠为 role=tool 消息；
- 纯文本/无内容消息行为。
"""
from __future__ import annotations

from dsh.llm.messages import (ContentBlock, Message, messages_to_openai)


def _assistant_with_tool_call(call_id: str = "call-1",
                              name: str = "bash",
                              arguments: str = "{\"script\": \"echo hi\"}") -> Message:
    return Message.assistant([
        ContentBlock.text_block("我调用工具"),
        ContentBlock.tool_call_block(call_id, name, arguments),
    ])


def test_tool_call_goes_to_top_level_tool_calls():
    """tool-call 块投影到 assistant 顶层 tool_calls，而非 content。"""
    history = [
        Message.user("跑一下"),
        _assistant_with_tool_call(),
        Message.assistant([ContentBlock.tool_result_block(
            "call-1", "hi", is_error=False)]),
    ]
    out = messages_to_openai(history)

    assert out[0] == {"role": "user",
                      "content": [{"type": "text", "text": "跑一下"}]}

    # assistant 消息：content 只剩 text，tool_calls 在顶层
    assistant = out[1]
    assert assistant["role"] == "assistant"
    assert assistant["content"] == [{"type": "text", "text": "我调用工具"}]
    assert assistant["tool_calls"] == [{
        "id": "call-1", "type": "function",
        "function": {"name": "bash", "arguments": "{\"script\": \"echo hi\"}"}}]

    # tool-result → role=tool
    assert out[2] == {"role": "tool", "tool_call_id": "call-1", "content": "hi"}


def test_tool_call_only_message_gets_empty_content():
    """纯 tool-call（无文本）的 assistant 消息 content 为空串（端点要求）。"""
    history = [Message.assistant([
        ContentBlock.tool_call_block("c2", "bash", "{}")])]
    out = messages_to_openai(history)
    assistant = out[0]
    assert assistant["content"] == ""
    assert assistant["tool_calls"][0]["id"] == "c2"


def test_missing_call_id_falls_back_to_index():
    """call_id 缺失时回退 call-<index>（OpenAI 要求 id 存在）。"""
    msg = Message.assistant([
        ContentBlock.tool_call_block("", "ls", "{}"),
        ContentBlock.tool_call_block("", "pwd", "{}"),
    ])
    out = messages_to_openai([msg])
    calls = out[0]["tool_calls"]
    assert [c["id"] for c in calls] == ["call-0", "call-1"]


def test_plain_text_messages_unchanged():
    """纯文本历史保持原样（无 tool_calls / 无 tool 消息）。"""
    history = [Message.user("hi"), Message.assistant([ContentBlock.text_block("hello")])]
    out = messages_to_openai(history)
    assert len(out) == 2
    assert out[1]["content"] == [{"type": "text", "text": "hello"}]
    assert "tool_calls" not in out[1]
