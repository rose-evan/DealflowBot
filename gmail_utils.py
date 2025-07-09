import os
import base64
from io import BytesIO
from typing import List, Tuple
import tempfile
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes

# Gmail API scope (read & modify so we can mark messages as read)
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def authenticate_gmail():
    creds = None
    token_path = "token.json"  # OAuth token cache

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json"), SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_unread_messages(service, max_results: int = 10):
    """Return a list of unread Gmail message metadata (can be empty), only those with the 'automated' label."""
    # Use Gmail search query to require 'automated' label
    query = 'label:automated is:unread'
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    return results.get("messages", [])


def _walk_parts(parts, service, msg_id, body_texts: List[str], pdf_blobs: List[bytes]):
    """Recursively walk MIME parts collecting plain text and PDFs."""
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain":
            data = part["body"].get("data", "")
            decoded = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
            body_texts.append(decoded)
        elif mime_type == "application/pdf":
            att_id = part["body"].get("attachmentId")
            if att_id:
                att = (
                    service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=msg_id, id=att_id)
                    .execute()
                )
                pdf_data = base64.urlsafe_b64decode(att["data"] + "==")
                pdf_blobs.append(pdf_data)
        # Nested parts
        if "parts" in part:
            _walk_parts(part["parts"], service, msg_id, body_texts, pdf_blobs)


def extract_email_content(service, msg_id: str) -> Tuple[str, str, str, list, list]:
    """Extract sender, subject, combined text (body + PDFs), PDF images, and saved PDF file paths from a message."""
    msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()

    headers = msg["payload"].get("headers", [])
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")

    body_texts: List[str] = []
    pdf_blobs: List[bytes] = []
    _walk_parts([msg["payload"]], service, msg_id, body_texts, pdf_blobs)

    # Create decks directory if it doesn't exist
    decks_dir = "decks"
    if not os.path.exists(decks_dir):
        os.makedirs(decks_dir)

    # Save PDFs and track file paths
    pdf_file_paths = []
    pdf_texts: List[str] = []
    pdf_images: list = []
    
    for i, blob in enumerate(pdf_blobs):
        # Save PDF to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"deck_{timestamp}_{i+1}.pdf"
        file_path = os.path.join(decks_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(blob)
        pdf_file_paths.append(file_path)
        print(f"[INFO] Saved PDF deck: {file_path}")
        
        # Extract text from PDF
        reader = PdfReader(BytesIO(blob))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        pdf_texts.append(text)
    combined_text = f"Subject: {subject}\n\n" + "\n\n".join(body_texts + pdf_texts)
    return sender, subject, combined_text, pdf_images, pdf_file_paths 
