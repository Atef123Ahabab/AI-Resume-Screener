import os
import re
import base64
import mimetypes
import docx
import pypdf
import pymupdf as fitz

def get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    return mime if mime in ("image/jpeg", "image/png") else "image/jpeg"

def image_part(image_b64, mime_type="image/jpeg"):
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}
    }

def process_resume(path, extension):
    if extension in ("jpeg", "jpg", "png"):
        with open(path, "rb") as file:
            encoded_image = base64.b64encode(file.read()).decode("utf-8")
        return None, encoded_image, get_mime_type(path)

    if extension == "pdf":
        text = ""
        try:
            reader = pypdf.PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            text = ""

        if len(text.strip()) >= 50:
            return text, None, None

        try:
            pdf = fitz.open(path)
            if len(pdf) == 0:
                pdf.close()
                return "", None, None
            page = pdf.load_page(0)
            pixmap = page.get_pixmap(dpi=180, alpha=False)
            image_bytes = pixmap.tobytes("jpeg")
            pdf.close()
            encoded_image = base64.b64encode(image_bytes).decode("utf-8")
            return None, encoded_image, "image/jpeg"
        except Exception as exc:
            return f"Error converting PDF to image: {exc}", None, None

    if extension == "docx":
        try:
            document = docx.Document(path)
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
            return text, None, None
        except Exception as exc:
            return f"Error reading DOCX: {exc}", None, None

    if extension == "txt":
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as file:
                return file.read(), None, None
        except Exception as exc:
            return f"Error reading TXT: {exc}", None, None

    return "", None, None

def parse_result(raw):
    raw = (raw or "").strip()
    score_match = re.search(r"\bSCORE\s*:\s*(\d{1,3})", raw, re.I)
    reason_match = re.search(r"\bREASON\s*:\s*(.*)", raw, re.I | re.S)

    score = int(score_match.group(1)) if score_match else 0
    score = max(0, min(score, 100))
    reason = reason_match.group(1).strip() if reason_match else "No reasoning returned."
    reason = re.sub(r"\s+", " ", reason)
    return score, reason[:1000]