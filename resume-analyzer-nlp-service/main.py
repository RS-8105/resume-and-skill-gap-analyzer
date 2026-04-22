
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables securely from .env
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

# Initialize GROQ Client (Requires GROQ_API_KEY environment variable)
api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
) if api_key else None

def get_llm_response(prompt: str) -> str:
    """
    Takes a single prompt string, calls the GROQ LLM, and returns the response.
    Throws a 500 status code if the API key is not set or if the call fails.
    """
    if not client:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY environment variable is not set. Please set the key."
        )

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GROQ error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"GROQ API Error: {str(e)}")

# Input validation model using Pydantic
class ResumeRequest(BaseModel):
    resume: str = Field(..., description="The raw text extracted from the candidate's resume")
    company: str = Field(..., description="The target company name")
    role: str = Field(..., description="The target role name")
    experience_level: Optional[str] = Field("Beginner", description="Experience level of the candidate")

REQUIRED_ANALYSIS_FIELDS = {
    "present_skills": [],
    "missing_skills": [],
    "recommendations": [],
    "company_overview": "",
    "company_growth": "",
    "role_responsibilities": "",
    "average_salary": "",
    "optimized_resume": "",
    "recommended_companies": [],
}

REQUIRED_INSIGHT_FIELDS = {
    "company_overview": "",
    "company_growth": "",
    "role_responsibilities": "",
    "average_salary": "",
}

def parse_json_object(raw_response: str):
    obj_start = raw_response.find('{')
    obj_end = raw_response.rfind('}')
    arr_start = raw_response.find('[')
    arr_end = raw_response.rfind(']')
    
    is_obj_valid = obj_start != -1 and obj_end != -1 and obj_start < obj_end
    is_arr_valid = arr_start != -1 and arr_end != -1 and arr_start < arr_end
    
    if is_obj_valid and is_arr_valid:
        if obj_start < arr_start and obj_end > arr_end:
            # array is inside object
            cutoff_start, cutoff_end = obj_start, obj_end
        elif arr_start < obj_start and arr_end > obj_end:
            # object is inside array
            cutoff_start, cutoff_end = arr_start, arr_end
        else:
            # Independent object and array? Pick whichever comes first but is most likely the main wrapper
            # In our case, we usually expect EITHER an array OR an object. 
            # If the LLM returns text with `{` before the `[`, but the `[` encapsulates the real data...
            # A simple heuristic: pick the one that encapsulates the most text.
            obj_len = obj_end - obj_start
            arr_len = arr_end - arr_start
            if obj_len > arr_len:
                cutoff_start, cutoff_end = obj_start, obj_end
            else:
                cutoff_start, cutoff_end = arr_start, arr_end
    elif is_obj_valid:
        cutoff_start, cutoff_end = obj_start, obj_end
    elif is_arr_valid:
        cutoff_start, cutoff_end = arr_start, arr_end
    else:
        cutoff_start, cutoff_end = 0, len(raw_response) - 1

    try:
        sliced_response = raw_response[cutoff_start:cutoff_end + 1]
        return json.loads(sliced_response)
    except json.JSONDecodeError:
        # Fallback to pure string cleanup on the sliced part
        sliced_response = raw_response[cutoff_start:cutoff_end + 1]
        clean_json = sliced_response.strip(" \n\t`").lstrip("json").strip(" \n\t")
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            clean_json = clean_json.replace("'", '"')
            try:
                return json.loads(clean_json)
            except json.JSONDecodeError:
                # Absolute last resort: use regex to extract quoted strings from the raw response
                import re
                strings = re.findall(r'"([^"]*)"', raw_response)
                # Filter out likely keys if it's an object, we just want bullet points
                bullets = [s for s in strings if len(s) > 15] 
                if len(bullets) >= 2:
                    return bullets
                return []

def normalize_analysis_response(analysis_result: dict):
    normalized = {
        key: analysis_result.get(key, default)
        for key, default in REQUIRED_ANALYSIS_FIELDS.items()
    }
    present_skills = analysis_result.get("present_skills", [])
    missing_skills = analysis_result.get("missing_skills", [])
    
    total_skills = len(present_skills) + len(missing_skills)
    calculated_match = int((len(present_skills) / total_skills) * 100) if total_skills > 0 else 0
    
    normalized["skill_match_percentage"] = calculated_match
    normalized["similarity_score"] = calculated_match
    return normalized

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

def analyze_resume(resume_text: str, company: str, role: str, experience_level: str = "Beginner"):
    """
    Uses the LLM to compare the candidate's resume with the target role.
    """
    print("Company:", company)
    print("Role:", role)
    print("Experience:", experience_level)
    print("Resume Text (Partial):", resume_text[:100].replace("\n", " "))
    prompt = f"""You are a recruiter at {company}. Consider hiring standards, company culture, and typical expectations for a {experience_level} level {role}.

Compare the candidate resume with the requirements and expectations of a {experience_level} level {role} at {company}.
Extract standard required skills for this role and compare them against the resume.
IMPORTANT: Consolidate similar skills, remove duplicates, and group skills with the same meaning. Keep the missing skills list concise (e.g. maximum 10-15 key skills).

Provide a calculated match percentage from 0 to 100 representing how well the resume fits the role.
CRITICAL SCORING RULE: The score MUST be highly specific to {company} and {role}. Deduct points heavily if the resume lacks skills typically essential for {company}'s specific tech stack or caliber. The score should drastically change depending on whether {company} is a startup vs FAANG, or frontend vs backend {role}.

You must output ONLY valid JSON.
No explanation text.
No markdown formatting (do not use ```json).

Return this exact format (replace the 0 with your calculated integer between 0 and 100):
{{
  "match_percentage": 0,
  "present_skills": [],
  "missing_skills": []
}}

Candidate Resume:
{resume_text}"""

    for attempt in range(3):
        raw_response = get_llm_response(prompt)
        try:
            resume_data = parse_json_object(raw_response)
            
            # Explicitly generate optimized recommendations
            resume_data["recommendations"] = generate_recommendations(
                company, 
                role, 
                resume_data.get("present_skills", []), 
                resume_data.get("missing_skills", [])
            )

            insights = get_company_job_insights(company, role)
            resume_data.update({
                key: insights.get(key, default)
                for key, default in REQUIRED_INSIGHT_FIELDS.items()
            })
            job_desc = insights.get("role_responsibilities", f"Role of {role} at {company}")
            resume_data["optimized_resume"] = rebuild_resume(resume_text, job_desc, company, role)
            resume_data["recommended_companies"] = recommend_companies(
                resume_text, 
                company, 
                role, 
                resume_data.get("missing_skills", []), 
                resume_data.get("present_skills", [])
            )
            return resume_data
        except json.JSONDecodeError as e:
            if attempt == 2:
                print(f"JSON Parse Error analyze_resume: {str(e)}. Raw: {raw_response}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse analyze_resume output into JSON format after 3 attempts. Raw: {raw_response}"
                )

def get_company_job_insights(company: str, role: str):
    """
    Generates structured insights about a company and a specific role.
    """
    prompt = f"""Give a structured response about the company {company} and the role {role}. 
Include:
1. What the company does
2. Growth and market position
3. Responsibilities of the role in that company
4. Average salary range for that role in Indian Rupees (INR)

You must output ONLY valid JSON.
No explanation text.
No markdown formatting (do not use ```json).

Return this exact format:
{{
  "company_overview": "",
  "company_growth": "",
  "role_responsibilities": "",
  "average_salary": ""
}}"""

    for attempt in range(3):
        raw_response = get_llm_response(prompt)
        try:
            insights = parse_json_object(raw_response)
            return {
                key: insights.get(key, default)
                for key, default in REQUIRED_INSIGHT_FIELDS.items()
            }
        except json.JSONDecodeError as e:
            if attempt == 2:
                print(f"JSON Parse Error get_company_job_insights: {str(e)}. Raw: {raw_response}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to parse insights output into JSON format after 3 attempts. Raw: {raw_response}"
                )

@app.post("/analyze")
def api_analyze_resume(data: ResumeRequest):
    """
    Accepts resume text, company, role, and experience level.
    Sequentially processes candidate comparison and insights.
    """
    
    resume_text = data.resume
    company = data.company
    role = data.role
    experience_level = data.experience_level
    print("Company:", company)
    print("Role:", role)
    print("Experience:", experience_level)

    # 1. Compare Role against Resume in single hit
    analysis_result = analyze_resume(resume_text, company, role, experience_level)
    
    # 3. Shape the JSON object explicitly to what the React UI component needs
    return normalize_analysis_response(analysis_result)

def rebuild_resume(resume_text: str, job_description: str, company: str, role: str) -> str:
    """
    Rewrites the resume to better match the job description and company.
    """
    prompt = f"""Rewrite the following resume to match the role of {role} at {company}.

Rules:
- Do NOT invent experience
- Optimize for ATS keywords
- Improve clarity and impact
- Align skills with job description
- concise content
- no long paragraphs
- optimized for one-page resume
- Limit projects to max 2-3
- Limit bullet points per project to 2-3
- Keep each bullet point under 15 words
- Keep objective under 2 lines

You must output STRICT JSON ONLY. Do not use markdown blocks (e.g. ```json).

Return exactly in this JSON format:
{{
  "name": "",
  "phone": "",
  "email": "",
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "objective": "",
  "education": "",
  "skills": {{
    "languages": "",
    "frontend": "",
    "backend": "",
    "database": "",
    "tools": "",
    "core": ""
  }},
  "projects": [
    {{
      "title": "",
      "description": [],
      "tech_stack": ""
    }}
  ],
  "exposure": [],
  "achievements": [],
  "activities": [],
  "strengths": ""
}}

Resume:
{resume_text}

Job Description:
{job_description}"""

    return get_llm_response(prompt)


def generate_recommendations(company: str, role: str, present_skills: list, missing_skills: list) -> list:
    """
    Generates personalized, specific recommendations to improve candidate selection chances.
    """
    print("Company:", company)
    print("Role:", role)
    print("Missing Skills:", missing_skills)
    prompt = f"""Based on the candidate's resume, target company {company}, and role {role},

Analyze:
- Required skills for this role in this company
- Candidate's present skills
- Missing skills

Then generate personalized recommendations to improve chances of selection in THIS company.

Context:
Present Skills: {', '.join(present_skills)}
Missing Skills: {', '.join(missing_skills)}

Rules:
- Must be specific to company and role
- No generic advice
- Suggest tools, technologies, or concepts
- Keep 4–5 concise bullet points

If output is generic, regenerate it to be company-specific.

You must output STRICT JSON ONLY. Do not use markdown blocks, no newlines inside brackets.

Return exactly 4-5 concise bullet points in this exact JSON array format:
["bullet 1", "bullet 2", "bullet 3", "bullet 4"]
"""
    for attempt in range(2):
        raw_response = get_llm_response(prompt)
        print(f"RAW RECOMMENDATION RESPONSE (Attempt {attempt+1}):\n", raw_response)
        try:
            data = parse_json_object(raw_response)
            print(f"PARSED DATA (Attempt {attempt+1}):", data)
            if isinstance(data, dict):
                flat_list = []
                for v in data.values():
                    if isinstance(v, list):
                        flat_list.extend(v)
                    else:
                        flat_list.append(v)
                data = flat_list
            
            if isinstance(data, list) and len(data) > 0:
                print(f"Generated Recommendations (Attempt {attempt+1}):", data)
                return data
            else:
                print(f"Data is not a list or is empty. Retrying...")
        except Exception as e:
            print(f"Error parsing recommendations (Attempt {attempt+1}):", str(e))
        
        prompt += "\nSTRICT RULE: YOU MUST RETURN AT LEAST 4 BULLET POINTS. DO NOT BE GENERIC."
    
    return []

def generate_resume_html(data: dict) -> str:
    """
    Generates a compact, professional single-page HTML resume from structured JSON data.
    """
    def truncate(text, max_len=200):
        if not text: return ""
        return text if len(text) <= max_len else text[:max_len].rsplit(' ', 1)[0] + '...'

    name = data.get("name", "YOUR NAME")
    contact_parts = [
        data.get("phone"), 
        data.get("email"), 
        data.get("linkedin"), 
        data.get("github"), 
        data.get("portfolio")
    ]
    contact = " | ".join([p for p in contact_parts if p and str(p).strip()])
    
    objective = truncate(data.get("objective", ""), 300)
    education = truncate(data.get("education", ""), 200)
    
    skills = data.get("skills", {})
    skills_html = "".join([
        f"<div style='margin-bottom: 2px;'><strong>{k.capitalize()}:</strong> {v}</div>"
        for k, v in skills.items() if v and str(v).strip()
    ])

    projects_html = ""
    for p in data.get("projects", [])[:3]:
        desc_list = "".join([f"<li>{truncate(d, 120)}</li>" for d in p.get("description", [])[:2]])
        projects_html += f"""
        <div style='margin-bottom: 6px;'>
            <strong>{p.get('title', '')}</strong>
            <ul style='margin: 2px 0 2px 20px; padding: 0;'>{desc_list}</ul>
            <div style='font-size: 0.9em; color: #555;'><strong>Tech Stack:</strong> {p.get('tech_stack', '')}</div>
        </div>
        """

    def simple_list(items, max_items=3, max_len=150):
        if not items: return ""
        return "<ul style='margin: 2px 0 2px 20px; padding: 0;'>" + \
               "".join([f"<li>{truncate(i, max_len)}</li>" for i in items[:max_items]]) + \
               "</ul>"

    exposure_html = simple_list(data.get("exposure", []))
    achievements_html = simple_list(data.get("achievements", []))
    activities_html = simple_list(data.get("activities", []))
    strengths = truncate(data.get("strengths", ""), 200)

    html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 10pt; line-height: 1.3; color: #000; max-width: 800px; margin: 0 auto; padding: 0.5in;">
        <div style="margin-bottom: 15px;">
            <div class="name">{name}</div>
            <div class="contact">{contact}</div>
            <div class="divider"></div>
        </div>
    """

    def section(title, content):
        if not content or not str(content).strip(): return ""
        return f"""
        <div style="margin-bottom: 10px;">
            <h4 style="color: #0d47a1; border-bottom: 1.5px solid #0d47a1; margin: 0 0 4px 0; font-size: 11pt; text-transform: uppercase; padding-bottom: 2px;">{title}</h4>
            {content}
        </div>
        """

    html += section("Objective", f"<p style='margin: 2px 0;'>{objective}</p>" if objective else "")
    html += section("Education", f"<p style='margin: 2px 0;'>{education}</p>" if education else "")
    html += section("Technical Skills", skills_html)
    html += section("Projects", projects_html)
    html += section("Practical Exposure", exposure_html)
    html += section("Achievements", achievements_html)
    html += section("Activities", activities_html)
    html += section("Strengths", f"<p style='margin: 2px 0;'>{strengths}</p>" if strengths else "")

    html += "</div>"
    return html


def generate_pdf(data: dict, filename: str = "Optimized_Resume.pdf"):
    """
    Generates a PDF from the HTML content and saves it to the given filename.
    Ensures A4 size, no breaks, and everything fits tightly.
    """
    from weasyprint import HTML

    html_content = generate_resume_html(data)
    
    # Wrap with full document constraints for WeasyPrint
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4 portrait;
                margin: 0; 
                padding: 0;
            }}
            body, html {{
                width: 210mm;
                height: 297mm;
                margin: 0;
                padding: 0;
                background-color: #ffffff;
                box-sizing: border-box;
                overflow: hidden; 
            }}
            * {{
                page-break-inside: avoid;
            }}
            .name {{
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                letter-spacing: 1px;
            }}
            .contact {{
                font-size: 12px;
                text-align: center;
                color: #444;
                margin-top: 4px;
            }}
            .divider {{
                border-top: 1px solid #000;
                margin: 8px 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    HTML(string=full_html).write_pdf(filename)
    return filename

def recommend_companies(resume_text: str, company: str, role: str, missing_skills: list, present_skills: list) -> list:
    """
    Suggests 5-7 companies similar to the input company where the candidate has higher chances 
    based on their present skills and lacking skills.
    """
    prompt = f"""Given the candidate's resume, target company {company}, and role {role},

Suggest similar companies where:
- The candidate has a better chance of selection
- Skills align better
- Hiring standards are realistic

Use candidate skills:
{present_skills}

Avoid:
- FAANG unless highly qualified
- unrealistic suggestions

You must output STRICT JSON ONLY. Do not use markdown blocks.

Return exactly in this JSON format:
[
  {{
    "company": "Company Name",
    "reason": "Brief reason why they are a good fit",
    "fit_score": "e.g., 85"
  }}
]

Resume:
{resume_text}
    """
    
    raw_response = get_llm_response(prompt)
    try:
        data = parse_json_object(raw_response)
        return data if isinstance(data, list) else []
    except Exception:
        return []
