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
    model="gpt-4o",
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
    "- 'name' and 'surname' must contain proper capitalization.\n",
    "- do not use examples or templates.\n"
    "- Never fabricate details; only use information provided.\n"
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




