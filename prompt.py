def get_evaluation_prompt(jd_text, cv_text):
    return f"""You are an expert, unbiased Technical Recruiter and Data Analyst.
Your task is to evaluate a candidate's CV strictly against the provided Job Description (JD).

--- JOB DESCRIPTION ---
{jd_text}

--- CANDIDATE CV ---
{cv_text}

--- INSTRUCTIONS ---
1. Extract the specific skills, experience, and education required by the JD.
2. Cross-reference these requirements against the CV.
3. Assign a score from 0 to 100 based strictly on these weights:
   - Skills Match (40%): How many required skills does the candidate explicitly have?
   - Experience Level (30%): Does the candidate have the required years and relevant roles?
   - Education & Certs (20%): Do they have the required degrees or certifications?
   - Overall Fit (10%): Based on the context of their history.
4. If the CV has NO text or is unreadable, you MUST output a score of 0 and explain why.
5. Do not round to random nice numbers (like 65 or 70) unless mathematically justified by the rubric.

--- OUTPUT FORMAT ---
You MUST reply exactly in this format:
NAME: [Candidate Name]
SCORE: [Integer 0-100]
REASON: [A single, concise sentence justifying the score based on the rubric.]
"""