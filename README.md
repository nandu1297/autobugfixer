# Phase 1: GitHub + MCP + PostgreSQL

This backend implements only Phase 1. It reads repositories and issues through the GitHub MCP server and can store them in existing PostgreSQL tables.

## Files

- `app.py`: FastAPI application and HTTP endpoints.
- `database.py`: Opens PostgreSQL connections, executes SQL, and closes resources.
- `github.py`: Loads the GitHub token from `.env`.
- `mcpclient.py`: Connects to the official GitHub MCP server over stdio.
- `services/repository_service.py`: Repository insert/update and database reads.
- `services/services.py`: Issue insert/update and database reads.
- `requirements.txt`: Minimal Phase 1 dependencies.

## Environment

The existing `.env` may use either these separate settings:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=database_name
DB_USER=postgres
DB_PASSWORD=password
GITHUB_TOKEN=github_token
```

`git_token` is also accepted for compatibility with the existing setup. Never commit `.env` or expose its values in logs. A GitHub token authenticates the MCP server without asking for a GitHub password.

## Run

From the project root, using the existing virtual environment:

```powershell
Push-Location backend
..\.conda\python.exe -m uvicorn app:app --reload
Pop-Location
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Endpoints

- `GET /db-test`: runs `SELECT 1`.
- `GET /github-tools`: lists tools supplied dynamically by GitHub MCP.
- `GET /repositories/{owner}/{repo}`: searches for repository information through MCP.
- `POST /repositories/{owner}/{repo}/sync`: saves repository information.
- `GET /repositories/{owner}/{repo}/issues`: lists GitHub issues through MCP.
- `POST /repositories/{owner}/{repo}/issues/sync`: saves or updates issues.
- `GET /repositories/{owner}/{repo}/issues/db`: reads stored issues from PostgreSQL.

The sync code does not create, alter, or delete tables. It expects an existing `repositories` table with `github_id`, `owner`, `name`, `description`, `default_branch`, and `url` columns, with a unique `(owner, name)` constraint. It expects an `issues` table with `owner`, `repository`, `issue_number`, `title`, `body`, `state`, `author`, `created_at`, and `labels` columns, with a unique `(owner, repository, issue_number)` constraint.

The current database inspection found only `public.users`, so repository and issue sync will return a clear `503` until those existing tables are created manually in pgAdmin.
