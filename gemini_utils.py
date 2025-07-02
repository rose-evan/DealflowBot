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
  Company Name
  Founder Name
  Founder Email
  Company Website
  Founder\'s LinkedIn
  Company Summary
  Industry
  HQ Location
  Raise Amount
  Round Type
  Metrics / Traction
  Pitch Deck Link

Text:
"""{text}"""'''

    response = model.generate_content(prompt)
    content = response.text.strip()
    if content.startswith("```"):
        content = content.strip("`\n ")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("[WARN] Gemini response was not valid JSON.")
        return {} 