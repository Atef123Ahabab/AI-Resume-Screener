import os
import base64
import mimetypes
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

def get_mime_type(path):
    mime, _ = mimetypes.guess_type(path)
    return mime if mime in ("image/jpeg", "image/png") else "image/jpeg"

def read_title_from_text(text):
    try:
        r = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": f"What is the exact Job Title in this text? Reply ONLY with the job title. Text: {text[:1000]}"}],
            temperature=0,
            max_tokens=20
        )
        title = r.choices[0].message.content.strip().replace('"', '')
        return title if title else None
    except:
        return None

def read_title_from_image(image_b64, mime_type):
    try:
        r = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "What is the exact Job Title in this image? Reply ONLY with the job title (e.g., 'Software Engineer'). Do not include any other words."},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}}
            ]}],
            temperature=0,
            max_tokens=20
        )
        title = r.choices[0].message.content.strip().replace('"', '')
        return title if title else None
    except:
        return None

def get_jd_title(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        title = read_title_from_text(text)
        if title: return title
        return os.path.splitext(os.path.basename(path))[0].title()
    else:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        mime = get_mime_type(path)
        title = read_title_from_image(b64, mime)
        if title: return title
        return os.path.splitext(os.path.basename(path))[0].title()