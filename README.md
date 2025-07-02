# Dealflow Automation

A minimal, no-frills Python utility that pulls unread startup pitches from Gmail, extracts key data via Google Gemini (gemini-2.5-flash), and stores the structured information in Airtable for easy tracking.

---

## Features

1. **Gmail → Text**
   • Authenticates with Gmail (OAuth) and fetches unread emails.
   • Parses the plain-text email body and any attached PDF pitch decks.

2. **Gemini → JSON**
   • Sends the combined text to Gemini and requests a concise JSON payload containing 🡒  company name, founder info, raise details, deck link, etc.

3. **Airtable → CRM**
   • Pushes the extracted fields straight into your Airtable base/table.

All logic is split across small, clear modules:

| File | Responsibility |
|------|----------------|
| `gmail_utils.py` | Gmail authentication & content extraction |
| `gemini_utils.py` | Gemini prompt & JSON post-processing |
| `airtable_utils.py` | Airtable REST insertion |
| `dealflow_entry.py` | Orchestrates the pipeline (entry-point) |

---

## Quick Start

1. **Clone & enter the project**
   ```bash
   git clone <repo-url> && cd DealflowBot
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**  – create a `.env` file in the repo root:
   ```env
   # Google OAuth client file (download from Google Cloud Console → OAuth consent)
   GMAIL_CREDENTIALS_FILE=credentials.json

   # Gemini
   GEMINI_API_KEY=your_gemini_api_key

   # Airtable
   AIRTABLE_API_KEY=patXXXXXXXXXXXXXX
   AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
   AIRTABLE_TABLE_NAME=Companies
   ```

   *Place `credentials.json` (the OAuth2 client secrets) in the same directory or point to an absolute path.*

5. **Run the pipeline**
   ```bash
   python dealflow_entry.py
   ```

If unread emails (with or without PDF decks) exist, the script will:
1. Parse them
2. Ask Gemini for structured data
3. Write rows to Airtable
4. Mark those emails as read

---

## Notes & Troubleshooting

• **First-time Gmail auth** – A browser window will open for OAuth consent and store the tokens in `token.json` for subsequent runs.

• **Gemini billing/quotas** – Ensure your Gemini API key has access to the `gemini-2.5-flash` model.

• **Airtable schema** – The table must contain fields matching the keys returned by Gemini (e.g., *Company Name*, *Founder Email*, etc.). Missing fields generate errors.

• **Extending** – The modules are intentionally tiny; feel free to adapt prompts, handle HTML emails, more file types, etc.

---

## License

MIT