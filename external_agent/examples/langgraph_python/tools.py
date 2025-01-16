from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
from typing import Dict, Any
import json
import uuid
import json
import ibm_boto3
from ibm_botocore.client import Config
from config import COS_API_KEY

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
    import random  # Add this at the top with other imports

    # Setup COS dump
    credentials = {
        'api_key_id': COS_API_KEY,
        'service_instance_id': 'crn:v1:bluemix:public:iam-identity::a/449a98ebc2e7439bac512a604003d05c::serviceid:ServiceId-79323ba9-7e9d-49f1-b4f2-d109e4ce5967',
        'endpoint': 'https://s3.us-south.cloud-object-storage.appdomain.cloud',  # Change region as needed
        'auth_endpoint': 'https://iam.cloud.ibm.com/identity/token'
    }

    profile_data = json.loads(profile)
    
    # Modified risk assessment logic with randomization
    risk_levels = ["Low", "Medium", "High"]
    possible_factors = [
        "Health history evaluation",
        "Lifestyle factors",
        "Occupational risks",
        "Family medical history",
        "Age-related risks",
        "Recreational activities",
        "Geographic location risks",
        "Previous claims history"
    ]
    possible_recommendations = [
        "Standard coverage recommended",
        "Additional evaluation needed for specific health conditions",
        "Higher premium coverage advised",
        "Preventive health measures recommended",
        "Specialist consultation required",
        "Risk mitigation plan needed",
        "Regular health monitoring suggested"
    ]

    risk_profile = {
        "risk_score": random.choice(risk_levels),
        "key_factors": random.sample(possible_factors, k=random.randint(2, 4)),
        "recommendations": random.sample(possible_recommendations, k=random.randint(1, 3))
    }

    try:
        success = store_json_in_cos(
            json_object=risk_profile,
            credentials=credentials,
            bucket_name='risk-analysis-bucket-hackathon-pru',
            object_key= ''.join(['risk_analysis/', str(uuid.uuid4()), '.json'])
        )
    except:
        pass  # It's fine if risk analysis doesn't get stored for hackathon
         
    return json.dumps(risk_profile)


@tool
def calculate_insurance_quote(risk_assessment: str) -> str:
    """
    Calculates an initial insurance quote based on the risk assessment.
    Input should be the JSON string output from assess_insurance_risk.
    Returns a quote summary.
    """
    import random  # Add this at the top with other imports

    try:
        risk_data = json.loads(risk_assessment)
        
        # Base premium varies based on risk score
        base_premiums = {
            "Low": random.uniform(300.00, 500.00),
            "Medium": random.uniform(500.00, 800.00),
            "High": random.uniform(800.00, 1200.00)
        }
        base_premium = base_premiums.get(risk_data["risk_score"], random.uniform(500.00, 800.00))
        
        # Risk adjustment factor varies by risk score
        risk_factors = {
            "Low": random.uniform(1.0, 1.2),
            "Medium": random.uniform(1.2, 1.5),
            "High": random.uniform(1.5, 2.0)
        }
        risk_adjustment = risk_factors.get(risk_data["risk_score"], 1.2)
        
        # Calculate final premium
        final_premium = round(base_premium * risk_adjustment, 2)
        
        # Coverage amount varies based on premium
        coverage_multipliers = {
            "Low": random.uniform(900, 1100),
            "Medium": random.uniform(800, 1000),
            "High": random.uniform(700, 900)
        }
        multiplier = coverage_multipliers.get(risk_data["risk_score"], 900)
        coverage_amount = round(final_premium * multiplier, 2)
        
        # Random term length selection
        term_lengths = ["10 years", "15 years", "20 years", "25 years", "30 years"]
        
        return json.dumps({
            "base_premium": round(base_premium, 2),
            "risk_adjustment_factor": round(risk_adjustment, 2),
            "final_monthly_premium": final_premium,
            "coverage_amount": coverage_amount,
            "quote_details": {
                "term_length": random.choice(term_lengths),
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


def store_json_in_cos(json_object, credentials, bucket_name, object_key):
    """
    Store a JSON object in IBM Cloud Object Storage
    
    Args:
        json_object: The Python dictionary/object to store as JSON
        credentials (dict): IBM COS credentials containing api_key_id, service_instance_id, etc.
        bucket_name (str): Name of the COS bucket
        object_key (str): The key/path where the JSON will be stored
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create IBM COS client
        cos_client = ibm_boto3.client(
            's3',
            ibm_api_key_id=credentials['api_key_id'],
            ibm_service_instance_id=credentials['service_instance_id'],
            ibm_auth_endpoint=credentials.get('auth_endpoint', 'https://iam.cloud.ibm.com/identity/token'),
            config=Config(signature_version='oauth'),
            endpoint_url=credentials['endpoint']
        )
        
        # Convert dictionary to JSON string
        json_data = json.dumps(json_object)
        
        # Upload JSON to COS
        cos_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=json_data,
            ContentType='application/json'
        )
        return True
        
    except Exception as e:
        print(f"Error uploading to IBM COS: {e}")
        return False

