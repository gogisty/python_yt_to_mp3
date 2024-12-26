import os
from download_yt import download_youtube_video_as_mp3
from mp3_to_transcribe import transcribe_wisper

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download YouTube video as mp3")
    parser.add_argument("link", help="YouTube video link")
    parser.add_argument("--summary-format", choices=["txt", "json"], default=None, help="Format of the summary output")
    args = parser.parse_args()

    audio_file = download_youtube_video_as_mp3(args.link)
    output_directory = os.path.dirname(audio_file)

    if args.summary_format:
        transcribe_wisper(output_directory, audio_file, args.summary_format)
        print(f"Transcription and summary saved in {output_directory}")
    else:
        print(f"MP3 file saved at {audio_file}")