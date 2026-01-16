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
    "You are an assistant specialized in writing professional reference lists.\n"
    "Task: Using ONLY the references explicitly provided in the user-supplied data, return a JSON object (and nothing else) with this exact shape:\n\n"
    "{\n"
    '  "references": [\n'
    "    {\n"
    '      "name": "Mr example",\n'
    '      "relationship_or_title": "Academic Advisor, Boğaziçi University",\n'
    '      "contact": "mr.example@bogazici.edu.tr"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Hard Rules:\n"
    "- Output MUST be valid JSON. No prose, no markdown, no extra keys anywhere.\n"
    "- The root key MUST be exactly \"references\".\n"
    "- Populate the array ONLY with references that are explicitly present in the provided user data.\n"
    "- Do NOT infer, fabricate, rename, expand, or synthesize any reference. If a field is missing, do NOT guess it.\n"
    "- Each emitted reference MUST include all three fields: \"name\", \"relationship_or_title\", and \"contact\".\n"
    "- \"contact\" MUST be taken directly from the user data and be in realistic email or phone format. Do NOT invent contacts.\n"
    "- Preserve the original order of references as given in the user data. Do NOT add extra objects.\n"
    "- If zero valid references are present (or none have all required fields), return exactly:\n"
    "{ \"references\": [{ \"message\": \"No references are available.\" }] }\n"
    "- If both academic and professional references exist in the provided data, include at least one of each; otherwise include only what is present.\n"
    "- The number of references in the output MUST NOT exceed the number of valid references provided by the user.\n"
)



    # Extract relevant context
    user_prompt = f"Here is the information you have about {name}: {state.get('context', '')}"

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




