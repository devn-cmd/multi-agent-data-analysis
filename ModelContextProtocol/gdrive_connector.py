import os
import io
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            os.getenv("GDRIVE_CREDENTIALS_PATH"), SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def fetch_csv_from_drive(file_name: str) -> pd.DataFrame:
    """Fetch a CSV file by name from the configured Drive folder."""
    service = get_drive_service()
    folder_id = os.getenv("GDRIVE_FOLDER_ID")

    # Search for the file in the folder
    query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        raise FileNotFoundError(f"'{file_name}' not found in Drive folder")

    file_id = files[0]["id"]

    # Download the file content
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    buffer.seek(0)
    df = pd.read_csv(buffer)
    print(f"Fetched '{file_name}' from Drive — {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def save_report_to_drive(report: str, report_name: str) -> str:
    """Save the final report as a text file back to Drive."""
    from googleapiclient.http import MediaInMemoryUpload
    service = get_drive_service()
    folder_id = os.getenv("GDRIVE_FOLDER_ID")

    media = MediaInMemoryUpload(report.encode("utf-8"), mimetype="text/plain")
    file_metadata = {"name": report_name, "parents": [folder_id]}
    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()

    file_url = f"https://drive.google.com/file/d/{uploaded['id']}/view"
    print(f"Report saved to Drive: {file_url}")
    return file_url
