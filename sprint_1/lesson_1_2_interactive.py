import os
import json
import urllib.request
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

# 2. Retrieve the API key from environment variables
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("API key not found. Please set the OPENROUTER_API_KEY in your .env file.")
    exit(1)

# 3. Setup OpenRouter Target URL (API endpoint) and Headers
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}
# 4. Accept user input for the AI prompt
user_prompt = input("Enter your prompt: ")

# Check if the user provided a prompt/input is empty
if not user_prompt.strip():
    print("No prompt provided. Input Cannot be empty. Please enter a valid prompt.")
    exit(1)

# 5. Build payload dynamically based on user input
payload = {
    "model": "openai/gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_prompt}
    ],
}

# 5. Compile and Execute the HTTP POST Request

# 6. Convert the payload dictionary to JSON byte stream
data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(url, data=data, headers=headers, method="POST")    

# 7. Send the request and handle the response
try:
    print("Sending request to OpenRouter API...")
    with urllib.request.urlopen(req) as response:
        # Read the raw byte response
        raw_response = response.read()

        # Decode the byte response and parse to a Python dictionary
        result = json.loads(raw_response.decode("utf-8"))

        # Exract the mpdel's text response from the result
        ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # Print the AI response from the OpenRouter API
        print("AI Response: " + ai_response)

except Exception as e:
    print(f"An error occurred while making the request: {e}")