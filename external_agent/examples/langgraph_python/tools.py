from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from typing import Dict, Any
import json

@tool
def web_search_duckduckgo(search_phrase: str):
    """Search the web using duckduckgo."""
    search = DuckDuckGoSearchResults()
    results = search.run(search_phrase) 
    return results

@tool
def news_search_duckduckgo(search_phrase: str):
    """Search news using duckduckgo."""
    search = DuckDuckGoSearchResults(backend="news")
    results = search.run(search_phrase) 
    return results

@tool
def generate_profile_details(applicant_info: str) -> str:
    """
    Use LLM to generate a life insurance applicant profile based on basic details.
    Input should be a string containing name, DOB, gender.
    Returns a JSON string with expanded applicant details.
    """
    prompt = f"""You are a life insurance profile generator. Generate a realistic profile for this applicant:
{applicant_info}

REQUIREMENTS:
- Return ONLY a valid JSON object, no other text
- Must use exactly this format:
{{
    "health_metrics": {{
        "height": "5'10\"",             // Use this exact format for height
        "weight": "170 lbs",            // Always include "lbs"
        "blood_pressure": "120/80"      // Use this exact format
    }},
    "medical_background": {{
        "conditions": [],               // List of current medical conditions, empty if none
        "family_history": []            // List of family medical conditions, empty if none
    }},
    "lifestyle": {{
        "smoker": false,               // Boolean true/false only
        "occupation": "Engineer",       // Current job
        "risky_activities": []         // List of risky hobbies/activities, empty if none
    }}
}}

Make the data realistic but slightly randomized. 80% of profiles should be relatively healthy with no major issues."""

    return prompt

@tool
def assess_insurance_risk(profile: str) -> str:
    """
    Analyzes the complete applicant profile and produces a risk assessment.
    Input should be a JSON string containing full applicant profile.
    Returns a risk assessment summary.
    """
    try:
        profile_data = json.loads(profile)

        print(profile_data)
        # Risk assessment logic would go here
        # For now, return a structured response
        return json.dumps({
            "risk_score": "Medium",  # Low, Medium, High
            "key_factors": [
                "Health history evaluation",
                "Lifestyle factors",
                "Occupational risks"
            ],
            "recommendations": [
                "Standard coverage recommended",
                "Additional evaluation needed for specific health conditions"
            ]
        })
    except json.JSONDecodeError:
        return "Error: Invalid profile format. Expected JSON string."

@tool
def calculate_insurance_quote(risk_assessment: str) -> str:
    """
    Calculates an initial insurance quote based on the risk assessment.
    Input should be the JSON string output from assess_insurance_risk.
    Returns a quote summary.
    """
    try:
        risk_data = json.loads(risk_assessment)
        # Quote calculation logic would go here
        # For now, return a sample quote structure
        return json.dumps({
            "base_premium": 500.00,
            "risk_adjustment_factor": 1.2,
            "final_monthly_premium": 600.00,
            "coverage_amount": 500000.00,
            "quote_details": {
                "term_length": "20 years",
                "payment_frequency": "monthly",
            }
        })
    except json.JSONDecodeError:
        return "Error: Invalid risk assessment format. Expected JSON string."
    

tool_choices = {
    "web_search_duckduckgo": web_search_duckduckgo,
    "news_search_duckduckgo": news_search_duckduckgo,
    "generate_profile_details": generate_profile_details,
    "assess_insurance_risk": assess_insurance_risk,
    "calculate_insurance_quote": calculate_insurance_quote

}