# Installation

Prerequisites:
- [Python][1]
- [UV][2]

Clone the repository
```bash
# HTTPS
git clone https://github.com/swils23/transcripts.git
# SSH
git clone git@github.com:swils23/transcripts.git
```

Navigate to the repository
```bash
cd transcripts
```

Make virtual environment
```bash
uv venv
```

Activate virtual environment
```bash
.venv\Scripts\activate # Windows
source .venv/bin/activate # Linux / MacOS
```

Install requirements
```bash
uv pip install -r requirements.txt
```

# Usage

Activate virtual environment
```bash
# Windows --------------------------------  
.venv\Scripts\activate
# Linux / MacOS ----------------------------
source .venv/bin/activate
```

Run the script
```bash
python -m src.transcripts.main
```

⚠️ **IMPORTANT**: HOW TO GET THE RIGHT URL FOR MEDIASITE
1. Go to the video - DON'T PRESS PLAY (if you do, refresh the page and try again)
2. Open Developer Tools > Network
3. NOW press play
4. Filter the requests by `manifest(audio`
5. Right click request > Copy > Copy URL 🎉



[1]: https://www.python.org/downloads/
[2]: https://docs.astral.sh/uv/#getting-started

