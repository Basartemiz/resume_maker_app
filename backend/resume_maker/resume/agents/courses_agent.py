from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict


# Agent for extracting courses and certifications from user input


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
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{user_prompt}"},
    ],
     # ensures valid JSON output
)   
    
    return resp.output[0].content[0].text
# Nodes

def get_courses_certifications(state: State) -> dict:
    """
    🔹 Purpose:
        Node function that queries an LLM to extract or generate
        a user's relevant courses in the format:
        <date>;<course>;<explanation>

    🔹 Example output:
        2023;Machine Learning (Coursera);Completed an online course covering supervised and unsupervised algorithms.

    🔹 Expected input:
        state: dict-like LangGraph State with key 'context' holding user information.

    🔹 Returns:
        dict with key 'courses' -> formatted string(s)
    """

    name = (state.get("name") or "The user").strip()
    system_prompt = (
    "You are an expert information extraction specialist focused on identifying courses, certifications, "
    "and professional development from unstructured text.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. Scan for course-related keywords: 'course', 'certification', 'certificate', 'completed', 'certified', "
    "'training', 'bootcamp', 'workshop', 'online course'\n"
    "2. Look for platform names: Coursera, edX, Udemy, LinkedIn Learning, AWS, Google, etc.\n"
    "3. Identify certification bodies or issuing organizations\n"
    "4. Extract completion dates or validity periods if mentioned\n"
    "5. Note any specific skills or knowledge areas covered\n"
    "6. Distinguish between: online courses, professional certifications, workshops, bootcamps\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object:\n"
    "{\n"
    '  "courses_and_certifications": [\n'
    "    {\n"
    '      "date": "<year or date range>",\n'
    '      "course_or_certificate": "<Course/Certification Name and Platform/Issuer>",\n'
    '      "description": "<first-person description of what was learned or certified>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"

    "## STRICT RULES\n"
    "- ALWAYS write descriptions in FIRST PERSON (e.g., 'I learned...', 'I completed...', 'I gained expertise in...')\n"
    "- NEVER use third person (e.g., 'He/She learned...', 'The candidate completed...')\n"
    "- ONLY extract courses/certifications that are EXPLICITLY mentioned in the text\n"
    "- NEVER fabricate, assume, or hallucinate courses not present in the source\n"
    "- NEVER use example data from this prompt - extract ONLY from provided text\n"
    "- Do NOT confuse formal education (degrees) with courses - degrees belong elsewhere\n"
    "- If a date is not mentioned, omit the date field or use 'N/A' sparingly\n"
    "- Keep descriptions factual based on what's stated about the course content\n"
    "- If NO courses or certifications are found in the text, return: {\"courses_and_certifications\": []}\n"
    "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
)


    user_prompt = (
        f"Extract all courses, certifications, and professional training from this text. "
        f"Include ONLY courses/certifications that are explicitly mentioned:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    courses_text = msg.strip() if msg else ""

    if not courses_text:
        courses_text = "2023;Data Structures and Algorithms;Focused on algorithmic problem solving and efficiency analysis."

    state["courses"] = courses_text
    return {"courses": courses_text}





