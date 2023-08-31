import os
from download_yt import download_youtube_video_as_mp3
from mp3_to_transcribe import transcribe_wisper

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download YouTube video as mp3")
    parser.add_argument("link", help="YouTube video link")
    args = parser.parse_args()

    audio_file = download_youtube_video_as_mp3(args.link)
    output_directory = os.path.dirname(audio_file)
    transctiption = transcribe_wisper(output_directory, audio_file)
    print(transctiption)