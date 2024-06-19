# root of the project is up one level from this script
$root = (Get-Item -Path ".\").FullName

# if we are not in project root, error
if (-Not($root -like "*\mediasite-dl")) {
    Write-Host "Please run this script from the root of the project"
    exit
}

# Check if the virtual environment directory does not exist
if (-Not (Test-Path "$root\.venv")) {
    # The virtual environment directory does not exist, so create it
    python -m venv "$root\.venv"
    Write-Host "Virtual environment created at $root\.venv"
} else {
    # The virtual environment directory already exists
    Write-Host "Virtual environment already exists at $root\.venv"
}

# activate virtualenv
$activate = $root + "\.venv\Scripts\Activate.ps1"
. $activate


# install dependencies
pip install uv
uv pip install -r requirements.txt
uv pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124

