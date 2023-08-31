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
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_link])

    info_dict = ydl.extract_info(youtube_link, download=False)
    file_path = ydl.prepare_filename(info_dict)
    mp3_file_path = os.path.splitext(file_path)[0] + ".mp3"
    return mp3_file_path  