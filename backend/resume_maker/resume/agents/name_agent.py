from dotenv import load_dotenv
import os
from openai import OpenAI
from typing_extensions import TypedDict


# Agent for extracting name from user input

class State(TypedDict):
    context: str
    name: str


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
    )
    return resp.output[0].content[0].text


def get_name(state: State) -> dict:
    """
    Purpose:
        Extract the person's full name from unstructured text.
        This agent is specifically designed to identify and extract
        names with high accuracy.

    Expected input:
        state: dict-like State with key 'context' holding user information.

    Returns:
        dict with key 'name' -> the extracted full name as a string
    """

    system_prompt = (
        "You are an expert name extraction specialist. Your ONLY task is to identify and extract "
        "a person's full name from unstructured text with high precision.\n\n"

        "## EXTRACTION PROCESS\n"
        "1. Look for explicit name introductions: 'I am', 'My name is', 'I'm', 'This is'\n"
        "2. Look for name patterns at the beginning of text or after greetings\n"
        "3. Identify first name and last name (surname) components\n"
        "4. Check for middle names if present\n"
        "5. Handle various cultural name formats (Western, Asian, etc.)\n\n"

        "## OUTPUT FORMAT\n"
        "Return ONLY a valid JSON object:\n"
        "{\n"
        '  "name": "<Full Name>"\n'
        "}\n\n"

        "## STRICT RULES\n"
        "- Extract ONLY the person's name - nothing else\n"
        "- Return the full name as a single string (e.g., 'John Smith', 'Maria Garcia Lopez')\n"
        "- Preserve original capitalization and spelling of the name\n"
        "- NEVER fabricate or guess a name that is not in the text\n"
        "- NEVER include titles (Dr., Mr., Mrs., etc.) unless they are part of how the person identifies\n"
        "- NEVER include job titles, positions, or other descriptors\n"
        "- If multiple names are mentioned, extract the PRIMARY person's name (usually the author/subject)\n"
        "- If NO name can be identified, return: {\"name\": \"\"}\n"
        "- Output must be valid JSON with no markdown, code blocks, or extra commentary\n"
    )

    user_prompt = (
        f"Extract the person's full name from this text. "
        f"Return ONLY the name, nothing else:\n\n"
        f"---TEXT START---\n{state.get('context', '')}\n---TEXT END---"
    )

    msg = invoke(system_prompt=system_prompt, user_prompt=user_prompt)
    name_text = msg.strip() if msg else ""

    # Safety fallback
    if not name_text:
        name_text = '{"name": ""}'

    state["name"] = name_text
    return {"name": name_text}
