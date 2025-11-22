# Python YouTube to MP3 Converter & Transcriber

A powerful command-line tool that downloads YouTube videos as high-quality MP3 audio files, automatically transcribes and summarizes the content using AI, and uploads the result to your Google Drive.

## Features

- **High-Quality Audio Download**: Downloads YouTube videos and converts them to MP3 format (192kbps) using `yt-dlp` and `ffmpeg`.
- **AI Transcription**: Uses OpenAI's **Whisper** model to transcribe audio to text with high accuracy.
- **Smart Summarization**: Summarizes the transcribed text using Hugging Face **Transformers**.
- **Cloud Backup**: Automatically uploads the MP3 file to a specified folder in your **Google Drive**.
- **Flexible Output**: Save summaries in `txt` or `json` format.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**
2.  **FFmpeg**: Required for audio conversion.
    *   **Windows**: [Download FFmpeg](https://ffmpeg.org/download.html), extract it, and add the `bin` folder to your system PATH.
    *   **Mac**: `brew install ffmpeg`
    *   **Linux**: `sudo apt install ffmpeg`
3.  **Google Cloud Credentials**:
    *   Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
    *   Enable the **Google Drive API**.
    *   Create OAuth 2.0 Client IDs (Desktop App).
    *   Download the JSON file, rename it to `credentials.json`, and place it in the project root directory.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd python_yt_to_mp3
    ```

2.  Install the required Python packages:
    ```bash
    pip install yt-dlp openai-whisper transformers google-auth google-auth-oauthlib google-api-python-client torch
    ```
    *(Note: `torch` is required for Whisper and Transformers. Please refer to [PyTorch's website](https://pytorch.org/get-started/locally/) for the specific installation command for your system if the default pip install doesn't work.)*

## Usage

Run the script from the command line:

```bash
python main.py <YOUTUBE_LINK> [OPTIONS]
```

### Arguments

- `link`: The URL of the YouTube video (Required).
- `--summary-format`: Format of the summary output. Options: `txt`, `json`.
- `--upload-drive`: Flag to enable uploading the MP3 to Google Drive.
- `--drive-folder`: Target Google Drive folder path. Default is `'Books/Audio'`.

### Examples

**1. Basic Download (MP3 only):**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**2. Download, Transcribe, and Summarize:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --summary-format txt
```

**3. Download and Upload to Google Drive:**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --upload-drive
```

**4. Full Pipeline (Download, Transcribe, Summarize, and Upload to Custom Folder):**
```bash
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --summary-format json --upload-drive --drive-folder "MyPodcasts/Tech"
```

## Project Structure

- `main.py`: Entry point of the application. Handles argument parsing and workflow orchestration.
- `app/download_yt.py`: Handles YouTube video downloading and MP3 conversion.
- `app/mp3_to_transcribe.py`: Contains logic for Whisper transcription and text summarization.
- `app/uploader.py`: Manages Google Drive authentication and file uploads.
- `outputs/`: Directory where downloaded files and transcriptions are saved (created automatically).

## Troubleshooting

- **FFmpeg not found**: Ensure FFmpeg is installed and added to your system's PATH environment variable.
- **Google Drive Upload Fails**: Check if `credentials.json` is present and valid. If it's your first time running, a browser window will open to authorize the app.
- **Download Errors**: `yt-dlp` is regularly updated to match YouTube's changes. Try updating it: `pip install --upgrade yt-dlp`.
