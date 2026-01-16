from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict

# Agent for extracting references from user input



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
def get_references(state: State) -> dict:
    """
    🔹 Purpose:
        Node function that queries an LLM to extract or generate
        a user's professional or academic references in the format:
        <name>;<relationship/title>;<contact information>


    🔹 Expected input:
        state: dict-like LangGraph State with key 'context' holding user information.

    🔹 Returns:
        dict with key 'references' -> formatted string(s)
    """

    name = (state.get("name") or "The user").strip()

    # Define structured and explicit system prompt
    system_prompt = (
    "You are an expert information extraction specialist focused on identifying professional and academic references "
    "from unstructured text. This is a HIGHLY SENSITIVE extraction task - references must NEVER be fabricated.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. Scan for reference-related keywords: 'reference', 'referee', 'recommend', 'contact', 'supervisor', "
    "'manager', 'professor', 'advisor', 'mentor'\n"
    "2. Look for explicit statements like: 'references available', 'contact X for reference', "
    "'my supervisor was Y'\n"
    "3. Identify reference names along with their titles/positions and organizations\n"
    "4. Extract contact information (email, phone) ONLY if explicitly provided\n"
    "5. Note the relationship context (academic advisor, former manager, etc.)\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object:\n"
    "{\n"
    '  "references": [\n'
    "    {\n"
    '      "name": "<Full Name>",\n'
    '      "relationship_or_title": "<Title/Position and Organization>",\n'
    '      "contact": "<email or phone if explicitly provided>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"

    "## CRITICAL RULES (MUST FOLLOW)\n"
    "- This extraction has ZERO tolerance for hallucination\n"
    "- ONLY extract references that are EXPLICITLY stated as references in the text\n"
    "- NEVER infer that someone is a reference just because they're mentioned (e.g., a coworker mentioned "
    "in a project description is NOT automatically a reference)\n"
    "- NEVER fabricate, guess, or invent ANY reference information\n"
    "- NEVER use example data from this prompt - extract ONLY from provided text\n"
    "- Contact information MUST be taken verbatim from the text - NEVER generate emails/phones\n"
    "- If contact info is missing for a reference, include the reference with contact as empty string\n"
    "- Preserve exact names and titles as written in the source text\n"
    "- If NO explicit references are found in the text, return: {\"references\": []}\n"
    "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
)



    # Extract relevant context
    user_prompt = (
        f"Extract ONLY explicitly stated professional or academic references from this text. "
        f"Do NOT treat mentioned colleagues, supervisors, or professors as references unless they are "
        f"EXPLICITLY identified as references:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

    # Call the LLM
    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    references_text = msg.strip() if msg else ""

    # Safety fallback if the model fails or returns empty
    if not references_text:
        references_text = (
            "No professional references could be generated."
        )

    # Update the state
    state["references"] = references_text
    return {"references": references_text}




