import google.genai as genai
import os
from dotenv import load_dotenv
from google.auth import default

load_dotenv()
        
credentials, project_id = default()

project=os.getenv("PROJECT")
location= "global" #os.getenv("LOCATION") 
client = genai.Client(
    vertexai=True,
    project=project,
    location=location,
    credentials=credentials
    
)

print("--- Active Stable & Preview Models ---")
print(client.models)
# List available foundation models
for model in client.models.list():
    # Bypass the broken Vertex supported_actions attribute entirely 
    # and filter purely by name strings
    if "gemini" in model.name.lower():
        print(f"Model ID: {model.name}")
        print(f"Display Name: {model.display_name}")
        print(f"Input Limit: {model.input_token_limit} tokens\n")
        
        
model_id = "gemini-3.1-flash-lite"

print(f"Sending prompt to {model_id} via Vertex AI...")

try:
    response = client.models.generate_content(
        model=model_id,
        contents="Explain the difference between an API and a webhook in one clear sentence."
    )

    print("\n--- Model Output ---")
    print(response.text)

except Exception as e:
    print(f"\nExecution failed with error:\n{e}")