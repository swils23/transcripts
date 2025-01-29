import ffmpeg
import torch
import torch.backends.cuda
import whisper
import warnings


def transcribe(video_path: str) -> str:
    # Use ffmpeg to load and convert audio to the format Whisper expects
    warnings.filterwarnings("ignore")
    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = whisper.load_model(
            "medium.en" if device.type == "cuda" else "small.en", device=device
        )
        result = model.transcribe(video_path)
        transcript = result["text"]
        return transcript

    except ffmpeg.Error as e:
        print("stdout:", e.stdout.decode("utf8"))
        print("stderr:", e.stderr.decode("utf8"))
        raise e


def download(url: str, output: str):
    video = ffmpeg.input(url)
    audio = video.audio
    out = ffmpeg.output(audio, output, format="mp4")
    ffmpeg.run(out)
