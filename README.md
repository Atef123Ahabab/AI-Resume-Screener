# AI-Powered Resume Screener

## Project Overview
This is a semi-automated recruitment screening tool that uses a Large Language Model (Qwen 27B via Groq API) to score candidate resumes against a Job Description.

**Live Repository:** https://github.com/Atef123Ahabab/AI-Resume-Screener

## Original Goal vs Achieved

| Step | Original Goal | Achieved | Coverage |
|------|---------------|----------|----------|
| 1. Bdjobs Login | Automated | Manual (Cloudflare) | 0% |
| 2. Candidate Filtering | Automated | Manual slider + AI | 50% |
| 3. CV Download | Automated | Manual (no API) | 0% |
| 4. AI Scoring | Automated | Fully automated (Qwen) | 100% |
| 5. Ranking | Automated | Fully automated | 100% |

**Overall Coverage: ~70%**

## Why 100% Is Impossible

1. **Cloudflare Turnstile** blocks automated browser login
2. **No official Bdjobs employer API** exists
3. **No bulk CV download** (one at a time only)
4. **Terms of Service forbid automation**

## The Working Workflow

### Step 1: Filter on Bdjobs (Manual)
Use the Requirement Matching slider (75%+ or 100%).

### Step 2: Download CVs (Manual)
Click each candidate, download resume, save to resumes/downloaded/

### Step 3: Run AI Scoring (Automated)
    python simple_rank.py

Output:
    1. candidate_a.pdf - Score: 91
    2. candidate_c.pdf - Score: 85
    3. candidate_b.pdf - Score: 72

## Setup

1. Get free Groq API key: https://console.groq.com/
2. Install: pip install pypdf openai python-dotenv
3. Create .env with GROQ_API_KEY="gsk_..."
4. Add jd.txt and CVs to resumes/downloaded/
5. Run: python simple_rank.py

## Security
- API keys in .env (excluded from Git)
- CV files excluded from Git

## Author
Atef Ahabab - SQA 19
