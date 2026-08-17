"""Temporary audit verification script (delete after use)."""
import asyncio
import sys

print("=== 1. Surface replace ordering (compaction summary placement) ===")
from dsh.session import Session
s = Session("t1")
for i in range(5):
    s.append("user/message", {"content": f"m{i}", "source": {"kind": "user"}},
             surface_op="append")
# replace the OLDEST 3 (0..2), keep last 2 (3,4)
s.append("compaction/summary", {"summary": "SUMMARY"},
         surface_op={"op": "replace", "start": 0, "end": 2},
         source_event_seqs=[0, 1, 2])
msgs = s.derive_messages()
print("surface.nodes =", s.surface.nodes)
print("derived order =", [m.content[0].text if m.content else '?' for m in msgs])
print("EXPECT summary FIRST (oldest), actual order shows summary LAST -> BUG")

print()
print("=== 2. fork boundary validation (mid-turn) ===")
from dsh.session import SessionStore
from dsh.kernel import Context
ctx = Context()
store = SessionStore(ctx, {})
store.apply(ctx)
src = store.create(meta={"cwd": "C:/x"})
src.append("turn/start", {"turn": 1})
src.append("step/start", {"turn": 1, "step": 1})
src.append("assistant/message", {"blocks": [{"kind": "text", "text": "hi"}],
                                  "provider": "m", "model": "m"},
            surface_op="append")
# Now source is mid-turn (no turn/end). fork at latest boundary should fail
try:
    child = store.fork(src)
    print("fork SUCCEEDED (BUG: mid-turn boundary not rejected); child last event =",
          child._events[-1].type)
except ValueError as e:
    print("fork correctly rejected:", e)

print()
print("=== 3. schema: properties/required without type == object ignored ===")
from dsh.tools.schema import assert_supported_schema, validate_value
schema = {"properties": {"a": {"type": "string"}}, "required": ["a"]}
try:
    assert_supported_schema(schema)
    print("assert_supported_schema: ACCEPTED (no 'type' but has properties)")
except Exception as e:
    print("assert_supported_schema rejected:", e)
# Now validate: a NON-dict and a dict missing 'a' should both fail if enforced
for bad in ("not a dict", {}, {"a": 123}, {"a": "ok"}):
    try:
        validate_value(bad, schema)
        print(f"  validate_value({bad!r}) -> PASSED (constraints silently ignored)")
    except Exception as e:
        print(f"  validate_value({bad!r}) -> REJECTED: {type(e).__name__}")

print()
print("=== 4. temperature=0 override via `or` ===")
options = {"temperature": 0.0}
defaults = {"temperature": 0.7}
result = options.get("temperature") or defaults.get("temperature")
print("temperature 0.0 ->", result, "(0.0 silently replaced -> BUG)")

print()
print("=== 5. ApprovalService config=None crash ===")
try:
    from dsh.agent.approval import ApprovalService
    a = ApprovalService(Context())
    print("ApprovalService(ctx) constructed, default =", a._default)
except Exception as e:
    print("ApprovalService(ctx) crashed:", type(e).__name__, e)

print()
print("=== 6. SessionStore.flush return value (always True?) ===")
ctx2 = Context()
store2 = SessionStore(ctx2, {})
store2.apply(ctx2)
sess = store2.create()

async def check_flush():
    # No persistence plugin mounted at all
    r = await store2.flush(sess)
    print("flush() with NO persistence listeners ->", r, "(expected False if 'any persistence listener')")
asyncio.get_event_loop().run_until_complete(check_flush())

print()
print("DONE")
