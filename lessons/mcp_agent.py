import asyncio
import os

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

FINISH_TOOL = {
    "name": "finish",
    "description": "Declare that the task is finished (or impossible), with a self-assessment.",
    "input_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["success", "reason"],
    },
}

SYSTEM_PROMPT = """You control a web browser through tools to complete a task. \
Use browser_navigate to go to pages, browser_snapshot to see the current page's \
accessibility tree (elements and their refs), and browser_click / browser_type to \
interact using the refs from the snapshot. Call finish when the task is complete \
or impossible, with an honest success=true/false assessment."""


def mcp_tools_to_anthropic(mcp_tools):
    return [{"name": t.name, "description": t.description or "", "input_schema": t.input_schema} for t in mcp_tools]


async def run_task(session, task, mcp_tools, max_steps=10):
    tools = mcp_tools_to_anthropic(mcp_tools) + [FINISH_TOOL]
    messages = [{"role": "user", "content": f"Task: {task}"}]

    for step in range(max_steps):
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            tools=tools,
            tool_choice={"type": "any"},
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        finished = False
        for tool_use in [b for b in response.content if b.type == "tool_use"]:
            print(f"  [step {step + 1}] {tool_use.name}({tool_use.input})")
            if tool_use.name == "finish":
                print(f"  FINISHED: success={tool_use.input['success']} reason={tool_use.input['reason']}")
                finished = True
                break
            result = await session.call_tool(tool_use.name, tool_use.input)
            text = result.content[0].text if result.content else ""
            tool_results.append({"type": "tool_result", "tool_use_id": tool_use.id, "content": text[:2000]})

        if finished:
            return
        messages.append({"role": "user", "content": tool_results})

    print("  Max steps reached without finishing.")


async def main():
    params = StdioServerParameters(command="npx", args=["-y", "@playwright/mcp@latest"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_tools = (await session.list_tools()).tools
            await run_task(session, "Go to https://example.com and tell me the page title.", mcp_tools)
            # Note: file:// URLs are blocked by Playwright MCP for security --
            # the app must be served over HTTP (see tasks_eval/run_eval_mcp.py,
            # which serves it automatically instead of needing a manual server).
            await run_task(
                session,
                "Go to http://localhost:8000/index.html and mark the task 'Read a book' as complete.",
                mcp_tools,
            )

asyncio.run(main())