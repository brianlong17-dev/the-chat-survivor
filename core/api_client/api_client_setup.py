import os
from dotenv import load_dotenv
import google.genai as genai
from google.auth import default
from core.api_client.api_client import APIClient
    
DEFAULT_MODEL_NAME = "gemini-2.5-flash-lite"
DEFAULT_MODEL_NAME = "gemini-3.1-flash-lite-preview"
DEFAULT_HIGHER_MODEL_NAME = "gemini-2.5-flash"


def create_api_client(game_sink,
                  model_name=DEFAULT_MODEL_NAME, higher_model_name=DEFAULT_HIGHER_MODEL_NAME):

    load_dotenv(override=True)
    project=os.getenv("PROJECT")
    location=os.getenv("LOCATION")
    credentials, project_id = default()
    client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials
    )
    return APIClient(client, model_name, higher_model_name, game_sink)