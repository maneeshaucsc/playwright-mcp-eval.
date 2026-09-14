"""The agent loop: Claude picks one action per turn via tool use, Playwright
executes it, the resulting page state is fed back, repeat until the agent
calls `finish` or runs out of steps.
"""
import os

from anthropic import Anthropic
from playwright.sync_api import Page

from actions import InvalidAction, execute
from config import AGENT_MODEL, AGENT_SYSTEM_PROMPT, MAX_STEPS
from state import describe_page

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TOOLS = [
    {
        "name": "fill",
        "description": "Type text into a textbox on the page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "enum": ["textbox"]},
                "name": {
                    "type": "string",
                    "description": 'Exact accessible name of the textbox, e.g. "New task".',
                },
                "text": {"type": "string"},
            },
            "required": ["role", "name", "text"],
        },
    },
    {
        "name": "click",
        "description": "Click a checkbox, button, or tab on the page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "role": {"type": "string", "enum": ["checkbox", "button", "tab"]},
                "name": {
                    "type": "string",
                    "description": "Exact accessible name, copied verbatim from the page description.",
                },
            },
            "required": ["role", "name"],
        },
    },
    {
        "name": "finish",
        "description": "Declare that the task is finished (or impossible to complete).",
        "input_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "description": "Did you complete the task?"},
                "reason": {"type": "string", "description": "One sentence explaining why."},
            },
            "required": ["success", "reason"],
        },
    },
]


def run_task(page: Page, task_description: str, max_steps: int = MAX_STEPS) -> dict:
    messages = [
        {
            "role": "user",
            "content": f"Task: {task_description}\n\nCurrent page state:\n{describe_page(page)}",
        }
    ]
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
            max_tokens=500,
            system=AGENT_SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "any"},
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        # A single turn can contain multiple tool_use blocks. The API requires
        # a tool_result for every one of them before another request can be
        # sent, so process them all -- unless one is `finish`, in which case
        # the conversation is over and no further request (hence no further
        # tool_result) is needed.
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        tool_results = []

        for tool_use in tool_use_blocks:
            trajectory["steps_taken"] += 1

            if tool_use.name == "finish":
                trajectory["self_reported_success"] = bool(tool_use.input["success"])
                trajectory["self_reported_reason"] = tool_use.input["reason"]
                trajectory["actions"].append({"type": "finish", **tool_use.input})
                finished = True
                break

            action = {"action": tool_use.name, **tool_use.input}
            try:
                execute(page, action)
                new_state = describe_page(page)
                result_text = f"Action executed. New page state:\n{new_state}"
                trajectory["actions"].append({"type": tool_use.name, **tool_use.input, "error": None})
            except InvalidAction as e:
                trajectory["invalid_actions"] += 1
                result_text = f"Error: {e}. Page state unchanged:\n{describe_page(page)}"
                trajectory["actions"].append({"type": tool_use.name, **tool_use.input, "error": str(e)})

            tool_results.append({"type": "tool_result", "tool_use_id": tool_use.id, "content": result_text})

        if finished:
            break

        messages.append({"role": "user", "content": tool_results})
    else:
        trajectory["self_reported_success"] = False
        trajectory["self_reported_reason"] = "Max steps reached without calling finish."

    return trajectory
