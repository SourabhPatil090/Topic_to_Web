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
# Add a strict system instruction defining the AI's persona 
SYSTEM_INSTRUCTION =(
    "You are a strict, professional Headline Editor."
    "You must rewrite whatever topic or text the user inputs into a short, compelling "
    "newspaper headline. You must ONLY output the headline string. Do NOT output any "
    "introductory text, conversational comments, or explanations. Do NOT use quotation marks around your headline."
)

# 4. Initialize the stateful conversation history list
messages = []

print("Type 'exit' or 'quit' to end the conversation.")


# 5. Enter the interactive session loop
while True:
    try:
        # 5.1 Accept user input for the AI prompt
        user_input = input("You: ")

        # Skip empty inputs
        if not user_input.strip():
            print("Error: Input cannot be empty. Please enter a valid prompt.")
            continue

        # 5.2 Check for exit commands
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the conversation. Goodbye!")
            break

         # 5.3 Append the user's message to the conversation history
        messages.append({"role": "user", "content": user_input})

        # 6. Build the dynamic payload using entire conversation history
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "system", "content": SYSTEM_INSTRUCTION}] + messages
        }

        # 7. Compile and Execute the HTTP POST Request
        # Convert the payload dictionary to JSON byte stream
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req) as response:
            # Read the raw byte response
            raw_response = response.read()

            # Decode the byte response and parse to a Python dictionary
            result = json.loads(raw_response.decode("utf-8"))

            # Exract the mpdel's text response from the result
            ai_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Print the AI response from the OpenRouter API
            print("\nAI Response: " + ai_response.strip(), "\n")

            # Append the AI's response to the conversation history for context in future interactions
            messages.append({"role": "assistant", "content": ai_response.strip()})

    except Exception as e:
        print(f"An error occurred while making the request: {e}")
        if messages and messages[-1]["role"] == "user":
            messages.pop()  # Remove the last user message if an error occurred