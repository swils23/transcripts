import whisper
import torch
import torch.backends.cuda
import os
import re

import argparse

import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

TRANSCRIPT_OUTPUT_DIR = "data/transcripts/"

def transcribe(video_path, fast=False):
    if os.path.exists(video_path) == False:
        print("Video does not exist.")
        return

    if os.path.exists(TRANSCRIPT_OUTPUT_DIR) == False:
        os.mkdir(TRANSCRIPT_OUTPUT_DIR)
    output_path = TRANSCRIPT_OUTPUT_DIR + re.sub(r"\.\w+$", ".txt", video_path).replace(
        "data/videos/", ""
    )
    # if transcript already
    if os.path.exists(output_path):
        x = input("Transcript already exists. Overwrite? (Y/n): ")
        if x.lower() != "y":
            return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if fast or device == "cpu":
        model_size = "small.en"
    else:
        model_size = "medium.en"
    print(f"Transcribing {video_path}\n\tModel: ({model_size}) on ({device}).")

    model = whisper.load_model(model_size, device=device)
    result = model.transcribe(video_path)


    # Save the transcript to a file. yank the extension off the video path and replace it with .txt
    output_path = TRANSCRIPT_OUTPUT_DIR + re.sub(r"\.\w+$", ".txt", video_path).replace(
        "data/videos/", ""
    )
    result_utf8 = result["text"].encode("utf-8")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_utf8.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Download and transcribe videos.")
    parser.add_argument("-v", "--video", type=str, help="Path to the video file")
    parser.add_argument(
        "-b",
        "--bulk",
        action="store_true",
        help="Transcribe all videos in the /data/videos directory",
    )
    parser.add_argument("--fast", action="store_true", help="Use a faster model")
    parser.add_argument("-u", "--url", type=str, help="URL of the video to download")
    
    args = parser.parse_args()

    fast = args.fast

    if args.video:
        if "/" in args.video:
            video_path = args.video
        else:
            video_path = "data/videos/" + args.video if args.video.endswith(".mp4") else "data/videos/" + args.video + ".mp4"

        transcribe(video_path, fast)
    elif args.bulk:
        for video in os.listdir("data/videos/"):
            if video.endswith(".mp4"):
                transcribe("data/videos/" + video, fast)

if __name__ == "__main__":
    main()
