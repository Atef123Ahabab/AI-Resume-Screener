import os
import pypdf
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load the .env file
load_dotenv()

# 2. Get the key
API_KEY = os.getenv("GROQ_API_KEY")

# Safety Check: If the key is missing, stop and tell the user
if not API_KEY:
    print("❌ ERROR: Could not find GROQ_API_KEY. Check if your .env file exists and has the key inside.")
    exit()

# 3. Initialize the client
client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

# ==========================================
# 4. Read the Job Description (JD)
# ==========================================
print("Reading Job Description...")
try:
    with open("jd.txt", "r", encoding="utf-8") as f:
        jd_text = f.read()
except Exception as e:
    print(f"Failed to read JD. Error: {e}")
    exit()

# ==========================================
# 5. Read the Resume PDF
# ==========================================
print("Reading Resume PDF...")
resume_text = ""
try:
    with open("resumes/Atef_Ahabab_CV with picture.pdf", "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            resume_text += page.extract_text()
except Exception as e:
    print(f"Failed to read PDF. Please check the file path. Error: {e}")
    exit()

# ==========================================
# 6. Construct the Prompt
# ==========================================
prompt = f"""
You are a professional recruiter. Please evaluate and score the candidate's resume based on the following Job Description (JD).

[Job Description]:
{jd_text}

[Candidate Resume]:
{resume_text}

Please output the following:
1. Match Score (0-100)
2. Candidate Strengths
3. Candidate Weaknesses / Mismatches
4. Overall Recommendation (Whether to invite for an interview)
"""

# ==========================================
# 7. Call Groq API for Scoring
# ==========================================
print("Calling Groq AI for scoring, please wait...\n")
try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a professional HR recruitment assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    print("========== AI SCORING RESULTS ==========")
    print(response.choices[0].message.content)
    print("========================================")

except Exception as e:
    print(f"\nAPI Call Failed. Error message: {e}")