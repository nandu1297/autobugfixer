from typing import Any

from database import database_cursor


def save_issues(owner: str, repo: str, issues: list[dict[str, Any]]) -> None:
	"""Insert or update issues in the existing issues table."""
	with database_cursor() as cursor:
		for issue in issues:
			cursor.execute(
				"""
				INSERT INTO issues
					(owner, repository, issue_number, title, body, state,
					 author, created_at, labels)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
				ON CONFLICT (owner, repository, issue_number) DO UPDATE SET
					title = EXCLUDED.title, body = EXCLUDED.body,
					state = EXCLUDED.state, author = EXCLUDED.author,
					created_at = EXCLUDED.created_at, labels = EXCLUDED.labels
				""",
				(
					owner,
					repo,
					issue.get("number"),
					issue.get("title"),
					issue.get("body"),
					issue.get("state"),
					(issue.get("user") or {}).get("login"),
					issue.get("created_at"),
					",".join(label.get("name", "") for label in issue.get("labels", [])),
				),
			)


def get_saved_issues(owner: str, repo: str) -> list[dict[str, Any]]:
	"""Read one repository's issues from PostgreSQL."""
	with database_cursor() as cursor:
		cursor.execute(
			"SELECT owner, repository, issue_number, title, body, state, author, "
			"created_at, labels FROM issues WHERE owner = %s AND repository = %s "
			"ORDER BY issue_number",
			(owner, repo),
		)
		columns = [column.name for column in cursor.description]
		return [dict(zip(columns, row)) for row in cursor.fetchall()]
