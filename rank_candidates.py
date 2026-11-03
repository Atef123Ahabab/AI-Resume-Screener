import reveilio

# 1. Configure API Key (Put your actual Gemini key here inside the quotes)
reveilio.configure(provider="gemini", api_key="YOUR_ACTUAL_API_KEY_HERE")

print("Loading Job Description...")
# Make sure this says jd.txt
jd = reveilio.JobDescription.from_file("jd.txt") 

print("Analyzing resumes... This may take a minute.")
results = reveilio.analyze_folder("resumes/", jd)

print("\n--- CANDIDATE RANKINGS ---")
for r in results:
    print(f"Rank {r.rank}: {r.candidate_data.name} | Score: {r.overall_score}")

# Save Report
reveilio.save_batch_report_pdf(results, "output/ranking_report.pdf")
print("\nReport saved to output/ranking_report.pdf")