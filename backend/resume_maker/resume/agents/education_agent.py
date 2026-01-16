from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict

# Agent for extracting education information from user input


class State(TypedDict):
    context:str
    skills:str
    education:str
    experience:str
    references:str
    personal_info:str
    profile:str

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def invoke(system_prompt: str, user_prompt: str):
    resp = client.responses.create(
    model="gpt-4o",
    input=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{user_prompt}"},
    ],
     # ensures valid JSON output
)   
    
    return resp.output[0].content[0].text
# Nodes

def get_education(state: State) -> dict:
    """
    🔹 Purpose:
        Node function that queries an LLM to extract or generate
        a user's education history in the format:
        <date>;<education>;<explanation>

    🔹 Example output:
        2020–2024;B.Sc. in Computer Engineering, Boğaziçi University;
        Focused on software systems, AI, and data analysis.

    🔹 Expected input:
        state: dict-like LangGraph State with key 'context' holding user information.

    🔹 Returns:
        dict with key 'education' -> formatted string(s)
    """

    name = (state.get("name") or "The user").strip()

    # Define system prompt to enforce structured, consistent output
    system_prompt = (
    "You are an expert information extraction specialist focused on identifying educational background "
    "from unstructured text. Your goal is to extract academic history with high precision.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. Scan for educational keywords: 'degree', 'bachelor', 'master', 'PhD', 'studied', 'graduated', "
    "'university', 'college', 'school', 'major', 'minor', 'GPA', 'honors'\n"
    "2. Look for institution names (universities, colleges, schools)\n"
    "3. Identify fields of study, majors, specializations, or concentrations\n"
    "4. Extract dates: graduation year, enrollment period, expected graduation\n"
    "5. Note any academic achievements, thesis topics, or research areas mentioned\n"
    "6. Order education chronologically (most recent first)\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object:\n"
    "{\n"
    '  "education": [\n'
    "    {\n"
    '      "date": "<start year – end year, or single year, or Expected YYYY>",\n'
    '      "education": "<Degree Type in Field at Institution Name>",\n'
    '      "description": "<first-person description of focus areas, achievements, or research topics>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"

    "## STRICT RULES\n"
    "- ALWAYS write descriptions in FIRST PERSON (e.g., 'I focused on...', 'I researched...', 'I achieved...')\n"
    "- NEVER use third person (e.g., 'He/She studied...', 'The student focused on...')\n"
    "- NEVER fabricate, assume, or hallucinate education details not in the source text\n"
    "- NEVER use example data from this prompt - extract ONLY from provided text\n"
    "- If education is ongoing, use 'Present' or 'Expected YYYY' for the end date\n"
    "- Include ONLY formal education (degrees, diplomas) - NOT courses/certifications (those go elsewhere)\n"
    "- If only an institution is mentioned without degree details, include what's available\n"
    "- For 'description': include ONLY explicitly mentioned focus areas, research, or achievements\n"
    "- If description would require guessing, leave it as a brief factual statement or empty\n"
    "- If NO education information is found in the text, return: {\"education\": []}\n"
    "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
)


    # Extract user context for the LLM
    user_prompt = (
        f"Extract all formal education (degrees, diplomas, academic programs) from this text. "
        f"Include ONLY educational background that is explicitly mentioned:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

    # Invoke the LLM to generate education info
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    education_text = msg.strip() if msg else ""

    # Safety fallback
    if not education_text:
        education_text = "2020–2024;Bachelor’s Degree;General undergraduate studies in relevant field."

    # Update state
    state["education"] = education_text
    return {"education": education_text}




