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



def get_profile(state: State) -> dict:
    """
    🔹 Purpose:
        Retrieve or generate professional contact information for a person.
        Expected to include LinkedIn, GitHub, email, and phone — if available.

    🔹 Expected input:
        state["name"] : str  → person's full name

    🔹 Returns:
        dict -> {"personal_info": <string>} containing cleanly formatted info.
    """

   

    # Clear system instruction for controlled and safe output
    system_prompt = (
    "You are a professional assistant that writes concise, factual personal summaries "
    "for resumes, portfolio introductions, or short biography sections. "
    "Your goal is to produce a brief 'Information' section describing who the person is professionally. "
    "Always write in clean, human-readable text — no markdown, no code, no bullet lists.\n\n"
    "Rules:\n"
    "- Keep it 2–4 sentences long.\n"
    "- Focus on the person’s profession, expertise areas, and goals.\n"
    "- Use a neutral, formal tone suitable for a professional profile.\n"
    "- Do not include contact details or links (only descriptive information about the person).\n"
    "- Do not guess or fabricate data that is not provided.\n\n"
    "Example format:\n"
    "Başar Temiz is a computer engineer specializing in artificial intelligence, data analysis, "
    "and scalable software systems. He has experience building end-to-end applications using "
    "Python, Docker, and React. His work focuses on developing intelligent systems that help users "
    "interact with data more effectively."
)

    # User prompt that guides structure and ensures clarity
    user_prompt = (
    f"Here is the information you have: {state['context']}"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)

    personal_info = msg

    # Safety: basic cleanup
    personal_info = personal_info.replace("N/A", "").replace("Unknown", "").strip()
    if not personal_info:
        personal_info = f"No public personal information available for {name}."

    return {"profile": personal_info}



