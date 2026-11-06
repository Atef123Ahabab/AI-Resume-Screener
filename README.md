# AI-Powered Resume Screener

## Project Overview
A semi-automated recruitment screening tool that uses a Large Language Model (Qwen 27B via Groq API) to score candidate resumes against **multiple** Job Descriptions and rank candidates **separately per role**.

**Live Repository:** https://github.com/Atef123Ahabab/AI-Resume-Screener

## What It Does Today

- Reads **all** JDs from `job_descriptions/` (`.txt`, `.pdf`, `.docx`, `.jpg`, `.jpeg`, `.png`)
- Auto-extracts each JD's title using the AI model (works even on image JDs)
- Reads **all** CVs from `resumes/downloaded/` (same formats, plus image PDFs via OCR fallback)
- Scores every CV against every JD (0-100) with a one-sentence justification
- Displays **one ranking table per JD**, sorted by score, with green/yellow/red badges (>=70 / >=50 / <50)
- Handles rate limits safely (sleep=6 between API calls)

## Original Goal vs Achieved

| Step | Original Goal | Achieved | Coverage |
|------|---------------|----------|----------|
| 1. Bdjobs Login | Automated | Manual (Cloudflare) | 0% |
| 2. Candidate Filtering | Automated | Manual slider + AI | 50% |
| 3. CV Download | Automated | Manual (no API) | 0% |
| 4. AI Scoring | Automated | Fully automated (Qwen) | 100% |
| 5. Multi-JD Ranking | - | Fully automated, per-JD tables | 100% |

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
Click each candidate, download resume, save to `resumes/downloaded/`.

### Step 3: Add Job Descriptions
Drop `.txt`, `.pdf`, `.docx`, or image files into `job_descriptions/`.

### Step 4: Run the App (Automated)

    ./run.sh

Then open http://localhost:8501, click **Run AI Screening**, and view separate rankings per JD.

## Setup

    git clone https://github.com/Atef123Ahabab/AI-Resume-Screener.git
    cd AI-Resume-Screener
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    echo 'GROQ_API_KEY="gsk_..."' > .env
    mkdir -p job_descriptions resumes/downloaded
    ./run.sh

Get a free Groq API key: https://console.groq.com/

## Tech Stack

- Python 3.13, Streamlit
- openai SDK (Groq's OpenAI-compatible endpoint)
- pypdf + pymupdf (PDFs), python-docx (DOCX)
- python-dotenv (secrets)

## Testing

This project includes an automated QA test suite using pytest and pytest-playwright.

### Run API Tests (fast, no browser)

    source .venv/bin/activate
    python -m pytest tests/api -v

Verifies:
- Missing API key handling (negative auth)
- Perfect match CV scores >= 80
- Non-matching CV scores <= 30

### Run UI Test (requires app running)

Terminal 1:

    ./run.sh

Terminal 2:

    source .venv/bin/activate
    python -m pytest tests/ui -v

Verifies:
- App loads at localhost:8501
- "AI Resume Screener" heading visible

### Run All Tests + HTML Report

    pip install pytest-html
    python -m pytest tests/ -v --html=report.html --self-contained-html
    open report.html

Result: 4 passed (3 API + 1 UI).

## Security

- API keys live in `.env` (excluded from Git)
- CV files in `resumes/` excluded from Git
- No secrets committed to history

## Author
Atef Ahabab - SQA 19
