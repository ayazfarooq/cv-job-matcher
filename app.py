import os
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# Set page layout
st.set_page_config(page_title="AI CV & Job Matcher", page_icon="📄", layout="wide")

# 2. Google Analytics Tracking Function
def inject_google_analytics(measurement_id: str):
    ga_code = f"""
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={measurement_id}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{measurement_id}');
    </script>
    """
    # Inject 0-pixel height component to load script invisibly
    components.html(ga_code, height=0, width=0)


# 3. Inject Analytics (Replace G-XXXXXXXXXX with your actual Measurement ID)
GA_MEASUREMENT_ID = st.secrets.get("GA_MEASUREMENT_ID") or "G-XXXXXXXXXX"
inject_google_analytics(GA_MEASUREMENT_ID)

# Check if user is logged in
if not st.experimental_user.is_logged_in if hasattr(st, "experimental_user") else False:
    # Streamlit OIDC Authentication check
    pass

# Display Auth Status / Login UI
if not st.user.is_logged_in:
    st.title("🔒 Welcome to AI CV Matcher")
    st.write("Please sign in with your Google Account to access the application.")
    
    if st.button("Log in with Google", type="primary"):
        st.login("google")
else:
    # Header & User Info Banner
    col_title, col_user = st.columns([3, 1])
    with col_title:
        st.title("📄 AI CV & Job Description Matcher")
    with col_user:
        st.write(f"Logged in as **{st.user.name}**")
        st.caption(f"({st.user.email})")
        if st.button("Log out"):
            st.logout()

    st.write("Upload a candidate's CV and a Job Description to get an instant match score and detailed HR analysis.")
    st.markdown("---")

    # Retrieve API Key from Secrets or Environment Variables
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

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
            st.error("API Key missing! Make sure GEMINI_API_KEY is configured in Streamlit Secrets.")
        elif not cv_file or not jd_file:
            st.warning("Please upload both a CV and a Job Description before running the evaluation.")
        else:
            try:
                with st.spinner("Analyzing document compatibility with Gemini..."):
                    client = genai.Client(api_key=api_key)

                    cv_part = types.Part.from_bytes(
                        data=cv_file.getvalue(),
                        mime_type=cv_file.type
                    )
                    
                    jd_part = types.Part.from_bytes(
                        data=jd_file.getvalue(),
                        mime_type=jd_file.type
                    )

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
                    [Bullet points of key qualifications missing from the CV]

                    ### 💡 Recommendations
                    [Specific advice for the hiring manager or candidate]
                    """

                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[cv_part, jd_part, prompt]
                    )

                    st.success("Evaluation Complete!")
                    st.markdown("---")
                    st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred during evaluation: {e}")