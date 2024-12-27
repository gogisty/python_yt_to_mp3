import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def upload_mp3_to_drive(file_path, folder_id):
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype="audio/mp3")
    
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    print(f"Uploaded file ID: {uploaded_file.get('id')}")

def get_folder_id(service, folder_name):
    """
    Searches Google Drive for a folder matching folder_name.
    Returns the folder ID if found, otherwise None.
    """
    query = (
        f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    response = service.files().list(
        q=query, 
        spaces="drive", 
        fields="files(id, name)"
    ).execute()
    
    files = response.get("files", [])
    if not files:
        return None  # No folders found matching the name
    
    # If multiple folders have the same name, return the first match
    return files[0]["id"]