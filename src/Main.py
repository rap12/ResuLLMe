import streamlit as st
import streamlit_ext as ste
import os
import google.generativeai as genai

from doc_utils import extract_text_from_upload

PROMPT_ASSESSMENT = """
You are an HR professional who reviews and assess resume of applicants. Extract the following fields in this uploaded resume:
- Name
- Email
- Mobile Number
- Check the latest education. Mention \"College\" if the last degree was college, Mention \"Post Grad\" if last degree was masteral and above
- Summarize her related experience in accounting as a list
- Check if the applicants fits the attached job description. Assess if the Applicant \"Pass\" or \"Fail\"  then provide a 3-4 bullet explanation to support your assessment
- Provide a list of interview questions

"""
OUTPUT_FORMAT = """
Follow the output format below and remove any conversational introduction:

Applicant Information [style: bold header]
- Name: 
- Email: 
- Mobile Number: 
- Highest Educational Attainment: 
- Related Experience: [List as sub-bullets]

AI Assessment (Resume x Job Description) [style: bold header]
- Pass or Fail:
- Explanation: [List as sub-bullets]

Recommended Interview Question [style: bold header]
- [List as bullet]
"""


st.set_page_config(
    page_title="Senti AI: HR Demo",
    page_icon=":clipboard:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.sidebar.write("## Upload Resume :gear:")

def get_llm_model_and_api(model_type):

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.sidebar.text_input(
                "Enter your API Key:",
                type="password",
        )
    api_model = "gemini-2.0-flash"
    return api_key, api_model


def assess_resume(text_resume, text_jd, api_key):
    """Generate a JSON resume from a CV text"""
    
    model = "gemini-2.0-flash"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model)


    full_prompt = f"{PROMPT_ASSESSMENT}\n\nHere's the resume: {text_resume}\nHere's the job description: {text_jd}\n\n {OUTPUT_FORMAT}"
    response = model.generate_content(full_prompt)
    answer = response.parts[0].text
    answer = answer.strip("'").replace("```json\n", "").replace("\n```", "")

    return answer




if __name__ == '__main__':

    st.markdown(
        f"""
        # Senti AI: HR Demo
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "Doc AI + Gen AI Demo! Upload a sample resume, and let the AI extract information and generate assssment"
    )

    model_type = "Gemini"
    api_key, api_model = get_llm_model_and_api(model_type)

    uploaded_file = st.sidebar.file_uploader("Upload Resume", type=["pdf"])

    uploaded_desc = st.sidebar.file_uploader("Upload Job Description", type=["pdf"])

    generate_button = st.sidebar.button("Assess Resume")


    if uploaded_file and uploaded_desc is not None:
        # Get the CV data that we need to convert to json
        text_resume = extract_text_from_upload(uploaded_file)
        text_jd = extract_text_from_upload(uploaded_desc)

        if len(text_resume) < 50:
            st.warning("The text extracted from the uploaded file is too short. Are you sure this is the correct file?",
                       icon="⚠️")

        if generate_button:
            with st.spinner("Assessing Resume"):
                ai_assesment = assess_resume(text_resume, text_jd, api_key)

            st.info(ai_assesment)

    else:
        st.info("Please upload files to get started.")
