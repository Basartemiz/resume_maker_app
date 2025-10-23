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
    "You are an assistant specialized in writing professional reference lists. "
    "Given the available user information, identify and return the user's main references "
    "as a JSON object ONLY (no prose, no markdown, no extra text) with this exact shape:\n\n"
    "{\n"
    '  "references": [\n'
    "    {\n"
    '      "name": "Dr. Ayşe Yılmaz",\n'
    '      "relationship_or_title": "Academic Advisor, Boğaziçi University",\n'
    '      "contact": "ayse.yilmaz@bogazici.edu.tr"\n'
    "    },\n"
    "    {\n"
    '      "name": "Mr. Mehmet Kara",\n'
    '      "relationship_or_title": "Software Engineering Supervisor, Baykar",\n'
    '      "contact": "mehmet.kara@baykar.com"\n'
    "    }\n"
    "  ]\n"
    "}\n\n"
    "Rules:\n"
    "- Always return a valid JSON object and nothing else.\n"
    "- The root key must be 'references'.\n"
    "- Each reference must contain 'name', 'relationship_or_title', and 'contact'.\n"
    "- Contact info must be a realistic email or phone number format.\n"
    "- Never fabricate or guess real people's names or contact details.\n"
    "- If no references are available, return:\n"
    "{ \"references\": [{ \"message\": \"No references are available.\" }] }\n"
    "- Include at least one academic and one professional reference if possible.\n"
    "- Use realistic, professional-sounding names and positions (fictional if needed, but plausible).\n"
    "- Keep formatting strict JSON with double quotes and proper commas."
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




