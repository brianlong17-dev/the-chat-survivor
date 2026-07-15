import google.genai as genai
import os
from dotenv import load_dotenv
from google.auth import default

load_dotenv()
        
credentials, _project_id = default()

project=os.getenv("PROJECT")
location=os.getenv("LOCATION")

api_key=os.getenv("GEMINI_API_KEY")


def run():
    if api_key:
        client = genai.Client(api_key=api_key)

        model_id = "gemini-3.1-flash-lite"
        print("Found API KEY")
        print_available_models(client)
        make_request_for_model_id(client, model_id)

    else:
        client = genai.Client(
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials)
        
        model_id = "gemini-3.1-flash-lite"
        print_available_models(client)
        make_request_for_model_id(client, model_id)
        
def print_available_models(client):
    print("--- Active Stable & Preview Models ---")
    for model in client.models.list():
        if "gemini" in model.name.lower():
            print(f"Model ID: {model.name}")
            print(f"Display Name: {model.display_name}")
            print(f"Input Limit: {model.input_token_limit} tokens\n")
            
def make_request_for_model_id(client, model_id):
            
    print(f"Sending prompt to {model_id}...")

    try:
        response = client.models.generate_content(
            model=model_id,
            contents="Explain the difference between an API and a webhook in one clear sentence."
        )

        print("\n--- Model Output ---")
        print(response.text)

    except Exception as e:
        print(f"\nExecution failed with error:\n{e}")
        


    
    
run()