from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from agents import (
    skills_agent, education_agent, 
    experience_agent, 
    references_agent, 
    personal_information_agent, profile_agent, 
    courses_agent)
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import TypedDict

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

#----------functions to make the output---------

class State(TypedDict):
    context:str
    skills:str
    education:str
    experience:str
    references:str
    personal_info:str
    profile:str

input_of_user="""
I’m Başar Temiz, a computer engineer with a strong passion for artificial intelligence, data analysis, and scalable software systems. Over the past few years, I’ve built and deployed several projects that combine back-end engineering with machine learning — from Django web applications and agentic AI tools to 3D reconstruction pipelines using NeRF and satellite imagery. I enjoy designing clean, maintainable architectures and have practical experience with technologies like Python, Docker, React, and LangChain. I earned my bachelor’s degree in Computer Engineering from Boğaziçi University, where I also collaborated on research involving depth estimation and generative AI. Beyond technical skills, I value teamwork and clarity — I’ve led small development groups, documented complex workflows, and communicated results effectively. My goal is to contribute to projects where intelligent systems meet real-world impact, creating tools that help people understand and shape data more intuitively.

You can reach me via LinkedIn at linkedin.com/in/basartemiz, explore my projects on github.com/Basartemiz, or contact me directly at basar.temiz2004@gmail.com or +90 535 745 09 33. I also worked at Baykar as a Software Engineer Intern where I contributed to the development of UAV software systems and collaborated with cross-functional teams to enhance system performance. I have completed several online courses including Machine Learning on Coursera and Advanced Python Programming on edX.
"""
def parse(input_of_user: str) -> dict:
    """
    🔹 Purpose:
        Main function to parse user input and generate a structured resume.

    🔹 Parameters:
        input_of_user: str - Raw user input containing personal and professional details.

    🔹 Returns:
        dict - Structured resume data including skills, education, experience, references, personal info, and profile.
    """

    # Initialize state with user input
    initial_state = {"context": input_of_user}

   
    # Build workflow
    workflow = StateGraph(State)

    # Add nodes to our workflow
    workflow.add_node("get_skills", skills_agent.get_skills)
    workflow.add_node("get_education", education_agent.get_education)
    workflow.add_node("get_experience", experience_agent.get_experience)
    workflow.add_node("get_references", references_agent.get_references)
    workflow.add_node("get_personal_info", personal_information_agent.get_personal_info)
    workflow.add_node("get_profile", profile_agent.get_profile)
    workflow.add_node("get_courses", courses_agent.get_courses_certifications)

    # Add edges to connect nodes
    workflow.add_edge(START, "get_personal_info")
    workflow.add_edge("get_personal_info", "get_profile")
    workflow.add_edge("get_profile", "get_education")
    workflow.add_edge("get_education", "get_experience")
    workflow.add_edge("get_experience", "get_courses")
    workflow.add_edge("get_courses", "get_skills")
    workflow.add_edge("get_skills", "get_references")
    workflow.add_edge("get_references", END)

    chain=workflow.compile()

    state=chain.invoke({"context":input_of_user})
    


    return state

#----------functions to make the output---------
# render_from_raw_dict.py



raw_dict = {'context': '\nI’m Başar Temiz, a computer engineer with a strong passion for artificial intelligence, data analysis, and scalable software systems. Over the past few years, I’ve built and deployed several projects that combine back-end engineering with machine learning — from Django web applications and agentic AI tools to 3D reconstruction pipelines using NeRF and satellite imagery. I enjoy designing clean, maintainable architectures and have practical experience with technologies like Python, Docker, React, and LangChain. I earned my bachelor’s degree in Computer Engineering from Boğaziçi University, where I also collaborated on research involving depth estimation and generative AI. Beyond technical skills, I value teamwork and clarity — I’ve led small development groups, documented complex workflows, and communicated results effectively. My goal is to contribute to projects where intelligent systems meet real-world impact, creating tools that help people understand and shape data more intuitively.\n\nYou can reach me via LinkedIn at linkedin.com/in/basartemiz, explore my projects on github.com/Basartemiz, or contact me directly at basar.temiz2004@gmail.com or +90 535 745 09 33. I also worked at Baykar as a Software Engineer Intern where I contributed to the development of UAV software systems and collaborated with cross-functional teams to enhance system performance. I have completed several online courses including Machine Learning on Coursera and Advanced Python Programming on edX.\n', 'skills': '{\n  "skills": [\n    {\n      "category": "Technical",\n      "skills": ["Python", "Docker", "React", "Django", "LangChain", "Machine Learning"],\n      "explanation": "Proficient in developing scalable software systems and implementing machine learning solutions."\n    },\n    {\n      "category": "Analytical",\n      "skills": ["Data Analysis", "Depth Estimation", "Generative AI"],\n      "explanation": "Experienced in analyzing data and developing AI tools for real-world applications."\n    },\n    {\n      "category": "Soft",\n      "skills": ["Teamwork", "Communication"],\n      "explanation": "Strong collaboration and communication skills developed through internships and project leadership."\n    },\n    {\n      "category": "Creative",\n      "skills": ["System Architecture Design"],\n      "explanation": "Skilled in designing clean and maintainable software architectures."\n    }\n  ]\n}', 'education': '{\n  "education": [\n    {\n      "date": "2020–2024",\n      "education": "Bachelor\'s Degree in Computer Engineering at Boğaziçi University",\n      "description": "Collaborated on research involving depth estimation and generative AI."\n    },\n    {\n      "date": "2021",\n      "education": "Machine Learning Course on Coursera",\n      "description": "Completed a foundational course on supervised and unsupervised learning methods."\n    },\n    {\n      "date": "2022",\n      "education": "Advanced Python Programming on edX",\n      "description": "Completed a course focusing on advanced concepts in Python programming."\n    }\n  ]\n}', 'experience': '{\n  "experience": [\n    {\n      "date": "2023–Present",\n      "position_or_company": "Software Engineer Intern at Baykar",\n      "description": "Contributed to the development of UAV software systems and collaborated with cross-functional teams to enhance system performance."\n    },\n    {\n      "date": "2021–2022",\n      "position_or_company": "Research Assistant at Boğaziçi University",\n      "description": "Assisted in research involving depth estimation and generative AI."\n    }\n  ]\n}', 'references': '{\n  "references": [\n    {\n      "name": "Dr. Ayşe Yılmaz",\n      "relationship_or_title": "Academic Advisor, Boğaziçi University",\n      "contact": "ayse.yilmaz@bogazici.edu.tr"\n    },\n    {\n      "name": "Mr. Mehmet Kara",\n      "relationship_or_title": "Software Engineering Supervisor, Baykar",\n      "contact": "mehmet.kara@baykar.com"\n    }\n  ]\n}', 'personal_info': '{\n  "profile": {\n    "name": "Başar",\n    "surname": "Temiz",\n    "position": "Computer Engineer",\n    "description": "Computer engineer specializing in artificial intelligence, scalable software systems, and data-driven development.",\n    "phone_number": "+90 535 745 09 33",\n    "accounts": {\n      "email": "basar.temiz2004@gmail.com",\n      "github": "github.com/Basartemiz",\n      "linkedin": "linkedin.com/in/basartemiz"\n    }\n  }\n}', 'profile': 'Başar Temiz is a computer engineer with expertise in artificial intelligence, data analysis, and scalable software systems. He has developed a range of projects that integrate back-end engineering with machine learning, including Django applications and tools for 3D reconstruction utilizing NeRF and satellite imagery. With a strong educational foundation from Boğaziçi University and practical experience in technologies such as Python, Docker, and React, Başar aims to create impactful solutions that enhance user interaction with data while valuing teamwork and clear communication.'}

# ===== 2) Helpers =====
def _loads(maybe_json: Any) -> Any:
    if isinstance(maybe_json, str):
        s = maybe_json.strip()
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except Exception:
                return maybe_json
    return maybe_json

def _build_contacts(pi: Dict[str, Any]) -> Dict[str, Optional[str]]:
    prof = (pi or {}).get("profile") or {}
    acc = prof.get("accounts") or {}
    return {
        "email": acc.get("email"),
        "phone": prof.get("phone_number"),
        "github": acc.get("github"),
        "linkedin": acc.get("linkedin"),
        "location": None,
    }

def _derive_highest_degree(edu_list: List[Dict[str, Any]]) -> Optional[str]:
    if not edu_list: return None
    for it in edu_list:
        text = f"{it.get('education','')} {it.get('description','')}".lower()
        if any(k in text for k in ("bachelor", "master", "phd", "degree")):
            return it.get("education")
    return edu_list[0].get("education")

def _collect_key_skills(sections: List[Dict[str, Any]], k: int = 5) -> List[str]:
    flat: List[str] = []
    for sec in sections:
        for it in (sec.get("items") or []):
            if isinstance(it, str):
                flat.append(it)
    out, seen = [], set()
    for x in flat:
        if x not in seen:
            out.append(x); seen.add(x)
        if len(out) >= k: break
    return out

# ===== 3) Normalize raw_dict to what the template expects =====
def normalize(raw: Dict[str, Any]) -> Dict[str, Any]:
    skills_json = _loads(raw.get("skills"))
    edu_json    = _loads(raw.get("education"))
    exp_json    = _loads(raw.get("experience"))
    refs_json   = _loads(raw.get("references"))
    pi_json     = _loads(raw.get("personal_info"))

    # Skills -> sections
    sections = []
    if isinstance(skills_json, dict) and isinstance(skills_json.get("skills"), list):
        for sec in skills_json["skills"]:
            sections.append({
                "label": sec.get("category"),
                "items": sec.get("skills") or [],
                "note": sec.get("explanation"),
            })
    skills_out = {"sections": sections} if sections else None

    # Education
    education_out = None
    if isinstance(edu_json, dict) and isinstance(edu_json.get("education"), list):
        education_out = [{
            "education": it.get("education"),
            "date": it.get("date"),
            "description": it.get("description"),
        } for it in edu_json["education"]]

    # Experience
    experience_out = None
    if isinstance(exp_json, dict) and isinstance(exp_json.get("experience"), list):
        experience_out = [{
            "position_or_company": it.get("position_or_company"),
            "date": it.get("date"),
            "description": it.get("description"),
        } for it in exp_json["experience"]]

    # References
    references_out = None
    if isinstance(refs_json, dict) and isinstance(refs_json.get("references"), list):
        references_out = [{
            "name": it.get("name"),
            "relationship_or_title": it.get("relationship_or_title"),
            "contact": it.get("contact"),
        } for it in refs_json["references"]]

    # Header name/title + contacts
    name, title, contacts = None, None, None
    if isinstance(pi_json, dict) and isinstance(pi_json.get("profile"), dict):
        p = pi_json["profile"]
        name = " ".join([x for x in [p.get("name"), p.get("surname")] if x]) or None
        title = p.get("position")
        contacts = _build_contacts(pi_json)

    # Profile object for the template
    highest_degree = _derive_highest_degree(education_out or [])
    key_skills = _collect_key_skills(sections, 5) if sections else None
    profile_obj = {
        "job_title": title,
        "highest_degree": highest_degree,
        "key_skills": key_skills,
        "summary": raw.get("profile") or None,  # use your provided summary text
    }

    # Return context
    ctx = {
        "name": name or "Başar Temiz",
        "title": title,
        "contacts": contacts,
        "profile": profile_obj,
        "skills": skills_out,
        "education": education_out,
        "experience": experience_out,
        "references": references_out,
    }
    # strip empties
    def _empty(v: Any) -> bool: return v in (None, [], {})
    return {k: v for k, v in ctx.items() if not _empty(v)}


#--------function to parse the input-----------



if __name__ == "__main__":
    
    