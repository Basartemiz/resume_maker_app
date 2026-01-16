from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict


# Agent for extracting work experience from user input


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
    "You are an expert information extraction specialist focused on identifying professional work experience "
    "from unstructured text. Your goal is to extract employment history with high accuracy.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. Scan for keywords indicating employment: 'worked at', 'interned at', 'employed by', 'position at', "
    "'role as', 'joined', 'contributed to', company names, job titles\n"
    "2. Look for temporal markers: dates, years, 'currently', 'present', duration phrases\n"
    "3. Identify responsibilities, achievements, or project descriptions tied to each role\n"
    "4. Distinguish between: full-time employment, internships, freelance work, research positions\n"
    "5. Order experiences chronologically (most recent first) if dates are available\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object:\n"
    "{\n"
    '  "experience": [\n'
    "    {\n"
    '      "date": "<start year/date – end year/date or Present>",\n'
    '      "position_or_company": "<Job Title at Company Name>",\n'
    '      "description": "<concise first-person summary of responsibilities/achievements>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"

    "## STRICT RULES\n"
    "- ALWAYS write descriptions in FIRST PERSON (e.g., 'I developed...', 'I led...', 'I contributed to...')\n"
    "- NEVER use third person (e.g., 'He/She developed...', 'The candidate worked on...')\n"
    "- NEVER fabricate, infer, or hallucinate experiences not explicitly mentioned in the text\n"
    "- NEVER use example data from this prompt - extract ONLY from the provided text\n"
    "- If dates are vague (e.g., 'a few years ago'), use approximate descriptors or omit\n"
    "- If only a company is mentioned without dates, still include it with date as 'N/A' only if critical\n"
    "- Combine job title and company in 'position_or_company' field (e.g., 'Software Engineer at Google')\n"
    "- Keep descriptions factual - use only stated responsibilities, not assumed ones\n"
    "- If NO work experience is found in the text, return: {\"experience\": []}\n"
    "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
)


    # Build the user prompt dynamically from context
    user_prompt = (
        f"Extract all professional work experiences (jobs, internships, research positions) from this text. "
        f"Include ONLY experiences that are explicitly mentioned:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

    # Call your LLM wrapper
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    experience_text = msg.strip() if msg else ""

    # Safety fallback
    if not experience_text:
        experience_text = "No professional experience details could be generated."

    # Update state
    state["experience"] = experience_text
    return {"experience": experience_text}




