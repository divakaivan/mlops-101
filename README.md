Setup:

- `uv venv -p 3.11`
- `source venv/bin/activate`
- `uv pip install -r pyproject.toml --all-extras`
- `uv lock`

Other:

`export UV_ENV_FILE=".env"` - to run uv with an env file by default
`pre-commit install` - to run the pre-commit hooks automatically
