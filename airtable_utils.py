import os
import requests
import mimetypes

def insert_to_airtable(record: dict):
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_name = os.getenv("AIRTABLE_TABLE_NAME")

    if not all([api_key, base_id, table_name]):
        raise RuntimeError("Airtable credentials are not fully set.")

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Drop empty strings / None to avoid select-option errors
    clean_record = {k: v for k, v in record.items() if v}
    payload = {"fields": clean_record}

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Airtable error {resp.status_code}: {resp.text}")
    print("[OK] Added row to Airtable.")