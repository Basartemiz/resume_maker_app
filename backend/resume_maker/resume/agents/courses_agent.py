from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict


#some variables


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
    "You are an assistant specialized in summarizing relevant academic or professional courses or certificates. "
    "Given the available user information, identify and return their notable completed or ongoing courses or certifications "
    "as a JSON object ONLY (no markdown, no commentary, no extra text) with this structure:\n\n"
    "{\n"
    '  "courses_and_certifications": [\n'
    "    {\n"
    '      "date": "2023",\n'
    '      "course_or_certificate": "Machine Learning on Coursera",\n'
    '      "description": "Completed a foundational course on supervised and unsupervised learning techniques."\n'
    "    },\n"
    "    {\n"
    '      "date": "2022",\n'
    '      "course_or_certificate": "Advanced Python Programming on edX",\n'
    '      "description": "Enhanced Python development skills for scalable software applications."\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object and nothing else.\n"
    "- The root key must be 'courses_and_certifications'.\n"
    "- Each entry must include 'date', 'course_or_certificate', and 'description'.\n"
    "- Use realistic dates (e.g., '2023', '2023–2024').\n"
    "- do not use example course names or descriptions.\n"
    "- Each description must be one concise, factual sentence.\n"
    "- Do not include markdown, commentary, or placeholders like 'unknown' or 'N/A'.\n"
    "- If no courses or certifications are mentioned, return:\n"
    "{ \"courses_and_certifications\": [{ \"message\": \"No relevant courses or certifications could be generated.\" }] }"
)


    user_prompt = f"Here is the information you have: {state.get('context', '')}"

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    courses_text = msg.strip() if msg else ""

    if not courses_text:
        courses_text = "2023;Data Structures and Algorithms;Focused on algorithmic problem solving and efficiency analysis."

    state["courses"] = courses_text
    return {"courses": courses_text}





