import pypdf
import sys

# Change this to your PDF filename
pdf_file = sys.argv[1] if len(sys.argv) > 1 else "my_job_description.pdf"

try:
    with open(pdf_file, "rb") as f:
        reader = pypdf.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    
    with open("jd.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"✅ Extracted {len(text)} characters from {pdf_file}")
    print("✅ Saved to jd.txt")
    print("\nPreview:")
    print(text[:500])
    
except FileNotFoundError:
    print(f"❌ File not found: {pdf_file}")
    print("Usage: python convert_jd.py <your_jd.pdf>")
except Exception as e:
    print(f"❌ Error: {e}")
