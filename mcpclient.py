import os
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient

from github import get_github_token


def _client() -> MultiServerMCPClient:
	"""Create a client for the official GitHub MCP server over stdio."""
	return MultiServerMCPClient(
		{
			"github": {
				"transport": "stdio",
				"command": "npx",
				"args": ["-y", "@modelcontextprotocol/server-github"],
				"env": {
					**os.environ,
					"GITHUB_PERSONAL_ACCESS_TOKEN": get_github_token(),
				},
			}
		}
	)


async def get_github_tools() -> list[Any]:
	"""Connect to GitHub MCP and return tools supplied by the server."""
	return await _client().get_tools()


async def call_github_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
	"""Find a named MCP tool and invoke it with JSON-like arguments."""
	tools = await get_github_tools()
	for tool in tools:
		if tool.name == tool_name:
			return await tool.ainvoke(arguments)
	available = ", ".join(tool.name for tool in tools)
	raise RuntimeError(f"MCP tool '{tool_name}' is unavailable. Available tools: {available}")
