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
