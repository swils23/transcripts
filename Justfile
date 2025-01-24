@requirements:
    uv pip compile pyproject.toml -o requirements.txt
    uv pip install -r requirements.txt

@format:
    uv tool run black ./src 

@initial_setup:
    uv tool install black