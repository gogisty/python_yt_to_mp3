import os
import yt_dlp
from yt_dlp.utils import DownloadError


def _prepare_and_return_path(ydl, info_dict):
    file_path = ydl.prepare_filename(info_dict)
    # if postprocessor converted to mp3, return .mp3 path, else original
    mp3_path = os.path.splitext(file_path)[0] + ".mp3"
    if os.path.exists(mp3_path):
        return mp3_path
    return file_path


def download_youtube_audio_as_mp3(youtube_link):
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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_link])
            info_dict = ydl.extract_info(youtube_link, download=False)
            return _prepare_and_return_path(ydl, info_dict)
    except DownloadError as e:
        print("Primary download failed:\n", e)
        # Try to print available formats to help debugging
        try:
            with yt_dlp.YoutubeDL({'listformats': True, 'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_link, download=False)
                formats = info.get('formats', [])
                print(f"Available formats ({len(formats)}):")
                for f in formats:
                    print(f" - {f.get('format_id')} : {f.get('ext')} {f.get('acodec')} {f.get('vcodec')}")
        except Exception:
            pass

        # Retry with a very permissive config (no postprocessor) to at least download original audio
        fallback_opts = {
            'format': 'bestaudio',
            'outtmpl': os.path.join("outputs", "%(title)s/%(title)s.%(ext)s"),
            'n_threads': 4,
            'verbose': True
        }
        try:
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                ydl.download([youtube_link])
                info_dict = ydl.extract_info(youtube_link, download=False)
                return _prepare_and_return_path(ydl, info_dict)
        except Exception as e2:
            print("Fallback download also failed:\n", e2)
            raise