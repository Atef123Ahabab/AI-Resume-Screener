import streamlit as st
import os, re, base64, time, docx, io
import pypdf
import fitz  # PyMuPDF for PDF-to-image fallback
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

st.set_page_config(page_title="AI Resume Screener", page_icon="🏆", layout="wide")

# --- DYNAMIC UI ---
try:
    with open("jd.txt", "r", encoding="utf-8") as f:
        jd_full_text = f.read()
    first_line = jd_full_text.strip().split("\n")[0]
    job_title = first_line[:80] + "..." if len(first_line) > 80 else first_line
except Exception:
    jd_full_text = "Job Description not found."
    job_title = "Unknown Job"

st.title("🏆 AI Resume Screener")
st.markdown(f"**Job Description:** {job_title}")
st.markdown("---")

folder = "resumes/downloaded"

def process_file(path, ext):
    """Extracts text, or returns base64 image if it's a scanned PDF/Image."""
    if ext in ["jpeg", "jpg", "png"]:
        return None, base64.b64encode(open(path, "rb").read()).decode()
    
    text = ""
    if ext == "pdf":
        try:
            reader = pypdf.PdfReader(path)
            text = "".join(p.extract_text() for p in reader.pages if p.extract_text())
        except Exception:
            text = ""
        
        # FALLBACK: If PDF has no text (scanned), convert first page to image
        if len(text.strip()) < 50: 
            try:
                doc = fitz.open(path)
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=150)
                img_data = pix.tobytes("jpeg")
                return None, base64.b64encode(img_data).decode()
            except Exception as e:
                return f"Error converting PDF to image: {e}", None
                
    elif ext == "docx":
        try:
            doc = docx.Document(path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            text = f"Error reading docx: {e}"
    elif ext == "txt":
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            text = f"Error reading txt: {e}"
            
    return text, None

if st.button("🚀 Run AI Screening", type="primary"):
    results = []
    status = st.empty()
    valid_exts = ["pdf", "jpeg", "jpg", "png", "docx", "txt"]
    
    files = [f for f in sorted(os.listdir(folder)) if f.lower().split(".")[-1] in valid_exts and not f.startswith(".")]
    
    if not files:
        st.error("No valid CVs found in 'resumes/downloaded'!")
    else:
        progress_bar = st.progress(0)
        
        for i, fn in enumerate(files):
            status.text(f"Analyzing {i+1} of {len(files)}: {fn}...")
            progress_bar.progress((i + 1) / len(files))
            
            path = os.path.join(folder, fn)
            ext = fn.lower().split(".")[-1]
            name = fn.rsplit('.', 1)[0]
            
            try:
                text, b64_img = process_file(path, ext)
                
                if b64_img:
                    # VISION AI for Images or Scanned PDFs
                    messages = [{"role": "user", "content": [
                        {"type": "text", "text": f"Job Description: {jd_full_text[:2000]}. Extract candidate name and score this resume 0-100. Reply: NAME: [name] | SCORE: [number]"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}]
                else:
                    # TEXT AI for normal PDFs, DOCX, TXT
                    messages = [{"role": "user", "content": f"Job Description: {jd_full_text[:2000]}. Resume: {text[:2500]}. Extract candidate name and score 0-100. Reply: NAME: [name] | SCORE: [number]"}]
                
                r = client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0, max_tokens=50)
                raw = r.choices[0].message.content.strip()
                
                sm = re.search(r"SCORE:\s*(\d+)", raw)
                nm = re.search(r"NAME:\s*([^|]+)", raw)
                
                score = min(int(sm.group(1)), 100) if sm else 0
                extracted = nm.group(1).strip() if nm else name
                results.append({"name": extracted, "file": fn, "score": score})
                
            except Exception as e:
                results.append({"name": name, "file": fn, "score": 0})
            
            time.sleep(2.5)
            
        status.text("✅ Analysis complete!")
        progress_bar.empty()
        
        results.sort(key=lambda x: x["score"], reverse=True)
        st.markdown("---")
        st.subheader(f"🏆 Final Candidate Ranking ({len(results)} CVs Analyzed)")
        
        for i, r in enumerate(results, 1):
            col1, col2, col3 = st.columns([1, 4, 2])
            with col1:
                st.markdown(f"### #{i}")
            with col2:
                st.markdown(f"**{r['name']}**")
                st.caption(r["file"])
            with col3:
                if r["score"] >= 70:
                    st.success(f"**{r['score']} / 100** ✅")
                elif r["score"] >= 50:
                    st.warning(f"**{r['score']} / 100** ⚠️")
                else:
                    st.error(f"**{r['score']} / 100** ❌")
        
        st.markdown("---")
        st.subheader("📊 Score Distribution")
        chart_data = {r["name"]: r["score"] for r in results}
        st.bar_chart(chart_data)
else:
    st.info("Click the button above to start the AI screening. Supports PDF, DOCX, TXT, and Images (including Scanned PDFs).")
