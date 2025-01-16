import os
from dotenv import load_dotenv

load_dotenv()

WATSONX_SPACE_ID = os.getenv('WATSONX_SPACE_ID', None)
WATSONX_API_KEY = os.getenv('WATSONX_API_KEY', None)
WATSONX_URL = os.getenv('WATSONX_URL','https://us-south.ml.cloud.ibm.com')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', None)
COS_API_KEY = os.getenv('COS_API_KEY', None)