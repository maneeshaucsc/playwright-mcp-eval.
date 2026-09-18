"""Reusable Claude + Playwright-MCP agent loop (cleaned up from the
exploratory mcp_agent.py). Converts the MCP server's own tool schemas into
Claude's tool format and drives a standard tool-use loop against them, with
one extra tool (`finish`) that isn't from MCP at all -- proving custom and
MCP-provided tools can be mixed in a single request.
"""
import os

from anthropic import Anthropic

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

AGENT_MODEL = "claude-sonnet-5"

FINISH_TOOL = {
    "name": "finish",
    "description": "Declare that the task is finished (or impossible), with a self-assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "Did you complete the task?"},
            "reason": {"type": "string", "description": "One sentence explaining why."},
        },
        "required": ["success", "reason"],
    },
}

SYSTEM_PROMPT = """You control a web browser through tools to complete a task on the \
TaskFlow to-do app. Use browser_snapshot to see the current page's accessibility tree \
(elements and their refs) -- refs change after the page re-renders, so take a fresh \
snapshot after any action that changes the page before acting again. Use browser_click \
and browser_type with the `target` ref from the most recent snapshot. If the task \
cannot be completed (e.g. it refers to a task that doesn't exist), call finish with \
success=false and explain why -- don't guess or fabricate an action. Call finish as \
soon as the task is actually done."""


def mcp_tools_to_anthropic(mcp_tools) -> list[dict]:
    return [
        {"name": t.name, "description": t.description or "", "input_schema": t.input_schema}
        for t in mcp_tools
    ]


async def run_task(session, task: str, mcp_tools, max_steps: int = 12) -> dict:
    tools = mcp_tools_to_anthropic(mcp_tools) + [FINISH_TOOL]
    messages = [{"role": "user", "content": f"Task: {task}"}]

    trajectory = {
        "actions": [],
        "invalid_actions": 0,
        "steps_taken": 0,
        "self_reported_success": None,
        "self_reported_reason": None,
    }

    finished = False
    for _ in range(max_steps):
        response = _client.messages.create(
            model=AGENT_MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=tools,
            tool_choice={"type": "any"},
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for tool_use in [b for b in response.content if b.type == "tool_use"]:
            trajectory["steps_taken"] += 1

            if tool_use.name == "finish":
                trajectory["self_reported_success"] = bool(tool_use.input["success"])
                trajectory["self_reported_reason"] = tool_use.input["reason"]
                trajectory["actions"].append({"type": "finish", **tool_use.input})
                finished = True
                break

            result = await session.call_tool(tool_use.name, tool_use.input)
            text = result.content[0].text if result.content else ""
            is_error = bool(getattr(result, "is_error", False)) or text.strip().startswith("### Error")
            if is_error:
                trajectory["invalid_actions"] += 1
            trajectory["actions"].append({
                "type": tool_use.name, **tool_use.input, "error": text[:200] if is_error else None,
            })
            tool_results.append({
                "type": "tool_result", "tool_use_id": tool_use.id, "content": text[:2000],
            })

        if finished:
            break
        messages.append({"role": "user", "content": tool_results})
    else:
        trajectory["self_reported_success"] = False
        trajectory["self_reported_reason"] = "Max steps reached without calling finish."

    return trajectory
