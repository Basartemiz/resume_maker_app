from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict





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
    "You are an expert professional summary writer. Your task is to synthesize information from text "
    "into a compelling first-person professional profile summary.\n\n"

    "## SYNTHESIS PROCESS\n"
    "1. Identify the person's primary profession or field\n"
    "2. Extract key expertise areas and specializations mentioned\n"
    "3. Note significant achievements, projects, or experience highlights\n"
    "4. Identify stated career goals or professional aspirations\n"
    "5. Synthesize into a cohesive narrative that flows naturally\n\n"

    "## OUTPUT FORMAT\n"
    "Write a 2-4 sentence professional summary in FIRST PERSON (using 'I', 'my', 'me').\n"
    "The summary should read naturally as a professional introduction.\n\n"

    "## STRICT RULES\n"
    "- ALWAYS write in first person (I am..., I specialize in..., My experience includes...)\n"
    "- Include ONLY information that is explicitly stated or clearly implied in the source text\n"
    "- NEVER fabricate achievements, skills, or experiences not mentioned\n"
    "- NEVER include contact information, links, or social media handles\n"
    "- NEVER use placeholder text or generic filler content\n"
    "- Keep tone professional, confident, and formal\n"
    "- Focus on: profession, expertise, key achievements, and goals (if mentioned)\n"
    "- Output plain text only - no markdown, bullet points, or formatting\n"
    "- If the text contains insufficient information for a meaningful summary, "
    "write a brief, factual statement based only on what IS available\n"
)

    # User prompt that guides structure and ensures clarity
    user_prompt = (
        f"Write a first-person professional summary (2-4 sentences) based on the following text. "
        f"Use ONLY information that is explicitly stated:\n\n"
        f"---TEXT START---\n{state['context']}\n---TEXT END---"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)

    personal_info = msg

    # Safety: basic cleanup
    personal_info = personal_info.replace("N/A", "").replace("Unknown", "").strip()
    if not personal_info:
        personal_info = f"No public personal information available for this user."

    return {"profile": personal_info}



