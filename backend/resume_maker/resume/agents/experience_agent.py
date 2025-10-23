from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict


#some variables
input_of_user="""
I’m Başar Temiz, a computer engineer with a strong passion for artificial intelligence, data analysis, and scalable software systems. Over the past few years, I’ve built and deployed several projects that combine back-end engineering with machine learning — from Django web applications and agentic AI tools to 3D reconstruction pipelines using NeRF and satellite imagery. I enjoy designing clean, maintainable architectures and have practical experience with technologies like Python, Docker, React, and LangChain. I earned my bachelor’s degree in Computer Engineering from Boğaziçi University, where I also collaborated on research involving depth estimation and generative AI. Beyond technical skills, I value teamwork and clarity — I’ve led small development groups, documented complex workflows, and communicated results effectively. My goal is to contribute to projects where intelligent systems meet real-world impact, creating tools that help people understand and shape data more intuitively.

You can reach me via LinkedIn at linkedin.com/in/basartemiz, explore my projects on github.com/Basartemiz, or contact me directly at basar.temiz2004@gmail.com or +90 535 745 09 33. I also worked at Baykar as a Software Engineer Intern where I contributed to the development of UAV software systems and collaborated with cross-functional teams to enhance system performance.
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
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{user_prompt}"},
    ],
     # ensures valid JSON output
)   
    
    return resp.output[0].content[0].text
# Nodes

def get_experience(state: State) -> dict:
    """
    🔹 Purpose:
        Node function that queries an LLM to extract or generate
        a user's work or internship experience in the format:
        <date>;<position/company>;<explanation>

    🔹 Example output:
        2023–Present;AI Intern, Akbank;Developing credit-risk analysis models and automating data pipelines.

    🔹 Expected input:
        state: dict-like LangGraph State with key 'context' holding user information.

    🔹 Returns:
        dict with key 'experience' -> formatted string(s)
    """

    name = (state.get("name") or "The user").strip()

    # Define system prompt to enforce structured, consistent output
    system_prompt = (
    "You are an assistant specialized in summarizing professional experience. "
    "Given the available user information, identify and return their main work or internship experiences "
    "as a JSON object ONLY (no prose, no markdown, no extra text) with this structure:\n\n"
    "{\n"
    '  "experience": [\n'
    "    {\n"
    '      "date": "2023–Present",\n'
    '      "position_or_company": "Software Engineer Intern at Baykar",\n'
    '      "description": "Contributed to UAV software development and collaborated with cross-functional teams to enhance performance."\n'
    "    },\n"
    "    {\n"
    '      "date": "2021–2022",\n'
    '      "position_or_company": "Research Assistant at Boğaziçi University",\n'
    '      "description": "Assisted in depth estimation research involving neural rendering and 3D reconstruction."\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object and nothing else.\n"
    "- The root key must be 'experience'.\n"
    "- Each experience must include 'date', 'position_or_company', and 'description'.\n"
    "- Use realistic date ranges (e.g., '2023–Present', '2021–2023').\n"
    "- Each description must be factual, concise, and one sentence long.\n"
    "- Do not use bullet points, markdown, or commentary.\n"
    "- Do not include placeholders like 'unknown' or 'N/A'.\n"
    "- If no experiences exist, return:\n"
    "{ \"experience\": [{ \"message\": \"No professional experience details could be generated.\" }] }"
)


    # Build the user prompt dynamically from context
    user_prompt = f"Here is the information you have about {name}: {state.get('context', '')}"

    # Call your LLM wrapper
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    experience_text = msg.strip() if msg else ""

    # Safety fallback
    if not experience_text:
        experience_text = "No professional experience details could be generated."

    # Update state
    state["experience"] = experience_text
    return {"experience": experience_text}




