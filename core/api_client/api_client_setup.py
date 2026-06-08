import os
import google.genai as genai
from google.auth import default
from google.oauth2 import service_account
from core.api_client.api_client import APIClient

MODEL_3 = "gemini-3.1-flash-lite-preview" 
MODEL_2 = "gemini-2.5-flash-lite"
DEFAULT_MODEL_NAME = MODEL_2
DEFAULT_HIGHER_MODEL_NAME = "gemini-2.5-flash"


def create_api_client(game_sink, token_budget,
                  model_name=DEFAULT_MODEL_NAME, higher_model_name=DEFAULT_HIGHER_MODEL_NAME):

    project=os.getenv("PROJECT")
    location=os.getenv("LOCATION")
    
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
    else:
        from google.auth import default
        credentials, _ = default()
        
    client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials
    )
    return APIClient(client, model_name, higher_model_name, game_sink, token_budget=token_budget, model_3 = MODEL_3)