from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, START, END
from openai import OpenAI
from typing_extensions import TypedDict

# Agent for extracting skills from user input



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
    "You are an expert information extraction specialist focused on identifying professional skills "
    "from unstructured text. Your goal is to extract and categorize skills with high precision.\n\n"

    "## EXTRACTION PROCESS\n"
    "1. Scan for explicit skill mentions: technologies, programming languages, frameworks, tools\n"
    "2. Identify implied skills from: project descriptions, job responsibilities, achievements\n"
    "3. Look for soft skills indicators: 'led', 'collaborated', 'communicated', 'managed', 'organized'\n"
    "4. Recognize domain expertise: data analysis, machine learning, web development, etc.\n"
    "5. Note proficiency indicators if mentioned: 'expert in', 'proficient with', 'familiar with'\n"
    "6. Group related skills into logical categories\n\n"

    "## OUTPUT FORMAT\n"
    "Return ONLY a valid JSON object:\n"
    "{\n"
    '  "skills": [\n'
    "    {\n"
    '      "category": "<Technical|Soft|Analytical|Domain|Tools|Languages>",\n'
    '      "skills": ["<skill1>", "<skill2>", ...],\n'
    '      "explanation": "<first-person context on how these skills were demonstrated or acquired>"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"

    "## SKILL CATEGORIES\n"
    "- Technical: Programming languages, frameworks, libraries (Python, React, Django, etc.)\n"
    "- Tools: Software tools, platforms, DevOps (Docker, Git, AWS, etc.)\n"
    "- Analytical: Data analysis, problem-solving, research methods\n"
    "- Soft: Communication, leadership, teamwork, project management\n"
    "- Domain: Industry-specific expertise (AI/ML, finance, healthcare, etc.)\n"
    "- Languages: Spoken/written languages if mentioned\n\n"

    "## STRICT RULES\n"
    "- ALWAYS write explanations in FIRST PERSON (e.g., 'I developed...', 'I have experience with...', 'I demonstrated...')\n"
    "- NEVER use third person (e.g., 'He/She has skills in...', 'The candidate knows...')\n"
    "- ONLY extract skills that are explicitly mentioned OR clearly demonstrated through described work\n"
    "- NEVER invent skills not supported by the text\n"
    "- NEVER use example skills from this prompt - extract ONLY from provided text\n"
    "- Group skills logically - don't create a category with only one skill unless necessary\n"
    "- Keep explanations tied to evidence from the text\n"
    "- If NO skills can be identified from the text, return: {\"skills\": []}\n"
    "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
)

    # Extract user context for the LLM
    user_prompt = (
        f"Extract and categorize all professional skills from this text. "
        f"Include both explicitly mentioned skills and skills clearly demonstrated through described work:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

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






