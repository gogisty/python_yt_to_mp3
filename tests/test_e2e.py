import os
import sys
import shutil

# Add project root to path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.download_yt import download_youtube_audio_as_mp3
from app.uploader import upload_mp3_to_drive, get_service, get_folder_id

def test_e2e_flow():
    """End-to-end test for YouTube download and Google Drive upload workflow.

    Tests the complete flow:
    1. Downloads a short YouTube video as MP3
    2. Uploads the MP3 to Google Drive folder 'Books/Audio'
    3. Verifies the upload succeeded
    4. Cleans up both Drive and local files

    Prerequisites:
    - Valid Google Drive credentials (credentials.json)
    - Network access to YouTube and Google Drive APIs
    - FFmpeg installed for audio conversion
    """
    print("Starting End-to-End Test...")
    
    # 1. Download short video
    # "Me at the zoo" is short (19s), but maybe "1 second video" is better.
    # https://www.youtube.com/watch?v=BaW_jenozKc (1 second video)
    video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    print(f"1. Downloading video: {video_url}")
    
    try:
        mp3_path = download_youtube_audio_as_mp3(video_url)
        if not mp3_path or not os.path.exists(mp3_path):
            print("ERROR: Download failed or file not found.")
            return
        print(f"   Download successful: {mp3_path}")
    except Exception as e:
        print(f"ERROR: Download exception: {e}")
        return

    # 2. Upload to Drive
    # Using the folder path the user mentioned to verify the issue
    target_folder = "Books/Audio" 
    print(f"2. Uploading to Drive folder: {target_folder}")
    
    service = get_service()
    
    # Resolve folder ID first to check if it exists (and reproduce error if any)
    folder_id = get_folder_id(service, target_folder)
    if not folder_id:
        print(f"ERROR: Could not resolve folder '{target_folder}'. This confirms the 'Folder component not found' issue.")
        # Clean up local file even if upload fails
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
            # Also remove the directory created by download_yt if empty
            parent_dir = os.path.dirname(mp3_path)
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)
            print("   Local cleanup done.")
        return

    file_id = upload_mp3_to_drive(mp3_path, folder_id)
    
    if file_id:
        print(f"   Upload successful. File ID: {file_id}")
        
        # 3. Verify upload (check existence)
        print("3. Verifying upload...")
        try:
            file_meta = service.files().get(fileId=file_id).execute()
            print(f"   Verification successful: Found file '{file_meta.get('name')}' (ID: {file_meta.get('id')})")
            
            # 4. Cleanup Drive
            print("4. Cleaning up Drive file...")
            service.files().delete(fileId=file_id).execute()
            print("   Drive file deleted.")
            
        except Exception as e:
            print(f"ERROR: Verification/Cleanup failed: {e}")
    else:
        print("ERROR: Upload returned no File ID.")

    # 5. Cleanup Local
    print("5. Cleaning up local file...")
    if os.path.exists(mp3_path):
        os.remove(mp3_path)
        print(f"   Deleted local file: {mp3_path}")
        # Try to remove the folder if empty (download_yt creates a folder based on title)
        parent_dir = os.path.dirname(mp3_path)
        try:
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)
                print(f"   Deleted empty directory: {parent_dir}")
        except OSError:
            # It's okay if the directory cannot be removed (e.g., not empty or already deleted).
            pass
    else:
        print("   Local file not found (already deleted?)")

    print("End-to-End Test Complete.")

if __name__ == "__main__":
    test_e2e_flow()
