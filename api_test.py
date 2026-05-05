import os
import google.genai as genai
from dotenv import load_dotenv

client = genai.Client(
    vertexai=True,
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents="Say hello in one sentence."
)

print(response.text)