import os
import json
import google.generativeai as genai


def extract_fields_with_gemini(text: str) -> dict:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f'''
You are a data extraction assistant for venture capital dealflow.
Given the following unstructured text (which may include an email and/or a pitch deck), extract the following fields.
Return *only* valid JSON with exactly these keys and empty strings when a field is missing:
  Company
  Founder Name
  Email
  Website
  Personal Linkedin
  Blurb about Company
  Industry
  Where Are You Based
  Raise Amount
  Round -> options: Angle, PreSeed, Seed, Series A, Series B+
  Relevant Company Metrics/Traction
  Deck -> leave blank
  Deck Links -> leave blank
  Status -> leave blank
  Call Notes -> leave blank
  Last Modified -> generate a date and time in the format YYYY-MM-DD HH:MM:SS

Text:
"""{text}"""'''

    response = model.generate_content(prompt)
    content = response.text.strip()

    # Strip markdown fences if present (```json ... ```)
    if content.startswith("```"):
        # Remove all leading/trailing backticks and language hints
        content = content.strip("`\n ")

    # In case the model added prose around the JSON, locate the first '{' and last '}'
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start : end + 1]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("[WARN] Gemini response was not valid JSON – raw output saved to gemini_raw.txt")
        # Save raw for debugging
        with open("gemini_raw.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
        return {} 