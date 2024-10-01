# We're using powershell
set allow-duplicate-recipes
set dotenv-load := true


# set shell := ["powershell", "-Command"]
set shell := ["zsh", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]


@default:
    echo "Please specify a target to run"

[windows]
activate:
    powershell -ExecutionPolicy ByPass -NoExit -Command "./.venv/Scripts/Activate.ps1"
    activate

[windows]
@deactivate:
    deactivate

[windows]
@initial_setup:
    # Execute scripts/initial_setup.ps1
    .\scripts\initial_setup.ps1

[unix]
@initial_setup:
    echo "Run: mkvirtualenv transcripts && workon transcripts && pip install uv && uv pip install -r requirements.txt"

[unix]
rm_venv:
    rm -rf .venv

[windows]
@make_requirements:
    # Execute scripts/make_requirements.py
    pip freeze > requirements.txt
    python scripts\make_requirements.py

[unix]
@make_requirements:
    echo "Making requirements.txt" \
    && uv pip install pip-tools \
    && pip-compile --strip-extras --output-file requirements.txt requirements.in

[unix]
@install: make_requirements
    uv pip install -r requirements.txt

download_only:
    python download.py -b

transcribe_only:
    python transcribe.py -b

transcribe:
    python download.py -b && python transcribe.py -b

transcribe_fast:
    python download.py -b && python transcribe.py -b --fast
