import unittest
import os
import sys
# Add project root to path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.download_yt import download_youtube_audio_as_mp3
from app.uploader import upload_mp3_to_drive, get_service, get_folder_id

class TestEndToEnd(unittest.TestCase):
    """End-to-end test for YouTube download and Google Drive upload workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.downloaded_files = []
        self.drive_files = []
        self.service = get_service()

    def tearDown(self):
        """Tear down test fixtures, cleaning up local and remote files."""
        # Cleanup Drive files
        for file_id in self.drive_files:
            try:
                print(f"Cleaning up Drive file: {file_id}")
                self.service.files().delete(fileId=file_id).execute()
            except Exception as e:
                print(f"Error deleting Drive file {file_id}: {e}")

        # Cleanup local files
        for file_path in self.downloaded_files:
            if os.path.exists(file_path):
                print(f"Cleaning up local file: {file_path}")
                try:
                    os.remove(file_path)
                    # Try to remove parent dir if empty
                    parent_dir = os.path.dirname(file_path)
                    if not os.listdir(parent_dir):
                        os.rmdir(parent_dir)
                except OSError:
                    pass

    def test_download_and_upload_flow(self):
        """Test the complete flow: Download -> Upload -> Verify."""
        print("\nStarting End-to-End Test...")

        # 1. Download short video
        # "Me at the zoo" - short video
        video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        print(f"1. Downloading video: {video_url}")
        
        mp3_path = download_youtube_audio_as_mp3(video_url)
        
        # Assertions for download
        self.assertIsNotNone(mp3_path, "Download function returned None")
        self.assertTrue(os.path.exists(mp3_path), f"Downloaded file not found at {mp3_path}")
        
        # Register for cleanup
        self.downloaded_files.append(mp3_path)
        print(f"   Download successful: {mp3_path}")

        # 2. Upload to Drive
        target_folder = "Books/Audio"
        print(f"2. Uploading to Drive folder: {target_folder}")
        
        # Resolve folder ID
        folder_id = get_folder_id(self.service, target_folder)
        self.assertIsNotNone(folder_id, 
            f"Could not resolve folder '{target_folder}'. "
            "Ensure the folder exists and the app has 'drive' scope permissions."
        )

        # Upload
        file_id = upload_mp3_to_drive(mp3_path, folder_id)
        
        # Assertions for upload
        self.assertIsNotNone(file_id, "Upload function returned None")
        
        # Register for cleanup
        self.drive_files.append(file_id)
        print(f"   Upload successful. File ID: {file_id}")

        # 3. Verify upload (check existence)
        print("3. Verifying upload...")
        try:
            file_meta = self.service.files().get(fileId=file_id).execute()
            self.assertEqual(file_meta.get('name'), os.path.basename(mp3_path), f"Uploaded file name mismatch: expected '{os.path.basename(mp3_path)}', got '{file_meta.get('name')}'")
            print(f"   Verification successful: Found file '{file_meta.get('name')}' (ID: {file_meta.get('id')})")
        except Exception as e:
            self.fail(f"Verification failed: {e}")

if __name__ == "__main__":
    unittest.main()
