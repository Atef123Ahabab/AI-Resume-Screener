import streamlit as st
import os, re, base64, time, docx
import pypdf
import pymupdf as fitz
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")
MODEL = "qwen/qwen3.8-27b"

st.set_page_config(page_title="AI Resume Screener", page_icon="🏆", layout="wide")
st.title("🏆 AI Resume Screener")
st.markdown("---")

JD_FOLDER = "job_descriptions"
CV_FOLDER = "resumes/downloaded"

def get_evaluation_prompt(jd_text, cv_text):
    return f"""You are an expert Technical Recruiter.
Evaluate the CV against the Job Description below.
--- JOB DESCRIPTION ---
{jd_text}
--- CANDIDATE CV ---
{cv_text}
--- INSTRUCTIONS ---
1. Find the candidate's full name from the CV.
2. Score the candidate from 0 to 100 based on how well they match the JD.
3. Write ONE sentence explaining the score.
--- OUTPUT FORMAT ---
Reply exactly in this format (no markdown, no extra words):
NAME: [Candidate Full Name]
SCORE: [Integer 0-100]
REASON: [One sentence]
"""

def process_file(path, ext):
    if ext in ["jpeg", "jpg", "png"]:
        return None, base64.b64encode(open(path, "rb").read()).decode()
    text = ""
    if ext == "pdf":
        try:
            reader = pypdf.PdfReader(path)
            text = "".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            text = ""
        if len(text.strip()) < 50: 
            try:
                doc = fitz.open(path)
                pix = doc.load_page(0).get_pixmap(dpi=150)
                return None, base64.b64encode(pix.tobytes("jpeg")).decode()
            except Exception as e:
                return f"Error: {e}", None
    elif ext == "docx":
        try:
            text = "\n".join([p.text for p in docx.Document(path).paragraphs])
        except Exception as e:
            text = f"Error: {e}"
    elif ext == "txt":
        try:
            text = open(path, "r", encoding="utf-8", errors="ignore").read()
        except Exception as e:
            text = f"Error: {e}"
    return text, None

def extract_jd_title(text, b64_img=None):
    if b64_img:
        messages = [{"role": "user", "content": [
            {"type": "text", "text": "What is the exact Job Title in this image? Reply ONLY with the job title."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
        ]}]
    else:
        messages = [{"role": "user", "content": f"What is the exact Job Title in this text? Reply ONLY with the job title.\n\n{text[:1500]}"}]
    
    try:
        r = client.chat.completions.create(model=MODEL, messages=messages, temperature=0, max_tokens=20)
        return r.choices[0].message.content.strip().replace('"', '').replace('*', '')
    except:
        return "Unknown Job"

@st.cache_data(ttl=600, show_spinner=False)
def load_all_jds():
    jds = []
    if not os.path.exists(JD_FOLDER): return jds
    for fn in sorted(os.listdir(JD_FOLDER)):
        ext = fn.lower().split(".")[-1]
        if ext not in ["txt", "pdf", "docx", "jpeg", "jpg", "png"] or fn.startswith("."): continue
        path = os.path.join(JD_FOLDER, fn)
        text, b64_img = process_file(path, ext)
        title = extract_jd_title(text, b64_img)
        jds.append({
            "title": title, "filename": fn,
            "text": text, "b64_img": b64_img, "ext": ext
        })
    return jds

with st.spinner("Reading Job Descriptions and extracting titles..."):
    jd_list = load_all_jds()

if not jd_list:
    st.warning(f"No JDs found in `{JD_FOLDER}/`. Please add some.")
else:
    st.markdown("### 📋 Active Job Openings:")
    for jd in jd_list:
        st.markdown(f"- **{jd['title']}** `({jd['filename']})`")

st.markdown("---")

if st.button("🚀 Run AI Screening", type="primary"):
    if not jd_list:
        st.error("Please add Job Descriptions to the folder first.")
        st.stop()
        
    files = [f for f in sorted(os.listdir(CV_FOLDER)) 
             if f.lower().split(".")[-1] in ["pdf", "docx", "txt", "jpeg", "jpg", "png"] 
             and not f.startswith(".")]
    
    if not files:
        st.error(f"No valid CVs found in `{CV_FOLDER}/`!")
        st.stop()

    results = []
    progress_bar = st.progress(0)
    status = st.empty()
    
    for i, fn in enumerate(files):
        status.text(f"Analyzing CV {i+1}/{len(files)}: {fn}...")
        progress_bar.progress((i + 1) / len(files))
        
        path = os.path.join(CV_FOLDER, fn)
        ext = fn.lower().split(".")[-1]
        fallback_name = fn.rsplit('.', 1)[0]
        
        try:
            text, b64_img = process_file(path, ext)
        except Exception as e:
            results.append({"name": fallback_name, "file": fn, "scores": {}, "reason": f"Read Error: {e}"})
            continue

        scores = {}
        extracted_name = fallback_name
        best_reason = ""
        
        for jd in jd_list:
            jd_text = jd["text"] if jd["text"] else "[Image attached]"
            cv_text = text if text else "[Image attached]"
            prompt_text = get_evaluation_prompt(jd_text[:4000], cv_text[:4000])
            
            content = [{"type": "text", "text": prompt_text}]
            if jd["b64_img"]:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{jd['b64_img']}"}})
            if b64_img:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}})
            
            msgs = [{"role": "user", "content": content}] if len(content) > 1 else [{"role": "user", "content": prompt_text}]
            
            try:
                r = client.chat.completions.create(model=MODEL, messages=msgs, temperature=0.1, max_tokens=200)
                raw = r.choices[0].message.content.strip()
                
                sm = re.search(r"SCORE:\s*(\d+)", raw, re.IGNORECASE)
                nm = re.search(r"NAME:\s*([^\n|]+)", raw, re.IGNORECASE)
                rm = re.search(r"REASON:\s*(.+)", raw, re.IGNORECASE)
                
                score = min(int(sm.group(1)), 100) if sm else 0
                if nm: extracted_name = nm.group(1).strip()
                reason = rm.group(1).strip() if rm else "No reasoning."
                
                scores[jd["title"]] = {"score": score, "reason": reason}
                time.sleep(1.5)
            except Exception as e:
                scores[jd["title"]] = {"score": 0, "reason": f"API Error: {str(e)[:50]}"}

        if scores:
            best_jd = max(scores, key=lambda k: scores[k]["score"])
            best_score = scores[best_jd]["score"]
            best_reason = scores[best_jd]["reason"]
        else:
            best_jd = "N/A"
            best_score = 0
        
        results.append({
            "name": extracted_name, "file": fn, "scores": scores,
            "best_jd": best_jd, "max_score": best_score, "best_reason": best_reason
        })

    status.text("✅ Analysis complete!")
    progress_bar.empty()
    
    results.sort(key=lambda x: x["max_score"], reverse=True)
    
    # Group results by Job Description
    jd_results = {jd["title"]: [] for jd in jd_list}
    
    for r in results:
        for jd_title, data in r["scores"].items():
            if jd_title in jd_results:
                jd_results[jd_title].append({
                    "name": r["name"],
                    "file": r["file"],
                    "score": data["score"],
                    "reason": data["reason"]
                })

    st.markdown("---")

    # Display a separate ranking table for each JD
    for jd in jd_list:
        jd_title = jd["title"]
        st.header(f"📌 {jd_title} Rankings")
        
        # Sort this specific JD's candidates by score
        ranked_candidates = sorted(jd_results[jd_title], key=lambda x: x["score"], reverse=True)
        
        if not ranked_candidates:
            st.info("No CVs evaluated for this position.")
            continue
            
        for i, r in enumerate(ranked_candidates, 1):
            score = r['score']
            badge = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
            
            with st.expander(f"{badge} #{i} - {r['name']} (Score: {score}/100)", expanded=(i==1)):
                st.caption(f"**File:** {r['file']}")
                st.info(f"💡 **Analysis:** {r['reason']}")
        
        st.markdown("---")
