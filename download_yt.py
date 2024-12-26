import os
import yt_dlp

def download_youtube_video_as_mp3(youtube_link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join("outputs", "%(title)s/%(title)s.%(ext)s"),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio',
             'preferredcodec': 'mp3',
             'preferredquality': '192'},
        ],
        'n_threads': 4,  # Increase the number of concurrent connections
        'external_downloader': 'aria2c',  # Use aria2c as an external downloader if installed
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])

    info_dict = ydl.extract_info(youtube_link, download=False)
    file_path = ydl.prepare_filename(info_dict)
    webm_file_path = file_path
    mp3_file_path = os.path.splitext(file_path)[0] + ".mp3"

    # Remove the original .webm file after conversion
    if os.path.exists(webm_file_path):
        os.remove(webm_file_path)

    return mp3_file_path