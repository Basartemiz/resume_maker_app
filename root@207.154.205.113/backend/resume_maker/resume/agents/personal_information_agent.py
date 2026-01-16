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


def get_personal_info(state: State) -> dict:
    
    # Build a detailed prompt for clarity and control
    system_prompt = (
    "You are an expert resume writer and professional biographer. "
    "Your task is to create concise, factual identity and professional summaries. "
    "Given the available user information, return a JSON object ONLY "
    "(no markdown, no commentary, no extra text) with this exact structure:\n\n"
    "{\n"
    '  "profile": {\n'
    '    "name": "Başar",\n'
    '    "surname": "Temiz",\n'
    '    "position": "Computer Engineer",\n'
    '    "description": "Computer engineer specializing in artificial intelligence, scalable software systems, and data-driven development.",\n'
    '    "phone_number": "+90 535 745 09 33",\n'
    '    "accounts": {\n'
    '      "email": "basar.temiz2004@gmail.com",\n'
    '      "github": "github.com/Basartemiz",\n'
    '      "linkedin": "linkedin.com/in/basartemiz"\n'
    '    }\n'
    "  }\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object and nothing else.\n"
    "- The root key must be 'profile'.\n"
    "- 'name' and 'surname' must contain proper capitalization.\n"
    "- 'position' must be a concise professional title (e.g., 'Software Engineer', 'Data Scientist').\n"
    "- 'description' must be one short, factual sentence describing the individual's professional focus.\n"
    "- 'phone_number' must include country code if available.\n"
    "- 'accounts' must include relevant verified fields such as email, GitHub, LinkedIn.\n"
    "- Keep tone formal, neutral, and resume-like.\n"
    "- Do not include placeholders such as 'unknown' or 'N/A'.\n"
)




    user_prompt = (
    f"Here is the information you have: {state['context']}"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    profile_text = msg

    state["personal_info"] = profile_text

    # Safety: ensure output isn't empty
    if not profile_text:
        profile_text = f"A concise professional summary for the user could not be generated."

    return {"personal_info": profile_text}




