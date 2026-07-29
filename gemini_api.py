import os
from google import genai

# Initialize the client (uses GEMINI_API_KEY environment variable)
client = genai.Client()

# Path to your local CV file (e.g., 'resume.pdf')
CV_FILE_PATH = "Lebenslauf.pdf" 
JD_FILE_PATH = "jd.txt"

# 1. Upload the CV to Gemini's File API
print("Uploading CV...")
cv_file = client.files.upload(file=CV_FILE_PATH)
jd_file = client.files.upload(file=JD_FILE_PATH)
print(f"Uploaded successfully as: {cv_file.name}")

# 2. Define your evaluation prompt
prompt = """
You are an expert ATS (Applicant Tracking System) reviewer and hiring manager. 
Compare the attached Candidate CV against the attached Job Description.

Please provide your evaluation structured exactly as follows:

1. MATCHING SCORE: [Provide a numerical score strictly between 0 and 100]
2. EXECUTIVE SUMMARY: [2-3 sentences summarizing the candidate's alignment]
3. KEY MATCHES: [Bullet points of matching skills, experience, and tools]
4. GAPS & MISSING REQUISITES: [Bullet points of required skills/qualifications the candidate lacks]
5. RECOMMENDATION: [Brief advice on whether to interview or how to bridge gaps]
"""

# 3. Generate content by passing both the uploaded file object and the prompt
print("Evaluating CV...")
response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[cv_file, jd_file, prompt]
)

# 4. Output the feedback
print("\n--- CV Evaluation Feedback ---")
print(response.text)

# 5. Clean up the uploaded file from the server
client.files.delete(name=cv_file.name)
print("\nCleanup complete.")