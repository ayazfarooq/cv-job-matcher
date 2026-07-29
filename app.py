import os
import streamlit as st
from google import genai
from google.genai import types

# Set page title and layout
st.set_page_config(page_title="AI CV & Job Matcher", page_icon="📄", layout="wide")

st.title("📄 AI CV & Job Description Matcher")
st.write("Upload a candidate's CV and a Job Description to get an instant match score and detailed HR analysis.")

# Sidebar for API Key input or fallback to environment variable
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Leave blank if GEMINI_API_KEY is set in environment")
    
    # Initialize API key
    api_key = api_key_input or os.environ.get("GEMINI_API_KEY")

# Upload UI columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Candidate CV")
    cv_file = st.file_uploader("Upload CV (PDF or TXT)", type=["pdf", "txt"], key="cv")

with col2:
    st.subheader("2. Job Description")
    jd_file = st.file_uploader("Upload Job Description (PDF or TXT)", type=["pdf", "txt"], key="jd")

# Action Button
if st.button("Evaluate Match", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar or set the GEMINI_API_KEY environment variable.")
    elif not cv_file or not jd_file:
        st.warning("Please upload both a CV and a Job Description before running the evaluation.")
    else:
        try:
            with st.spinner("Analyzing document compatibility with Gemini..."):
                # Initialize GenAI Client
                client = genai.Client(api_key=api_key)

                # Convert uploaded files in-memory to Parts
                cv_part = types.Part.from_bytes(
                    data=cv_file.getvalue(),
                    mime_type=cv_file.type
                )
                
                jd_part = types.Part.from_bytes(
                    data=jd_file.getvalue(),
                    mime_type=jd_file.type
                )

                # Structured Evaluation Prompt
                prompt = """
                You are an expert ATS (Applicant Tracking System) reviewer and technical hiring manager.
                Compare the attached candidate CV against the attached Job Description.

                Provide your analysis strictly structured as follows:

                ## 🎯 MATCHING SCORE: [Score out of 100]%

                ### 📝 Executive Summary
                [2-3 sentences summarizing overall candidate fit]

                ### ✅ Key Matches & Strengths
                [Bullet points of matching skills, tools, and experiences]

                ### ⚠️ Gaps & Missing Requisites
                [Bullet points of key qualifications or skills required in the job description that are missing from the CV]

                ### 💡 Recommendations
                [Specific advice for the hiring manager or candidate]
                """

                # Query Gemini Model
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[cv_part, jd_part, prompt]
                )

                st.success("Evaluation Complete!")
                st.markdown("---")
                
                # Display Results
                st.markdown(response.text)

        except Exception as e:
            st.error(f"An error occurred during evaluation: {e}")