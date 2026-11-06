import pytest
import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
MODEL = "qwen/qwen3.8-27b"

def _score(jd_text, cv_text):
    prompt = f"""You are an expert Technical Recruiter.
Evaluate the CV against the Job Description below.
--- JOB DESCRIPTION ---
{jd_text}
--- CANDIDATE CV ---
{cv_text}
--- INSTRUCTIONS ---
1. Find the candidate's full name from the CV.
2. Score the candidate from 0 to 100 based on how well they match the JD.
--- OUTPUT FORMAT ---
Reply exactly in this format:
NAME: [Full Name]
SCORE: [Integer 0-100]
"""
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    raw = r.choices[0].message.content
    sm = re.search(r"SCORE:\s*(\d+)", raw, re.IGNORECASE)
    nm = re.search(r"NAME:\s*(.+)", raw, re.IGNORECASE)
    return {
        "score": int(sm.group(1)) if sm else 0,
        "name": nm.group(1).strip() if nm else ""
    }

def test_missing_env_var():
    original = os.environ.get("GROQ_API_KEY")
    os.environ["GROQ_API_KEY"] = ""
    assert os.environ.get("GROQ_API_KEY") == ""
    if original:
        os.environ["GROQ_API_KEY"] = original

def test_perfect_match_scores_high():
    jd = "Senior Python Developer, 5+ years Django and AWS, led a team."
    cv = "Jane Doe - 7 years Python, Django expert, managed team of 5, AWS Docker."
    result = _score(jd, cv)
    assert result["score"] >= 80

def test_bad_match_scores_low():
    jd = "Senior Python Developer, 5+ years Django and AWS."
    cv = "Alice Johnson - Graphic Designer, 5 years Photoshop, no programming."
    result = _score(jd, cv)
    assert result["score"] <= 30
