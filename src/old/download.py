import sys
import whisper
import torch
import torch.backends.cuda
import os
import re
import ffmpeg
import argparse
import yt_dlp

VIDEO_OUTPUT_DIR = "data/videos/"


def _mediasite_video_to_audio(video_url):
    """
    Converts mediasite video URL to audio URL
    """
    generic_audio_manifest = (
        "audio=mp4a_eng_193657,format=m3u8-aapl-isoff"  # TODO this may not be universal
    )
    if not video_url.startswith("https://ondem-a.us-a.mediasite.com/MediasiteDeliver/"):
        raise NotImplementedError("This function only works with mediasite URLs")

    # Check if the URL is a video URL
    # grab contents of manifest()
    pattern = re.compile(r"manifest\(video=(.*?),format=m3u8-aapl-isoff\)")
    match = pattern.search(video_url)

    if match:
        print("Warning: This is a video URL. Coercing into audio URL")
        video_format = match.group(1)
        audio_url = video_url.replace(f"video={video_format}", generic_audio_manifest)
        print(f"Coerced into audio URL: {audio_url}")
        return audio_url
    
    # Check if the URL is an audio URL
    pattern = re.compile(r"manifest\(audio=(.*?),format=m3u8-aapl-isoff\)")
    match = pattern.search(video_url)
    if match:
        return video_url
    
    raise ValueError("Invalid URL. Must be a mediasite video or audio URL")


def _parse_url(video_url: str):
    video_url = video_url.strip()
    # TODO maybe replace \ with empty string?
    print(video_url)

    if video_url.startswith("https://ondem-a.us-a.mediasite.com/MediasiteDeliver/"):
        return _mediasite_video_to_audio(video_url)

    return video_url


def _ffmpeg_download(video_url, output=None):
    """
    Downloads a video using ffmpeg.
    NOTE: This only downloads the audio track currently since all we need is the audio for generating transcripts
    """
    if output is None:
        raise ValueError("output must be specified")
    # ffmpeg -i "url" -c copy "video_name".mp4
    video = ffmpeg.input(video_url)
    audio = video.audio
    out = ffmpeg.output(audio, output)
    ffmpeg.run(out)


def _yt_dlp_download(video_url, output=None):
    if output is None:
        raise ValueError("output must be specified")
    """
    Downloads a video using yt-dlp.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def _check_dirs():
    """
    ensure that from the directory of this file, we have data/, data/videos/, data/transcripts/
    """
    if not os.path.exists("data/"):
        os.mkdir("data/")
    if not os.path.exists(VIDEO_OUTPUT_DIR):
        os.mkdir(VIDEO_OUTPUT_DIR)
    if not os.path.exists("data/transcripts/"):
        os.mkdir("data/transcripts/")


def _get_output_path(name=None):
    """
    Generate a name for a video if none is provided
    """
    if name is None:
        i = 1
        while os.path.exists(f"data/videos/untitled_{i}.mp4"):
            i += 1
        name = f"untitled_{i}.mp4"
    name = name.strip()
    name = name if name.endswith(".mp4") else name + ".mp4"
    return VIDEO_OUTPUT_DIR + name


def _check_overwrite(output_file=None):
    if os.path.exists(output_file):
        x = input("Video already exists. Overwrite? (Y/n): ")
        if x.lower() != "y":
            return False
    return True


def download_video(video_url, video_name=None):
    # Setup and cleaning
    _check_dirs()
    video_url = _parse_url(video_url)
    output_file = _get_output_path(name=video_name)
    proceed = _check_overwrite(output_file)
    if not proceed:
        print("Skipping download")
        return

    print(f"Downloading {video_url} to {output_file}")
    if video_url.startswith("https://www.youtube.com/"):
        _yt_dlp_download(video_url, output=output_file)
    else:
        _ffmpeg_download(video_url, output=output_file)


def main():
    # -u --url URL downloads the video from the URL
    # -n --name NAME downloads the video from the URL and saves it as NAME
    # -b --bulk FILE downloads all videos in the file, one URL and optionally name per line

    parser = argparse.ArgumentParser(description="Download videos to data/video/")

    parser.add_argument("-u", "--url", type=str, help="URL of the video to download")
    parser.add_argument("-n", "--name", type=str, help="Name of the video to download")
    parser.add_argument(
        "-b", "--bulk", action="store_true", help="File containing URLs of videos to download"
    )
    parser.add_argument(
        "--file", type=str, help="File containing URLs of videos to download", dest="file"
    )

    args = parser.parse_args()

    if args.url and args.name:
        download_video(video_url=args.url, video_name=args.name)
    elif args.url:
        download_video(video_url=args.url, video_name=None)
    elif args.bulk:
        url_file = args.file if args.file else "data/urls.txt"
        url_name_map = []  # list of tuples of (url, name)
        with open(url_file, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue

                parts = line.split(",https")
                if len(parts) == 1:
                    url_name_map.append((parts[0], None))
                elif len(parts) == 2:
                    url_name_map.append(("https" + parts[1], parts[0]))
                else:
                    print(f"Invalid line: {line}")

        for url, name in url_name_map:
            print(f"Downloading {url} as {name}")
            name = name if name is not None else url.split("/")[-1].split("?")[0]
            download_video(video_url=url.strip(), video_name=name.strip())


if __name__ == "__main__":
    main()
