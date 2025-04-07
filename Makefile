test:
	uv sync --all-extras
	uv run pytest

cov:
	uv sync --all-extras
	uv run coverage run --source=gorillacompression -m pytest
	uv run coverage report -m
	uv run coverage html
