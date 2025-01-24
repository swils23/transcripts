from urllib.parse import urlparse
from .download import Video


def normalize_url(url: str) -> tuple[bool, str]:
    try:
        url = url.strip()
        url = urlparse(url).geturl()
        # ensure http or https (default to https)
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return True, url
    except Exception as e:
        return False, f"Invalid URL: {url}"


def download_and_transcribe(url: str) -> str:
    video = Video(url)
    video.download()
    video.transcribe()
    return video.transcript
