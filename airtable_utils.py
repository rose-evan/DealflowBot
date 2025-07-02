"""airtable_utils.py
Utility for inserting records into Airtable via REST API.
"""

import os
import requests


def insert_to_airtable(record: dict):
    """Insert a single record (dict) into Airtable."""
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
    payload = {"fields": record}

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Airtable error {resp.status_code}: {resp.text}")
    print("[OK] Added row to Airtable.") 