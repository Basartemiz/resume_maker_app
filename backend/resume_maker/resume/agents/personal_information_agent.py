from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict

# Agent for extracting personal information from user input



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
    "You are an expert information extraction specialist. Your task is to carefully analyze unstructured text "
    "and extract personal and professional identity information with high precision.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. First, scan the entire text for explicit mentions of: names, job titles, contact info, social profiles\n"
    "2. Identify contextual clues that indicate professional focus (e.g., 'I work on...', 'specializing in...')\n"
    "3. Only extract information that is DIRECTLY STATED or STRONGLY IMPLIED by the text\n"
    "4. If information is ambiguous or missing, OMIT that field entirely from the output\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object with this structure (omit any field without clear data):\n"
    "{\n"
    '  "profile": {\n'
    '    "name": "<first name>",\n'
    '    "surname": "<last name>",\n'
    '    "position": "<professional title>",\n'
    '    "description": "<one sentence about professional focus>",\n'
    '    "phone_number": "<phone with country code if present>",\n'
    '    "accounts": {\n'
    '      "email": "<email address>",\n'
    '      "github": "<github profile URL or username>",\n'
    '      "linkedin": "<linkedin profile URL or username>"\n'
    '    }\n'
    "  }\n"
    "}\n\n"

    "## STRICT RULES\n"
    "- NEVER invent, guess, or hallucinate any information not present in the source text\n"
    "- NEVER use placeholder values like 'N/A', 'Unknown', 'TBD', or example data\n"
    "- If a name appears as a full name, split it into 'name' and 'surname' appropriately\n"
    "- For 'position': derive from stated job title, degree field, or professional self-description\n"
    "- For 'description': synthesize ONLY from explicitly mentioned skills, expertise, or goals\n"
    "- Preserve original capitalization for names; use title case for positions\n"
    "- Include only accounts/contact info that are explicitly provided in the text\n"
    "- If the text contains no extractable personal information, return: {\"profile\": {}}\n"
    "- Output must be valid JSON with no markdown formatting, code blocks, or commentary\n"
)




    user_prompt = (
    f"Analyze the following text and extract personal/professional identity information. "
    f"Extract ONLY what is explicitly stated or clearly implied:\n\n"
    f"---TEXT START---\n{state['context']}\n---TEXT END---"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    profile_text = msg

    state["personal_info"] = profile_text

    # Safety: ensure output isn't empty
    if not profile_text:
        profile_text = f"A concise professional summary for the user could not be generated."

    return {"personal_info": profile_text}




