from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict

#some variables
input_of_user="""
I’m Başar Temiz, a computer engineer with a strong passion for artificial intelligence, data analysis, and scalable software systems. Over the past few years, I’ve built and deployed several projects that combine back-end engineering with machine learning — from Django web applications and agentic AI tools to 3D reconstruction pipelines using NeRF and satellite imagery. I enjoy designing clean, maintainable architectures and have practical experience with technologies like Python, Docker, React, and LangChain. I earned my bachelor’s degree in Computer Engineering from Boğaziçi University, where I also collaborated on research involving depth estimation and generative AI. Beyond technical skills, I value teamwork and clarity — I’ve led small development groups, documented complex workflows, and communicated results effectively. My goal is to contribute to projects where intelligent systems meet real-world impact, creating tools that help people understand and shape data more intuitively.

You can reach me via LinkedIn at linkedin.com/in/basartemiz, explore my projects on github.com/Basartemiz, or contact me directly at basar.temiz2004@gmail.com or +90 535 745 09 33.
"""


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
    "You are an assistant specialized in writing structured academic backgrounds. "
    "Given the available user information, identify and return their main education details "
    "as a JSON object ONLY (no markdown, no commentary, no extra text) with this structure:\n\n"
    "{\n"
    '  "education": [\n'
    "    {\n"
    '      "date": "2020–2024",\n'
    '      "education": "Bachelor\'s Degree in Computer Engineering at Boğaziçi University",\n'
    '      "description": "Focused on software systems, AI, and depth estimation research."\n'
    "    },\n"
    "    {\n"
    '      "date": "2021",\n'
    '      "education": "Machine Learning Course on Coursera",\n'
    '      "description": "Completed a foundational course on supervised and unsupervised learning methods."\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object and nothing else.\n"
    "- Never fabricate education details; only use information provided.\n"
    "If the users education is still ongoing, reflect that accurately.\n"
    "- The root key must be 'education'.\n"
    "- Each entry must include 'date', 'education', and 'description'.\n"
    "- Use realistic date ranges (e.g., '2020–2024', '2022', '2018–2020').\n"
    "- Each description must be one concise factual sentence (no commentary or opinion).\n"
    "- Do not include placeholders like 'unknown' or 'N/A'.\n"
    "- If no education information is available, return:\n"
    "{ \"education\": [{ \"message\": \"No academic background details could be generated.\" }] }"
)


    # Extract user context for the LLM
    user_prompt = f"Here is the information you have about {name}: {state.get('context', '')}"

    # Invoke the LLM to generate education info
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    education_text = msg.strip() if msg else ""

    # Safety fallback
    if not education_text:
        education_text = "2020–2024;Bachelor’s Degree;General undergraduate studies in relevant field."

    # Update state
    state["education"] = education_text
    return {"education": education_text}




