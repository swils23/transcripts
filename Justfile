@requirements:
    uv pip compile pyproject.toml -o requirements.txt
    uv pip install -r requirements.txt