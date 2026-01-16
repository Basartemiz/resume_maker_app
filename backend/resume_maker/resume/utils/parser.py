from __future__ import annotations

from langgraph.graph import StateGraph, START, END
from ..agents import (
    skills_agent, education_agent,
    experience_agent,
    references_agent,
    personal_information_agent, profile_agent,
    courses_agent, name_agent)
import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from typing import TypedDict

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

#----------functions to make the output---------

# Maximum retries per agent
MAX_RETRIES = 2

class State(TypedDict):
    context: str
    name: str
    skills: str
    education: str
    experience: str
    references: str
    personal_info: str
    profile: str
    courses: str
    # Retry counters for each agent
    retry_name: int
    retry_personal_info: int
    retry_profile: int
    retry_education: int
    retry_experience: int
    retry_courses: int
    retry_skills: int
    retry_references: int


# ===== Validation Functions =====

def _is_valid_json(text: str) -> bool:
    """Check if the text is valid JSON."""
    if not text or not isinstance(text, str):
        return False
    text = text.strip()
    if not ((text.startswith("{") and text.endswith("}")) or
            (text.startswith("[") and text.endswith("]"))):
        return False
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def _contains_hallucination_markers(text: str, context: str) -> bool:
    """
    Check if the output contains signs of hallucination.
    Returns True if hallucination is detected.
    """
    if not text:
        return True

    text_lower = text.lower()

    # Check for common hallucination patterns
    hallucination_patterns = [
        r'\bexample\.com\b',
        r'\bjohn\.doe\b',
        r'\bjane\.doe\b',
        r'\btest@test\b',
        r'\bplaceholder\b',
        r'\blorem ipsum\b',
        r'\bxxx\b',
        r'\b123-456-7890\b',
        r'\b555-\d{4}\b',  # Fake phone numbers
    ]

    for pattern in hallucination_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def _validate_personal_info(output: str, context: str) -> bool:
    """Validate personal_info agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        # Must have profile key
        if "profile" not in data:
            return False

        profile = data["profile"]
        # Empty profile is valid (means no data found)
        if not profile:
            return True

        # If profile has data, check for hallucination
        if _contains_hallucination_markers(output, context):
            return False

        return True
    except:
        return False


def _validate_experience(output: str, context: str) -> bool:
    """Validate experience agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "experience" not in data:
            return False

        # Empty array is valid
        if not data["experience"]:
            return True

        # Check each experience entry
        for exp in data["experience"]:
            if not isinstance(exp, dict):
                return False
            # Check for hallucinated data
            if _contains_hallucination_markers(json.dumps(exp), context):
                return False

        return True
    except:
        return False


def _validate_education(output: str, context: str) -> bool:
    """Validate education agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "education" not in data:
            return False

        # Empty array is valid
        if not data["education"]:
            return True

        for edu in data["education"]:
            if not isinstance(edu, dict):
                return False
            if _contains_hallucination_markers(json.dumps(edu), context):
                return False

        return True
    except:
        return False


def _validate_skills(output: str, context: str) -> bool:
    """Validate skills agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "skills" not in data:
            return False

        # Empty array is valid
        if not data["skills"]:
            return True

        for skill_group in data["skills"]:
            if not isinstance(skill_group, dict):
                return False
            if "category" not in skill_group or "skills" not in skill_group:
                return False

        return True
    except:
        return False


def _validate_courses(output: str, context: str) -> bool:
    """Validate courses agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "courses_and_certifications" not in data:
            return False

        # Empty array is valid
        if not data["courses_and_certifications"]:
            return True

        for course in data["courses_and_certifications"]:
            if not isinstance(course, dict):
                return False
            if _contains_hallucination_markers(json.dumps(course), context):
                return False

        return True
    except:
        return False


def _validate_references(output: str, context: str) -> bool:
    """Validate references agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "references" not in data:
            return False

        # Empty array is valid
        if not data["references"]:
            return True

        for ref in data["references"]:
            if not isinstance(ref, dict):
                return False
            # References are very sensitive - check for hallucination
            if _contains_hallucination_markers(json.dumps(ref), context):
                return False

        return True
    except:
        return False


def _validate_profile(output: str, context: str) -> bool:
    """Validate profile agent output (plain text, not JSON)."""
    if not output or not isinstance(output, str):
        return False

    output = output.strip()

    # Profile should be plain text, not JSON
    if output.startswith("{") or output.startswith("["):
        return False

    # Should have some content
    if len(output) < 20:
        return False

    # Check for hallucination markers
    if _contains_hallucination_markers(output, context):
        return False

    return True


def _validate_name(output: str, context: str) -> bool:
    """Validate name agent output."""
    if not _is_valid_json(output):
        return False

    try:
        data = json.loads(output)
        if "name" not in data:
            return False

        name = data["name"]
        # Empty name is valid (means no name found)
        if not name:
            return True

        # Name should be a non-empty string
        if not isinstance(name, str):
            return False

        # Check for hallucination markers
        if _contains_hallucination_markers(name, context):
            return False

        return True
    except:
        return False


# ===== Wrapper Nodes with Validation and Retry =====

def get_name_with_retry(state: State) -> dict:
    """Wrapper for name agent with validation and retry."""
    retry_count = state.get("retry_name", 0)

    result = name_agent.get_name(state)
    output = result.get("name", "")

    if _validate_name(output, state["context"]):
        return {"name": output, "retry_name": 0}
    else:
        # Invalid output - increment retry counter
        if retry_count < MAX_RETRIES:
            return {"name": "", "retry_name": retry_count + 1}
        else:
            # Max retries reached - return empty valid JSON
            return {"name": '{"name": ""}', "retry_name": 0}


def get_personal_info_with_retry(state: State) -> dict:
    """Wrapper for personal_info agent with validation and retry."""
    retry_count = state.get("retry_personal_info", 0)

    result = personal_information_agent.get_personal_info(state)
    output = result.get("personal_info", "")

    if _validate_personal_info(output, state["context"]):
        return {"personal_info": output, "retry_personal_info": 0}
    else:
        # Invalid output - increment retry counter
        if retry_count < MAX_RETRIES:
            return {"personal_info": "", "retry_personal_info": retry_count + 1}
        else:
            # Max retries reached - return empty valid JSON
            return {"personal_info": '{"profile": {}}', "retry_personal_info": 0}


def get_profile_with_retry(state: State) -> dict:
    """Wrapper for profile agent with validation and retry."""
    retry_count = state.get("retry_profile", 0)

    result = profile_agent.get_profile(state)
    output = result.get("profile", "")

    if _validate_profile(output, state["context"]):
        return {"profile": output, "retry_profile": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"profile": "", "retry_profile": retry_count + 1}
        else:
            return {"profile": "Professional summary not available.", "retry_profile": 0}


def get_education_with_retry(state: State) -> dict:
    """Wrapper for education agent with validation and retry."""
    retry_count = state.get("retry_education", 0)

    result = education_agent.get_education(state)
    output = result.get("education", "")

    if _validate_education(output, state["context"]):
        return {"education": output, "retry_education": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"education": "", "retry_education": retry_count + 1}
        else:
            return {"education": '{"education": []}', "retry_education": 0}


def get_experience_with_retry(state: State) -> dict:
    """Wrapper for experience agent with validation and retry."""
    retry_count = state.get("retry_experience", 0)

    result = experience_agent.get_experience(state)
    output = result.get("experience", "")

    if _validate_experience(output, state["context"]):
        return {"experience": output, "retry_experience": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"experience": "", "retry_experience": retry_count + 1}
        else:
            return {"experience": '{"experience": []}', "retry_experience": 0}


def get_courses_with_retry(state: State) -> dict:
    """Wrapper for courses agent with validation and retry."""
    retry_count = state.get("retry_courses", 0)

    result = courses_agent.get_courses_certifications(state)
    output = result.get("courses", "")

    if _validate_courses(output, state["context"]):
        return {"courses": output, "retry_courses": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"courses": "", "retry_courses": retry_count + 1}
        else:
            return {"courses": '{"courses_and_certifications": []}', "retry_courses": 0}


def get_skills_with_retry(state: State) -> dict:
    """Wrapper for skills agent with validation and retry."""
    retry_count = state.get("retry_skills", 0)

    result = skills_agent.get_skills(state)
    output = result.get("skills", "")

    if _validate_skills(output, state["context"]):
        return {"skills": output, "retry_skills": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"skills": "", "retry_skills": retry_count + 1}
        else:
            return {"skills": '{"skills": []}', "retry_skills": 0}


def get_references_with_retry(state: State) -> dict:
    """Wrapper for references agent with validation and retry."""
    retry_count = state.get("retry_references", 0)

    result = references_agent.get_references(state)
    output = result.get("references", "")

    if _validate_references(output, state["context"]):
        return {"references": output, "retry_references": 0}
    else:
        if retry_count < MAX_RETRIES:
            return {"references": "", "retry_references": retry_count + 1}
        else:
            return {"references": '{"references": []}', "retry_references": 0}


# ===== Conditional Edge Functions =====

def should_retry_name(state: State) -> str:
    """Decide whether to retry name or proceed."""
    if state.get("retry_name", 0) > 0 and state.get("retry_name", 0) <= MAX_RETRIES:
        return "retry_name"
    return "proceed_to_personal_info"


def should_retry_personal_info(state: State) -> str:
    """Decide whether to retry personal_info or proceed."""
    if state.get("retry_personal_info", 0) > 0 and state.get("retry_personal_info", 0) <= MAX_RETRIES:
        return "retry_personal_info"
    return "proceed_to_profile"


def should_retry_profile(state: State) -> str:
    """Decide whether to retry profile or proceed."""
    if state.get("retry_profile", 0) > 0 and state.get("retry_profile", 0) <= MAX_RETRIES:
        return "retry_profile"
    return "proceed_to_education"


def should_retry_education(state: State) -> str:
    """Decide whether to retry education or proceed."""
    if state.get("retry_education", 0) > 0 and state.get("retry_education", 0) <= MAX_RETRIES:
        return "retry_education"
    return "proceed_to_experience"


def should_retry_experience(state: State) -> str:
    """Decide whether to retry experience or proceed."""
    if state.get("retry_experience", 0) > 0 and state.get("retry_experience", 0) <= MAX_RETRIES:
        return "retry_experience"
    return "proceed_to_courses"


def should_retry_courses(state: State) -> str:
    """Decide whether to retry courses or proceed."""
    if state.get("retry_courses", 0) > 0 and state.get("retry_courses", 0) <= MAX_RETRIES:
        return "retry_courses"
    return "proceed_to_skills"


def should_retry_skills(state: State) -> str:
    """Decide whether to retry skills or proceed."""
    if state.get("retry_skills", 0) > 0 and state.get("retry_skills", 0) <= MAX_RETRIES:
        return "retry_skills"
    return "proceed_to_references"


def should_retry_references(state: State) -> str:
    """Decide whether to retry references or finish."""
    if state.get("retry_references", 0) > 0 and state.get("retry_references", 0) <= MAX_RETRIES:
        return "retry_references"
    return "finish"

def parse(input_of_user: str) -> dict:
    """
    🔹 Purpose:
        Main function to parse user input and generate a structured resume.
        Includes validation and retry logic for each agent.

    🔹 Parameters:
        input_of_user: str - Raw user input containing personal and professional details.

    🔹 Returns:
        dict - Structured resume data including skills, education, experience, references, personal info, and profile.
    """

    # Build workflow with retry logic
    workflow = StateGraph(State)

    # Add nodes using wrapper functions with validation
    workflow.add_node("get_name", get_name_with_retry)
    workflow.add_node("get_personal_info", get_personal_info_with_retry)
    workflow.add_node("get_profile", get_profile_with_retry)
    workflow.add_node("get_education", get_education_with_retry)
    workflow.add_node("get_experience", get_experience_with_retry)
    workflow.add_node("get_courses", get_courses_with_retry)
    workflow.add_node("get_skills", get_skills_with_retry)
    workflow.add_node("get_references", get_references_with_retry)

    # Start -> name (first extract the name)
    workflow.add_edge(START, "get_name")

    # name -> conditional (retry or proceed to personal_info)
    workflow.add_conditional_edges(
        "get_name",
        should_retry_name,
        {
            "retry_name": "get_name",
            "proceed_to_personal_info": "get_personal_info"
        }
    )

    # personal_info -> conditional (retry or proceed to profile)
    workflow.add_conditional_edges(
        "get_personal_info",
        should_retry_personal_info,
        {
            "retry_personal_info": "get_personal_info",
            "proceed_to_profile": "get_profile"
        }
    )

    # profile -> conditional (retry or proceed to education)
    workflow.add_conditional_edges(
        "get_profile",
        should_retry_profile,
        {
            "retry_profile": "get_profile",
            "proceed_to_education": "get_education"
        }
    )

    # education -> conditional (retry or proceed to experience)
    workflow.add_conditional_edges(
        "get_education",
        should_retry_education,
        {
            "retry_education": "get_education",
            "proceed_to_experience": "get_experience"
        }
    )

    # experience -> conditional (retry or proceed to courses)
    workflow.add_conditional_edges(
        "get_experience",
        should_retry_experience,
        {
            "retry_experience": "get_experience",
            "proceed_to_courses": "get_courses"
        }
    )

    # courses -> conditional (retry or proceed to skills)
    workflow.add_conditional_edges(
        "get_courses",
        should_retry_courses,
        {
            "retry_courses": "get_courses",
            "proceed_to_skills": "get_skills"
        }
    )

    # skills -> conditional (retry or proceed to references)
    workflow.add_conditional_edges(
        "get_skills",
        should_retry_skills,
        {
            "retry_skills": "get_skills",
            "proceed_to_references": "get_references"
        }
    )

    # references -> conditional (retry or finish)
    workflow.add_conditional_edges(
        "get_references",
        should_retry_references,
        {
            "retry_references": "get_references",
            "finish": END
        }
    )

    chain = workflow.compile()

    # Initialize state with user input and zero retry counters
    initial_state = {
        "context": input_of_user,
        "retry_name": 0,
        "retry_personal_info": 0,
        "retry_profile": 0,
        "retry_education": 0,
        "retry_experience": 0,
        "retry_courses": 0,
        "retry_skills": 0,
        "retry_references": 0,
    }

    state = chain.invoke(initial_state)

    return state

# ===== Helper functions for normalization =====
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
    name_json    = _loads(raw.get("name"))
    skills_json  = _loads(raw.get("skills"))
    edu_json     = _loads(raw.get("education"))
    exp_json     = _loads(raw.get("experience"))
    refs_json    = _loads(raw.get("references"))
    pi_json      = _loads(raw.get("personal_info"))
    courses_json = _loads(raw.get("courses"))

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

    # Courses and Certifications
    courses_out = None
    if isinstance(courses_json, dict) and isinstance(courses_json.get("courses_and_certifications"), list):
        courses_out = [{
            "course_or_certificate": it.get("course_or_certificate"),
            "date": it.get("date"),
            "description": it.get("description"),
        } for it in courses_json["courses_and_certifications"]]

    # References
    references_out = None
    if isinstance(refs_json, dict) and isinstance(refs_json.get("references"), list):
        references_out = [{
            "name": it.get("name"),
            "relationship_or_title": it.get("relationship_or_title"),
            "contact": it.get("contact"),
        } for it in refs_json["references"]]

    # Extract name from name_agent (priority) or fallback to personal_info
    name = None
    if isinstance(name_json, dict) and name_json.get("name"):
        name = name_json.get("name")

    # Header name/title + contacts from personal_info
    title, contacts = None, None
    if isinstance(pi_json, dict) and isinstance(pi_json.get("profile"), dict):
        p = pi_json["profile"]
        # Use name from name_agent if available, otherwise fallback to personal_info
        if not name:
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
        "summary": raw.get("profile") or None,
    }

    # Return context
    ctx = {
        "name": name or "User",
        "title": title,
        "contacts": contacts,
        "profile": profile_obj,
        "skills": skills_out,
        "education": education_out,
        "experience": experience_out,
        "courses": courses_out,
        "references": references_out,
    }
    # strip empties
    def _empty(v: Any) -> bool: return v in (None, [], {})
    return {k: v for k, v in ctx.items() if not _empty(v)}


#--------function to parse the input-----------

def parse_resume_input(raw_input: str) -> dict:
    parsed_data = parse(raw_input)
    normalized_data = normalize(parsed_data)
    return normalized_data

    
    