from dotenv import load_dotenv
from datetime import datetime
import pytz

from gmail_utils import authenticate_gmail, get_unread_messages, extract_email_content
from gemini_utils import extract_fields_with_gemini
from airtable_utils import insert_to_airtable


def main():
    # Load environment variables from .env
    load_dotenv()

    service = authenticate_gmail()
    messages = get_unread_messages(service)

    if not messages:
        print("No unread emails found.")
        return

    for msg_meta in messages:
        msg_id = msg_meta["id"]
        try:
            sender, subject, text, pdf_images, pdf_file_paths = extract_email_content(service, msg_id)
            print(f"Processing: {subject} ({sender})")

            structured = extract_fields_with_gemini(text, pdf_images)
            if structured:
                # Add current date/time in PST
                pst = pytz.timezone('US/Pacific')
                current_time = datetime.now(pst).strftime("%Y-%m-%d %H:%M:%S")
                structured["Last Modified"] = current_time
                
                # Insert record without PDF attachments
                insert_to_airtable(structured)
            else:
                print("[WARN] Skipping insert — no structured data returned.")
        except Exception as exc:
            print(f"[ERROR] Failed to process message {msg_id}: {exc}")
            continue
        finally:
            # Mark email as read regardless of success to avoid loops
            service.users().messages().modify(
                userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
            ).execute()


if __name__ == "__main__":
    main() 