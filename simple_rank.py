import os
import pypdf
import re
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# 1. Load API Key
# ==========================================
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("❌ ERROR: Could not find GROQ_API_KEY in .env file.")
    exit()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

# ==========================================
# 2. Read Job Description
# ==========================================
with open("jd.txt", "r", encoding="utf-8") as f:
    jd_text = f.read()

RESUME_DIR = "resumes/downloaded"
results = []

print("=" * 60)
print("🚀 Starting Batch AI Resume Analysis...")
print("=" * 60)

if not os.path.exists(RESUME_DIR):
    print(f"❌ Folder {RESUME_DIR} does not exist.")
    exit()

# ==========================================
# 3. Loop Through All Resumes
# ==========================================
for filename in os.listdir(RESUME_DIR):
    if not filename.lower().endswith(".pdf"):
        continue
    
    filepath = os.path.join(RESUME_DIR, filename)
    print(f"\nAnalyzing: {filename}...")
    
    try:
        with open(filepath, "rb") as f:
            reader = pypdf.PdfReader(f)
            resume_text = ""
            for page in reader.pages:
                resume_text += page.extract_text()
    except Exception as e:
        print(f"  ❌ Failed to read PDF: {e}")
        continue

    # Keep only first 1500 chars to avoid token limits
    resume_snippet = resume_text[:1500]

    # ==========================================
    # 4. AI Scoring Prompt
    # ==========================================
    prompt = f"""
    Here is a Job Description:
    {jd_text}

    Here is a candidate's Resume:
    {resume_snippet}

    Based on the match between the resume and the job description, what is the match score from 0 to 100? 
    Please reply with only the number.
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=20
        )
        raw = response.choices[0].message.content.strip()
        print(f"  🔍 Raw AI response: '{raw}'")
        
        numbers = re.findall(r'\d+', raw)
        score = int(numbers[0]) if numbers else 0
        if score > 100:
            score = 100
            
        results.append((filename, score))
        print(f"  ✅ Score: {score}")
    except Exception as e:
        print(f"  ❌ AI call failed: {e}")
        results.append((filename, 0))

# ==========================================
# 5. Sort and Display Rankings
# ==========================================
results.sort(key=lambda x: x[1], reverse=True)

print("\n" + "=" * 60)
print("🏆 FINAL CANDIDATE RANKING (by AI Score)")
print("=" * 60)
for i, (name, score) in enumerate(results, 1):
    print(f"{i}. {name} — Score: {score}")
print("=" * 60)
