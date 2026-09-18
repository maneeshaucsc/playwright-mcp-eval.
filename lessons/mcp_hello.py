import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

async def main():
    params = StdioServerParameters(command="npx", args=["-y", "@playwright/mcp@latest"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for t in tools.tools:
                print(t.name, "-", (t.description or "")[:70])

            result = await session.call_tool("browser_navigate", {"url": "https://example.com"})
            print(result.content[0].text[:500])

            snapshot = await session.call_tool("browser_snapshot", {})
            print(snapshot.content[0].text[:500])
            click_result = await session.call_tool("browser_click", {
                "element": "Learn more link",
                "target": "e6",
            })
            print(click_result.content[0].text[:500])

asyncio.run(main())