import os
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


def get_github_token() -> str:
	"""Return the GitHub token without hardcoding it in source code."""
	token = os.getenv("GITHUB_TOKEN") or os.getenv("git_token")
	if not token:
		raise RuntimeError("GITHUB_TOKEN or git_token is missing from .env")
	return token


def parse_github_url(repo_url: str) -> tuple[str, str]:
	"""Return the owner and repository name from a GitHub URL."""
	parsed = urlparse(repo_url)

	if parsed.netloc.lower() != "github.com":
		raise ValueError("Invalid GitHub repository URL")

	parts = parsed.path.strip("/").split("/")
	if len(parts) < 2:
		raise ValueError("Invalid GitHub repository URL")

	owner = parts[0]
	repo = parts[1]

	if repo.endswith(".git"):
		repo = repo[:-4]

	if not owner or not repo:
		raise ValueError("Invalid GitHub repository URL")

	return owner, repo


def _decode_mcp_response(response: Any) -> Any:
	"""Convert the GitHub MCP text envelope into ordinary Python data."""
	if isinstance(response, list):
		for item in response:
			if isinstance(item, dict) and item.get("type") == "text":
				return json.loads(item["text"])
		return response
	if isinstance(response, dict) and isinstance(response.get("text"), str):
		return json.loads(response["text"])
	return response


async def get_repository_from_github(owner: str, repo: str) -> dict[str, Any]:
	"""Retrieve and normalize one repository through the existing MCP client."""
	from mcpclient import call_github_tool

	response = await call_github_tool("search_repositories", {"query": f"{owner}/{repo}"})
	decoded_response = _decode_mcp_response(response)
	items = decoded_response.get("items", []) if isinstance(decoded_response, dict) else []
	repository = next(
		(
			item
			for item in items
			if item.get("full_name", "").lower() == f"{owner}/{repo}".lower()
		),
		None,
	)
	if repository is None:
		raise LookupError("GitHub repository was not found")

	repository_owner = repository.get("owner") or {}
	return {
		"id": repository.get("id"),
		"owner": repository_owner.get("login", owner),
		"name": repository.get("name", repo),
		"description": repository.get("description"),
		"default_branch": repository.get("default_branch"),
		"url": repository.get("html_url", f"https://github.com/{owner}/{repo}"),
	}
