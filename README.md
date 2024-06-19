# transcripts

---

# Installation

#### Windows
**Important**: Make sure you are using powershell, NOT cmd.
```sh
# Install Just
winget install --id Casey.Just --exact

# Setup
git clone https://github.com/swils23/transcripts.git
cd transcripts
just initial_setup
```

---

#### Ubuntu

```sh
wget -qO - 'https://proget.makedeb.org/debian-feeds/prebuilt-mpr.pub' | gpg --dearmor | sudo tee /usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg 1> /dev/null
echo "deb [arch=all,$(dpkg --print-architecture) signed-by=/usr/share/keyrings/prebuilt-mpr-archive-keyring.gpg] https://proget.makedeb.org prebuilt-mpr $(lsb_release -cs)" | sudo tee /etc/apt/sources.list.d/prebuilt-mpr.list
sudo apt update
sudo apt-get install just

python -m venv .venv
source .venv/bin/activate

pip install uv
uv pip install -r requirements.txt
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```