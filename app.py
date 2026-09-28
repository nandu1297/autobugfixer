from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import run_query
from github import get_repository_from_github, parse_github_url
from mcpclient import call_github_tool, get_github_tools
from services.services import get_saved_issues, save_issues
from services.repository_service import save_repository

app = FastAPI()


class RepositoryRequest(BaseModel):
    repo_url: str


@app.get("/")
def root():
    return {
        "message": "Autonomous Bug Fixer"
    }


@app.get("/db-test")
def db_test():
    run_query("SELECT 1", fetch=True)
    return {"status": "database connected"}


@app.get("/github-tools")
async def github_tools():
    return {"tools": [tool.name for tool in await get_github_tools()]}


@app.post("/repositories/connect")
async def connect_repository(request: RepositoryRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        repository = await get_repository_from_github(owner, repo)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (RuntimeError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"GitHub/MCP could not retrieve the repository: {error}") from error

    try:
        save_repository(repository)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Database could not save the repository: {error}") from error

    return {
        "message": "Repository connected successfully",
        "repository": {
            "id": repository["id"],
            "owner": repository["owner"],
            "name": repository["name"],
            "url": repository["url"],
            "default_branch": repository["default_branch"],
        },
    }


async def _github_tool(tool_name: str, arguments: dict):
    try:
        return await call_github_tool(tool_name, arguments)
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.get("/repositories/{owner}/{repo}")
async def get_repository(owner: str, repo: str):
    return await _github_tool("search_repositories", {"query": f"{owner}/{repo}"})


@app.post("/repositories/{owner}/{repo}/sync")
async def sync_repository(owner: str, repo: str):
    repository = await get_repository(owner, repo)
    try:
        save_repository(repository)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Repository table is unavailable: {error}") from error
    return {"message": "repository synced successfully", "repository": repository}


@app.get("/repositories/{owner}/{repo}/issues")
async def get_repository_issues(owner: str, repo: str):
    return await _github_tool("list_issues", {"owner": owner, "repo": repo, "state": "all"})


@app.post("/repositories/{owner}/{repo}/issues/sync")
async def sync_repository_issues(owner: str, repo: str):
    issues = await get_repository_issues(owner, repo)
    try:
        save_issues(owner, repo, issues)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Issues table is unavailable: {error}") from error
    return {"message": "issues synced successfully", "issues": issues}


@app.get("/repositories/{owner}/{repo}/issues/db")
def get_repository_issues_from_db(owner: str, repo: str):
    try:
        return {"issues": get_saved_issues(owner, repo)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Issues table is unavailable: {error}") from error