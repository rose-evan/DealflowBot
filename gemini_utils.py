import os
import json
import google.generativeai as genai


def extract_fields_with_gemini(text: str, images: list = None) -> dict:
    """
    Extract fields from text and optional images using Gemini.
    images: list of PIL.Image.Image objects (from pdf2image)
    """
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = (
        "You are a data extraction assistant for venture capital dealflow.\n"
        "Given the following unstructured text (which may include an email and/or a pitch deck), extract the following fields.\n"
        "Return *only* valid JSON with exactly these keys and empty strings when a field is missing:\n"
        "  Company\n"
        "  Founder Name\n"
        "  Email\n"
        "  Website\n"
        "  Personal Linkedin -> occasionaly founders attach their linkedin profile in the email\n"
        "  Blurb about Company\n"
        "  Industry\n"
        "  Where Are You Based\n"
        "  Raise Amount\n"
        "  Round -> options: Angle, PreSeed, Seed, Series A, Series B+\n"
        "  Relevant Company Metrics/Traction\n"
        "  Deck -> leave blank (PDF files will be added separately)\n"
        "  Deck Links -> leave blank\n"
        "  Status -> leave blank\n"
        "  Call Notes -> leave blank\n"
        "  Last Modified -> leave blank (will be set automatically)\n\n"
        "Text and images follow."
    )

    # Compose multimodal input
    contents = [
        {"role": "user", "parts": [
            {"text": prompt},
            {"text": text}
        ]}
    ]
    # If images are provided, add them as parts
    if images:
        for img in images:
            # Convert PIL Image to bytes (JPEG)
            from io import BytesIO
            buf = BytesIO()
            img.save(buf, format="JPEG")
            img_bytes = buf.getvalue()
            contents[0]["parts"].append({"inline_data": {"mime_type": "image/jpeg", "data": img_bytes}})

    # The google.generativeai API expects a list of parts (text, images, etc.)
    # See: https://ai.google.dev/gemini-api/docs/send-multimodal-content
    try:
        response = model.generate_content(contents[0]["parts"])
    except Exception as e:
        print(f"[ERROR] Gemini API call failed: {e}")
        return {}

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