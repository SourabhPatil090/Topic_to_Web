# Lesson 1.3 - Conversation Memory Loop

## Objective

Build a persistent chat session by wrapping the HTTP API connection in an interactive CLI loop and maintaining a stateful conversation history (memory) across conversational turns.

---

## Why

LLMs are fundamentally stateless. Each API request is processed as a fresh interaction, with no memory of what was said in previous requests. To build a cohesive chat app or an agent that can reason across multiple steps, you must build a stateful memory system that stores and re-transmits conversation history with each network request.

---

## What We Are Building

A command-line script (`lesson_1_3_memory.py`) that loops continuously, prompting the user for messages. It appends the user's prompt to a list, requests completions from the model, captures the model's text response, appends the response back to the list, and prints the interaction. It exits cleanly when the user types `exit` or `quit`.

---

## Architecture

```text
               +--------------------------------------+
               |          Stateful memory list        |
               |  messages = [                        |
               |    {"role": "user", "content": ...}, |
               |    {"role": "model", "content": ...}|
               |  ]                                   |
               +------------------+-------------------+
                                  ^
                                  | (appends responses)
                                  v
+------------------+      HTTP POST (JSON)     +--------------------+
|  Python Script   | ────────────────────────> |    OpenRouter      |
|  (lesson_1_3)    | <──────────────────────── |   /chat/complete   |
+------------------+      JSON Response        +--------------------+
```

---

## Prerequisites

- Completion of Lesson 1.2.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Copy Starter Code from Lesson 1.2

### Do

Create a new file named `sprint_1/lesson_1_3_memory.py`. 

Copy the entire codebase from `sprint_1/lesson_1_2_interactive.py` and paste it into the new file.

### What
We initialize our Lesson 1.3 file by copying the interactive user input base we built in the previous lesson.

### Why
Using verified boilerplate scripts guarantees connectivity details and validation guards remain functional as we scale.

---

## Step 2: Implement Loop & Stateful Memory

### Do

Locate the input and payload configuration block in your copied code:

```python
# --- BEFORE (Lesson 1.2) ---
# 4. Accept dynamic input from the user in the terminal
user_prompt = input("Enter a topic for the publication: ")

# Check if the input is empty
if not user_prompt.strip():
    print("Error: Topic input cannot be empty.")
    exit(1)

# 5. Build payload dynamically using the user's input
payload = {
    "model": "google/gemini-2.5-flash:free",
    "messages": [
        {"role": "user", "content": f"Write a short, engaging headline about: {user_prompt}"}
    ]
}

# 6. Compile and Execute the HTTP Request ... [urllib connection code block followed]
```

Replace everything from **Step 4** downward with a persistent `messages` list and a `while True:` loop. 

Here is the complete, run-ready codebase for `sprint_1/lesson_1_3_memory.py`:

```python
import os
import json
import urllib.request
from dotenv import load_dotenv

# 1. Load the environment variables from the .env file
load_dotenv()

# 2. Retrieve the OpenRouter API Key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY not found. Please check your .env file.")
    exit(1)

# 3. Setup OpenRouter Target URL and Headers
url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 4. Initialize the stateful conversation history list
messages = []

print("=== TopicToWeb AI Chatbot Activated ===")
print("Type 'exit' or 'quit' to terminate the session.\n")

# 5. Enter the interactive session loop
while True:
    try:
        # Prompt the user for input
        user_input = input("You: ")
        
        # Check for termination command
        if user_input.strip().lower() in ["exit", "quit"]:
            print("Session terminated. Goodbye!")
            break
            
        # Skip empty entries
        if not user_input.strip():
            continue
            
        # Append the new user message to history
        messages.append({"role": "user", "content": user_input})
        
        # 6. Build the dynamic payload using the entire message history
        payload = {
            "model": "openai/gpt-oss-20b:free",
            "messages": messages
        }
        
        # Compile and execute the request
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req) as response:
            raw_response = response.read()
            result = json.loads(raw_response.decode("utf-8"))
            
            # Extract response details
            ai_response = result["choices"][0]["message"]["content"]
            prompt_tokens = result["usage"]["prompt_tokens"]
            completion_tokens = result["usage"]["completion_tokens"]
            
            # Print the AI's response
            print(f"\nAI: {ai_response.strip()}")
            print(f"[Tokens -> Prompt: {prompt_tokens} | Response: {completion_tokens}]\n")
            
            # Append the model's response back to history to maintain context
            messages.append({"role": "assistant", "content": ai_response})

    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
        # Remove the last user message if the request failed to keep memory aligned
        if messages and messages[-1]["role"] == "user":
            messages.pop()
```

### What
We declare a `messages` list before entering our loop. Within the `while True:` loop, we check for exit triggers (`exit` or `quit`), append the new user input to the list, send the *entire* list as our payload messages array, extract the text response, and append it back to the history list with the role of `assistant`.

### Why
Because LLMs do not have native session storage, we must act as the memory manager. By appending prompts and responses to a persistent list and sending that list back to the API on each turn, the model reads the entire history and understands the context.

### Behind the Scenes
- When you call `messages.append()`, you are appending a dictionary object to a list in your computer's RAM.
- When sending a payload, the model parses the messages array in order. It uses the past content as context to calculate the statistical probability of the next word.
- If a connection fails, we call `messages.pop()` to remove the last user prompt. This keeps the memory list clean, preventing the LLM from getting confused by requests that never received replies.

### New Concepts
- **Conversation State/Memory:** Storing past exchanges and re-submitting them to maintain conversation context.
- **Roles (`user` vs. `assistant`):** Declaring who said what. OpenRouter (and standard LLMs) identify user inputs as `user` and model outputs as `assistant`.
- **Memory Alignment (Popping):** Splicing out failed requests to prevent state pollution.

### Verify
Run the script in your terminal and perform a back-and-forth query:

```powershell
python sprint_1/lesson_1_3_memory.py
```

*Verification flow (testing if it remembers your name):*
```text
=== TopicToWeb AI Chatbot Activated ===
Type 'exit' or 'quit' to terminate the session.

You: My name is Alice.
AI: Nice to meet you, Alice! How can I help you today?
[Tokens -> Prompt: 11 | Response: 15]

You: What is my name?
AI: Your name is Alice.
[Tokens -> Prompt: 39 | Response: 6]

You: exit
Session terminated. Goodbye!
```

---

## Step 3: Commit and Push to GitHub

### Do

Run the following commands in your terminal to commit and push changes:

```powershell
git add .
git commit -m "sprint 1: lesson 1.3 memory loop complete"
git push
```

### What
Staging, committing, and pushing the new code changes.

### Why
Ensures that local milestones are safely tracked in your repository.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Model forgets my name after 3-4 turns | Clearing the `messages` list inside the loop instead of outside. | Verify that `messages = []` is declared **before** the `while True:` loop statement starts. |
| Memory contains duplicate entries | Appending user message multiple times. | Check that `messages.append` for the user is only called once per cycle. |

---

## Key Takeaways

- LLM APIs are stateless; developers must manage and send conversation history.
- Use a persistent list to store alternating `user` and `assistant` message dictionaries.
- Remove failed request entries using `.pop()` to prevent memory corruption.

---

## Next Lesson

[Lesson 1.4 - System Instructions & Persona](lesson_1_4_system.md) - Learn how to control the agent's tone, personality, and rules using system prompts.
