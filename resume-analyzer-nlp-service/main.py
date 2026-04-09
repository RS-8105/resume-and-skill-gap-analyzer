
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables securely from .env
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

# Initialize Google Gemini Client (Requires GEMINI_API_KEY environment variable)
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemini-2.5-flash')

def get_llm_response(prompt: str) -> str:
    """
    Takes a single prompt string, calls the Google Gemini LLM, and returns the response.
    Throws a 500 status code if the API key is not set or if the call fails.
    """
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="GEMINI_API_KEY environment variable is not set. Please set the key."
        )

    try:
        # Utilizing gemini-2.5-flash by default for fast, free-tier inclusive access!
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.0}
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API Error: {str(e)}")

# Input validation model using Pydantic
class ResumeRequest(BaseModel):
    resume_text: str = Field(..., description="The raw text extracted from the candidate's resume")
    company: str = Field(..., description="The target company name")
    job_description: str = Field(..., description="The full job description text")

def extract_skills(job_description: str, company: str):
    """
    Extracts structured skill breakdown from a job description using the LLM with parse retry logic.
    """
    prompt = f"""You are a recruiter at {company}. Consider hiring standards, company culture, and typical expectations.

Analyze the following job description for '{company}' and extract:
- Technical skills
- Soft skills
- Tools/technologies

IMPORTANT: Consolidate similar skills, remove duplicates, and group skills with the same meaning. Keep the lists concise.

You must output ONLY valid JSON.
No explanation text.
No markdown formatting (do not use ```json).

Return this exact format:
{{
  "technical_skills": [],
  "soft_skills": [],
  "tools": []
}}

Job Description:
{job_description}"""

    for attempt in range(3):
        raw_response = get_llm_response(prompt)
        # Attempt to clean it just in case despite the strict prompt
        clean_json = raw_response.strip(" \n\t`").lstrip("json").strip(" \n\t")
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            if attempt == 2:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse extract_skills output into JSON format after 3 attempts. Raw: {raw_response}"
                )

def analyze_resume(resume_text: str, job_description: str, company: str):
    """
    Uses the LLM to compare the candidate's resume with the job description in a single call.
    """
    prompt = f"""You are a recruiter at {company}. Consider hiring standards, company culture, and typical expectations.

Compare the candidate resume with the following job description.
Extract required skills from the job description and compare them against the resume.
IMPORTANT: Consolidate similar skills, remove duplicates, and group skills with the same meaning. Keep the missing skills list concise (e.g. maximum 10-15 key skills).

You must output ONLY valid JSON.
No explanation text.
No markdown formatting (do not use ```json).

Return this exact format:
{{
  "match_percentage": 0,
  "present_skills": [],
  "missing_skills": [],
  "recommendations": []
}}

Job Description:
{job_description}

Candidate Resume:
{resume_text}"""

    for attempt in range(3):
        raw_response = get_llm_response(prompt)
        clean_json = raw_response.strip(" \n\t`").lstrip("json").strip(" \n\t")
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            if attempt == 2:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse analyze_resume output into JSON format after 3 attempts. Raw: {raw_response}"
                )

@app.post("/analyze")
def api_analyze_resume(data: ResumeRequest):
    """
    Accepts resume text, company, and job description.
    Sequentially processes JD extraction, then candidate comparison.
    """
    
    resume_text = data.resume_text
    company = data.company
    job_description = data.job_description

    # 1. Compare JD against Resume in single hit
    analysis_result = analyze_resume(resume_text, job_description, company)
    
    # 3. Shape the JSON object explicitly to what the React UI component needs
    return {
        "present_skills": analysis_result.get("present_skills", []),
        "missing_skills": analysis_result.get("missing_skills", []),
        "skill_match_percentage": analysis_result.get("match_percentage", 0),
        "similarity_score": analysis_result.get("match_percentage", 0),
        "recommendations": analysis_result.get("recommendations", [])
    }