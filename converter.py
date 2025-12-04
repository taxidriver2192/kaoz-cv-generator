"""
Kaoz.dk JSON to RenderCV YAML Converter

This module handles the mapping between Kaoz.dk profile JSON structure
and RenderCV's expected YAML format.
"""

from datetime import datetime
from dateutil import parser
import yaml
from pathlib import Path


def parse_date(date_str):
    """
    Parse ISO date string to RenderCV format (YYYY-MM or YYYY)

    Args:
        date_str: ISO format date string or empty string

    Returns:
        Formatted date string (YYYY-MM) or "present" for empty/current dates
    """
    if not date_str or date_str == "":
        return "present"

    try:
        date = parser.parse(date_str)
        return date.strftime("%Y-%m")
    except Exception as e:
        print(f"⚠️  Warning: Could not parse date '{date_str}': {e}")
        return "present"


def split_summary_to_highlights(summary, max_length=150):
    """
    Split a long summary into multiple highlight bullet points

    Args:
        summary: Long text string
        max_length: Maximum length per highlight

    Returns:
        List of highlight strings
    """
    if not summary or len(summary) <= max_length:
        return [summary] if summary else []

    # Split on periods, but keep them
    sentences = [s.strip() + '.' for s in summary.split('.') if s.strip()]

    highlights = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_length:
            current += " " + sentence if current else sentence
        else:
            if current:
                highlights.append(current.strip())
            current = sentence

    if current:
        highlights.append(current.strip())

    return highlights if highlights else [summary]


def convert_kaoz_to_rendercv(kaoz_json, theme="sb2nov"):
    """
    Convert Kaoz.dk JSON profile to RenderCV YAML structure

    Args:
        kaoz_json: Dictionary with Kaoz.dk profile structure
        theme: RenderCV theme name (default: sb2nov)

    Returns:
        Dictionary in RenderCV format ready for YAML export
    """
    profile = kaoz_json.get("profile", {})

    # Initialize base CV structure
    cv_data = {
        "cv": {
            "name": profile.get("name", "Unknown Name"),
            "location": profile.get("location", ""),
            "email": profile.get("email", ""),
            "sections": {}
        },
        "design": {
            "theme": theme
        }
    }

    # Add phone if available
    # Note: RenderCV has strict phone validation, so we skip it if format might cause issues
    # Users can add phone manually to generated CV if needed
    # if profile.get("phone"):
    #     cv_data["cv"]["phone"] = profile["phone"]

    # Add social networks if available
    social_networks = []
    if profile.get("linkedin_url"):
        username = profile["linkedin_url"].split("/")[-1]
        social_networks.append({
            "network": "LinkedIn",
            "username": username
        })
    if profile.get("github_url"):
        username = profile["github_url"].split("/")[-1]
        social_networks.append({
            "network": "GitHub",
            "username": username
        })

    if social_networks:
        cv_data["cv"]["social_networks"] = social_networks

    # Add headline as summary section
    if profile.get("headline"):
        cv_data["cv"]["sections"]["summary"] = [profile["headline"]]

    # Map Professional Experience
    experiences = []
    for exp in kaoz_json.get("professional_experience", []):
        entry = {
            "company": exp.get("company", "Unknown Company"),
            "position": exp.get("title", "Unknown Position"),
            "start_date": parse_date(exp.get("start_date")),
            "end_date": parse_date(exp.get("end_date")),
        }

        # Add location if exists
        if exp.get("location"):
            entry["location"] = exp["location"]

        # Convert summary to highlights (bullet points)
        if exp.get("summary"):
            entry["highlights"] = split_summary_to_highlights(exp["summary"])

        experiences.append(entry)

    if experiences:
        cv_data["cv"]["sections"]["experience"] = experiences

    # Map Education
    education = []
    for edu in kaoz_json.get("education", []):
        # Parse degree to extract area (e.g., "Master of Science in Computer Science" -> "Computer Science")
        degree_str = edu.get("degree", "Unknown Degree")
        if " in " in degree_str:
            parts = degree_str.split(" in ", 1)
            degree = parts[0]
            area = parts[1]
        else:
            degree = degree_str
            area = degree_str

        entry = {
            "institution": edu.get("school", "Unknown Institution"),
            "area": area,
            "degree": degree,
            "start_date": str(edu.get("start_year", "")),
            "end_date": str(edu.get("end_year", "")),
        }

        # Add summary as highlights
        if edu.get("summary"):
            entry["highlights"] = split_summary_to_highlights(edu["summary"])

        education.append(entry)

    if education:
        cv_data["cv"]["sections"]["education"] = education

    # Map Skills to Technologies section
    skills = kaoz_json.get("skills", {})
    technologies = []

    if skills.get("programming_languages"):
        technologies.append({
            "label": "Programming Languages",
            "details": ", ".join(skills["programming_languages"])
        })

    if skills.get("frameworks_libraries"):
        technologies.append({
            "label": "Frameworks & Libraries",
            "details": ", ".join(skills["frameworks_libraries"])
        })

    if skills.get("other_skills"):
        # Take top 10 to avoid overcrowding
        top_other = skills["other_skills"][:10]
        technologies.append({
            "label": "Tools & Technologies",
            "details": ", ".join(top_other)
        })

    if technologies:
        cv_data["cv"]["sections"]["technologies"] = technologies

    return cv_data


def save_as_yaml(cv_data, output_path):
    """
    Save CV data as YAML file

    Args:
        cv_data: Dictionary with CV data
        output_path: Path to save YAML file

    Returns:
        Path to saved file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(cv_data, f,
                 default_flow_style=False,
                 allow_unicode=True,
                 sort_keys=False)

    return output_path


if __name__ == "__main__":
    # Test converter standalone
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python converter.py <input.json>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        kaoz_json = json.load(f)

    cv_data = convert_kaoz_to_rendercv(kaoz_json)
    output_path = save_as_yaml(cv_data, "test_output.yaml")

    print(f"✅ Converted to: {output_path}")
    print(f"📄 Name: {cv_data['cv']['name']}")
    print(f"📧 Email: {cv_data['cv']['email']}")
