# AI-Powered Resume Screener (SQA Automation Project)

## 📌 Overview
An automated candidate screening tool that reads a Job Description (JD) and a candidate's Resume (PDF), then uses a Large Language Model via the **Groq API** to score the candidate and provide HR feedback.

## 🚀 Features
- **PDF Parsing:** Extracts text from resume PDFs using `pypdf`.
- **AI Evaluation:** Uses Groq API (Llama 3) for fast, free resume scoring.
- **Detailed Output:** Match Score (0-100), Strengths, Weaknesses, and Interview Recommendation.
- **Secure Design:** Uses `python-dotenv` to protect API keys with `.gitignore`.

## 🛠️ Tech Stack
- Python 3.x
- Groq API
- pypdf, openai, python-dotenv

## ⚙️ Setup
1. Clone the repo:
   \`\`\`bash
   git clone https://github.com/Atef123Ahabab/AI-Resume-Screener.git
   cd AI-Resume-Screener
   \`\`\`
2. Create virtual environment:
   \`\`\`bash
   python3 -m venv .venv
   source .venv/bin/activate
   \`\`\`
3. Install dependencies:
   \`\`\`bash
   pip install pypdf openai python-dotenv
   \`\`\`
4. Create a `.env` file with your Groq API key:
   \`\`\`
   GROQ_API_KEY="gsk_your_key_here"
   \`\`\`
5. Add your `jd.txt` and CV PDF into the `resumes/` folder.
6. Run:
   \`\`\`bash
   python simple_rank.py
   \`\`\`

## 📊 Expected Output
\`\`\`
========== AI SCORING RESULTS ==========
1. Match Score: 78/100
2. Candidate Strengths: [MERN, DevOps, QA]
3. Weaknesses: [No professional experience]
4. Recommendation: Invite for an interview.
\`\`\`

## 🔒 Security
API keys are stored in `.env` and excluded from Git via `.gitignore`.

## 👤 Author
Atef Ahabab — SQA 19
