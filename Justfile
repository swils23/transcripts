# We're using powershell

set shell := ["powershell", "-Command"]

@default:
    echo "Please specify a target to run"




activate:
    activate
    


@deactivate:
    deactivate

@initial_setup:
    # Execute scripts/initial_setup.ps1
    .\scripts\initial_setup.ps1


@make_requirements:
    # Execute scripts/make_requirements.py
    pip freeze > requirements.txt
    python scripts\make_requirements.py


@format:
    black .