import os
from download_yt import download_youtube_audio_as_mp3
from mp3_to_transcribe import transcribe_wisper
from uploader import get_credentials, get_folder_id, upload_mp3_to_drive
from googleapiclient.discovery import build

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download YouTube video as mp3")
    parser.add_argument("link", help="YouTube video link")
    parser.add_argument("--summary-format", choices=["txt", "json"], default=None, help="Format of the summary output")
    parser.add_argument("--upload-drive", action="store_true", help="Upload to Google Drive folder 'MyDrive/Books/Audio'")
    args = parser.parse_args()

    audio_file = download_youtube_audio_as_mp3(args.link)
    output_directory = os.path.dirname(audio_file)

    if args.summary_format:
        transcribe_wisper(output_directory, audio_file, args.summary_format)
        print(f"Transcription and summary saved in {output_directory}")
    else:
        print(f"MP3 file saved at {audio_file}")

    # 3. Optionally upload to drive folder "MyDrive/Books/Audio"
    if args.upload_drive:
        creds = get_credentials()
        service = build("drive", "v3", credentials=creds)
        folder_id = get_folder_id(service, "Audio")  # e.g. if "Books" is just an org unit in the path
        if folder_id is None:
            print("Drive folder not found. Check folder name.")
        else:
            upload_mp3_to_drive(audio_file, folder_id)       