import os
import yt_dlp
from yt_dlp.utils import DownloadError
import shutil

def _check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("WARNING: 'ffmpeg' not found in PATH. MP3 conversion will likely fail.")
        return False
    return True

def _prepare_and_return_path(ydl, info_dict):
    file_path = ydl.prepare_filename(info_dict)
    # if postprocessor converted to mp3, return .mp3 path, else original
    mp3_path = os.path.splitext(file_path)[0] + ".mp3"
    if os.path.exists(mp3_path):
        return mp3_path
    return file_path

def _download_with_options(link, options):
    """Helper method to download video with specific options."""
    with yt_dlp.YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(link, download=True)
        return _prepare_and_return_path(ydl, info_dict)

def download_youtube_audio_as_mp3(youtube_link):
    _check_ffmpeg()

    # Preferred options: download best audio and convert to mp3
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join("outputs", "%(title)s/%(title)s.%(ext)s"),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
        ],
        'n_threads': 4,
        'verbose': True
    }

    try:
        return _download_with_options(youtube_link, ydl_opts)
    except DownloadError as e:
        print("\n" + "="*60)
        print("PRIMARY DOWNLOAD FAILED (MP3 Conversion)")
        print(f"Error details: {e}")
        print("="*60 + "\n")
        
        # Try to print available formats to help debugging
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_link, download=False)
                formats = info.get('formats', [])
                print(f"Available formats ({len(formats)}):")
                for f in formats:
                    print(f" - {f.get('format_id')} : {f.get('ext')} {f.get('acodec')} {f.get('vcodec')}")
        except Exception as ex:
            print("Failed to print available formats for debugging:", ex) 

        print("\nAttempting fallback download (Original Format)...")
        print("WARNING: The file will NOT be converted to MP3.")
        
        # Retry with a very permissive config (no postprocessor) to at least download original audio
        fallback_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join("outputs", "%(title)s/%(title)s.%(ext)s"),
            'n_threads': 4,
            'verbose': True
        }
        try:
            return _download_with_options(youtube_link, fallback_opts)
        except Exception as e2:
            print("Fallback download also failed:\n", e2)
            raise