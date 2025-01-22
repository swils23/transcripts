from enum import Enum, auto
import re
import io
import ffmpeg
import torch
import torch.backends.cuda
import whisper
import numpy as np
import warnings


class VideoType(Enum):
    MEDIASITE = auto()
    YOUTUBE = auto()
    GENERIC = auto()


class Video:
    def __init__(self, url: str):
        self.url = url
        self.type = self._check_type()
        if self.type == VideoType.MEDIASITE:
            self.url = self._mediasite_video_to_audio(self.url)

        # Downloads
        self.video = io.BytesIO()
        self.is_downloaded = False

        # Transcription
        self.transcript = None

    def download(self):
        if self.type == VideoType.YOUTUBE:
            return self._download_youtube(self.url)
        else:
            return self._download_ffmpeg(self.url)

    def transcribe(self):
        """Try to transcribe with whisper"""
        if not self.is_downloaded:
            raise ValueError("Video not downloaded")

        # Reset buffer position
        self.video.seek(0)

        # Use ffmpeg to load and convert audio to the format Whisper expects
        warnings.filterwarnings("ignore")
        try:
            process = (
                ffmpeg.input("pipe:", format="mp3")  # Read from pipe since we have BytesIO
                .output("pipe:", format="f32le", acodec="pcm_f32le", ac=1, ar=16000)
                .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
            )

            # Feed the input
            audio_data, err = process.communicate(input=self.video.read())

            # Convert to numpy array
            audio_np = np.frombuffer(audio_data, np.float32)

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model = whisper.load_model("medium.en" if device.type == "cuda" else "small.en", device=device)
            result = model.transcribe(audio_np)
            self.transcript = result["text"]
            return self.transcript

        except ffmpeg.Error as e:
            print("stdout:", e.stdout.decode("utf8"))
            print("stderr:", e.stderr.decode("utf8"))
            raise e

    def _check_type(self):
        if self.url.startswith("https://ondem-a.us-a.mediasite.com/MediasiteDeliver/"):
            return VideoType.MEDIASITE
        elif self.url.startswith("https://www.youtube.com/"):
            return VideoType.YOUTUBE
        else:
            return VideoType.GENERIC

    def _mediasite_video_to_audio(self, video_url: str):
        """
        Converts mediasite video URL to audio URL
        """
        generic_audio_manifest = "audio=mp4a_eng_160000,format=m3u8-aapl-isoff"  # may not be universal
        if not video_url.startswith("https://ondem-a.us-a.mediasite.com/MediasiteDeliver/"):
            raise NotImplementedError("This function only works with mediasite URLs")

        # First check if it's a simple format URL
        pattern = re.compile(r"manifest\(format=m3u8-aapl-isoff,.*?\)")
        match = pattern.search(video_url)
        if match:
            # Replace the entire manifest part with our audio manifest
            return video_url.replace(match.group(0), f"manifest({generic_audio_manifest})")

        # Check if it's a video URL with explicit video parameter
        pattern = re.compile(r"manifest\(video=(.*?),format=m3u8-aapl-isoff\)")
        match = pattern.search(video_url)
        if match:
            print("Warning: This is a video URL. Coercing into audio URL")
            video_format = match.group(1)
            audio_url = video_url.replace(f"video={video_format}", generic_audio_manifest)
            print(f"Coerced into audio URL: {audio_url}")
            return audio_url

        # Check if it's already an audio URL
        pattern = re.compile(r"manifest\(audio=(.*?),format=m3u8-aapl-isoff\)")
        match = pattern.search(video_url)
        if match:
            return video_url

        raise ValueError("Invalid URL. Must be a mediasite video or audio URL")

    def _download_youtube(self, url: str):
        """Download youtube video using yt-dlp"""
        raise NotImplementedError("Not implemented")

    def _download_ffmpeg(self, url: str):
        """Download video using ffmpeg and write directly to BytesIO buffer"""
        process = (
            ffmpeg.input(url)
            .output("pipe:", format="mp3", acodec="libmp3lame")
            .overwrite_output()
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

        out, err = process.communicate()

        self.video.write(out)
        self.video.seek(0)
        self.is_downloaded = True
        print(f"Downloaded audio to buffer, size: {self.video.getbuffer().nbytes} bytes")
