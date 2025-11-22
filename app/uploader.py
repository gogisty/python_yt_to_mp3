import os
import os.path
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Use full Drive scope (matches reference example) so listing/nested search works reliably
SCOPES = ["https://www.googleapis.com/auth/drive"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def get_credentials():
    """Load (and if necessary obtain/refresh) user credentials.
    Keeps previous public signature used by main.
    """
    creds: Optional[Credentials] = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            # Run local server OAuth flow
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return creds

def get_service():
    """Return an authenticated Drive v3 service instance."""
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)

def upload_mp3_to_drive(file_path: str, folder_id: str) -> Optional[str]:
    """Upload the local MP3 file to the specified Drive folder.
    Returns uploaded file id or None on failure.
    Signature preserved for main; internally we now share logic with example script.
    """
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return None
    service = get_service()
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="audio/mpeg", resumable=True)
    try:
        request = service.files().create(body=file_metadata, media_body=media, fields="id, name")
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                # Simple progress percentage
                print(f"Upload progress: {int(status.progress() * 100)}%")
        print(f"Uploaded file ID: {response.get('id')}")
        return response.get("id")
    except HttpError as e:
        print(f"Upload failed: {e}")
        return None

def list_root_folders() -> List[dict]:
    """List all folders directly under the user's root (My Drive)."""
    service = get_service()
    query = "'root' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    folders: List[dict] = []
    page_token = None
    while True:
        resp = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, parents)",
            pageSize=1000,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageToken=page_token,
        ).execute()
        folders.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    if not folders:
        print("No folders found in root.")
    else:
        print("Root folders:")
        for f in folders:
            print(f"{f['name']} ({f['id']})")
    return folders

def get_folder_id(service, folder_path: str) -> Optional[str]:
    """Resolve a nested folder path (e.g. 'Books/Audio') to its folder ID.
    Returns None if any component is missing.
    (Keeps original name for compatibility with main.)
    """
    if not folder_path:
        return None
    parent_id = 'root'
    parts = [p.strip() for p in folder_path.split('/') if p.strip()]
    for part in parts:
        # Escape single quotes in part for Drive query syntax
        escaped_part = part.replace("'", "\\'")
        query = (
            f"'{parent_id}' in parents and name='{escaped_part}' and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        try:
            resp = service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=10,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            ).execute()
        except HttpError as e:
            print(f"Error searching for '{part}': {e}")
            return None
        matches = resp.get("files", [])
        if not matches:
            print(f"Folder component not found: {part}")
            return None
        # If multiple, take first (could be improved with disambiguation)
        parent_id = matches[0]["id"]
    return parent_id

# Backwards-compatible helper to debug folder path resolution

def debug_resolve_folder_path(path: str):
    service = get_service()
    fid = get_folder_id(service, path)
    if fid:
        print(f"Resolved '{path}' -> {fid}")
    else:
        print(f"Failed to resolve '{path}'")
    return fid