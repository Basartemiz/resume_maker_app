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
    model="gpt-4o-mini",
    input=[
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": f"{user_prompt}"},
    ],
     # ensures valid JSON output
)   
    
    return resp.output[0].content[0].text
# Nodes
def get_skills(state: State) -> dict:
    """
    🔹 Purpose:
        Node function that queries an LLM to extract or generate
        a user's key skills in the format:
        <category>;<skill(s)>;<explanation>

    🔹 Example output:
        Technical;Python, Django, Docker;Experienced in backend development and deployment pipelines.
        Soft;Leadership, Communication;Strong collaboration and team coordination skills.

    🔹 Expected input:
        state: dict-like LangGraph State with key 'context' holding user information.

    🔹 Returns:
        dict with key 'skills' -> formatted string(s)
    """

    name = (state.get("name") or "The user").strip()

    # Define a structured and concise system prompt
    system_prompt = (
    "You are an assistant specialized in summarizing professional skill sets. "
    "Given the available user information, identify the user's main skills and return them "
    "as a JSON object in the following format:\n\n"
    "{\n"
    '  "skills": [\n'
    "    {\n"
    '      "category": "Technical",\n'
    '      "skills": ["Python", "Docker", "React"],\n'
    '      "explanation": "Proficient in backend and full-stack software development."\n'
    "    },\n"
    "    {\n"
    '      "category": "Soft",\n'
    '      "skills": ["Communication", "Teamwork"],\n'
    '      "explanation": "Strong collaboration and communication skills gained from internships and team projects."\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object.\n"
    "- The root key must be 'skills'.\n"
    "- Each skill group must include 'category', 'skills', and 'explanation'.\n"
    "- Group similar skills together in one list under 'skills'.\n"
    "- Categories can include 'Technical', 'Soft', 'Analytical', 'Creative', etc.\n"
    "- Keep explanations factual and concise (1 sentence each).\n"
    "- Do not include markdown, commentary, or placeholders like 'unknown'."
)

    # Extract user context for the LLM
    user_prompt = f"Here is the information you have about {name}: {state.get('context', '')}"

    # Call your LLM wrapper
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    skills_text = msg.strip() if msg else ""

    # Safety fallback
    if not skills_text:
        skills_text = (
            "Technical;Python, Django, Docker;Experienced in backend development and API design.\n"
            "Soft;Teamwork, Communication;Effective collaborator in academic and project settings."
        )

    # Update state
    state["skills"] = skills_text
    return {"skills": skills_text}






