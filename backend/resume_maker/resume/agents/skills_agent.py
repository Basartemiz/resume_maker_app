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
    "- do not give information about the user if not available.\n"
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
            ""
        )

    # Update state
    state["skills"] = skills_text
    return {"skills": skills_text}






