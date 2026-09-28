from typing import Any

from database import database_cursor


def save_repository(repository: dict[str, Any]) -> None:
	"""Store GitHub repository data in the existing repositories table."""
	with database_cursor() as cursor:
		cursor.execute(
			"""
			INSERT INTO repositories
				(github_id, owner, name, description, default_branch, url)
			VALUES (%s, %s, %s, %s, %s, %s)
			ON CONFLICT (owner, name) DO UPDATE SET
				description = EXCLUDED.description,
				default_branch = EXCLUDED.default_branch,
				url = EXCLUDED.url
			""",
			(
				repository.get("id"),
				repository.get("owner"),
				repository.get("name"),
				repository.get("description"),
				repository.get("default_branch"),
				repository.get("url"),
			),
		)


def get_saved_repositories() -> list[dict[str, Any]]:
	"""Read repositories from PostgreSQL."""
	with database_cursor() as cursor:
		cursor.execute(
			"SELECT github_id, owner, name, description, default_branch, url "
			"FROM repositories ORDER BY name"
		)
		columns = [column.name for column in cursor.description]
		return [dict(zip(columns, row)) for row in cursor.fetchall()]
