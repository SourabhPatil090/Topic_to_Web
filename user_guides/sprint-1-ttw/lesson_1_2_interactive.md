# Lesson 1.2 - Interactive Terminal Input

## Objective

Create a script that dynamically accepts inputs from the command line interface (CLI) using Python's native input mechanisms and feeds them into the HTTP API payload.

---

## Why

Static payloads are useless for real-world applications. An agent must be able to process external inputs—whether they come from terminal prompts, user chat forms, or file systems. Accepting interactive input dynamically is the first step in building a responsive system.

---

## What We Are Building

A Python script (`lesson_1_2_interactive.py`) that prompts the user in the terminal to enter a topic, dynamically constructs the API JSON request payload using their input, and prints the generated response.

---

## Architecture

```text
+------------------+
|    User Input    |
| (Terminal stdin) |
+---------+--------+
          | (captures topic)
          v
+---------+--------+      HTTP POST (JSON)     +--------------------+
|  Python Script   | ────────────────────────> |    OpenRouter      |
|  (lesson_1_2)    | <──────────────────────── |   /chat/complete   |
+------------------+      JSON Response        +--------------------+
```

---

## Prerequisites

- Completion of Lesson 1.1.
- Your virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Copy Starter Code from Lesson 1.1

### Do

Create a new file named `sprint_1/lesson_1_2_interactive.py`. 

Copy the entire codebase from `sprint_1/lesson_1_1_first_call.py` and paste it into the new file.

### What
We are initializing our new lesson file by copying the working boilerplate configuration (imports, `.env` loading, credentials check, request setup) from our first lesson.

### Why
Instead of typing connection details and API URLs repeatedly, we build progressively. Copying verified configurations saves time and maintains consistency across our files.

---

## Step 2: Implement Dynamic User Input

### Do

Locate the static payload section in your `lesson_1_2_interactive.py` file:

```python
# --- BEFORE (Lesson 1.1) ---
# 4. Define the JSON Request Payload
# We use a free, lightweight model for testing: openai/gpt-oss-20b:free
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": "Explain the concept of Agentic AI in one sentence."}
    ]
}
```

Replace it by adding a dynamic terminal input and inserting it into the payload content:

```python
# --- AFTER (Lesson 1.2 Modifications) ---
# 4. Accept dynamic input from the user in the terminal
user_prompt = input("Enter a topic for the publication: ")

# Check if the input is empty
if not user_prompt.strip():
    print("Error: Topic input cannot be empty.")
    exit(1)

# 5. Build payload dynamically using the user's input
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": f"Write a short, engaging headline about: {user_prompt}"}
    ]
}
```

Here is how the complete, run-ready file should look:

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

# 4. Accept dynamic input from the user in the terminal
user_prompt = input("Enter a topic for the publication: ")

# Check if the input is empty
if not user_prompt.strip():
    print("Error: Topic input cannot be empty.")
    exit(1)

# 5. Build payload dynamically using the user's input
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": f"Write a short, engaging headline about: {user_prompt}"}
    ]
}

# 6. Compile and Execute the HTTP Request
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    print("\nSending request to OpenRouter...")
    with urllib.request.urlopen(req) as response:
        raw_response = response.read()
        result = json.loads(raw_response.decode("utf-8"))
        
        ai_response = result["choices"][0]["message"]["content"]
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        
        print("\n=== Response ===")
        print(ai_response.strip())
        print("================")
        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Response Tokens: {completion_tokens}")

except Exception as e:
    print(f"\nAn error occurred while connecting to the API: {e}")
```

### What
We capture keyboard input using `input()`, clean it up, make sure it is not empty, and embed it into our system query string inside the payload JSON before executing the POST request.

### Why
Using `input()` pauses execution and waits for standard input (`stdin`) bytes from the console. This makes our script interactive, adapting its payload dynamically depending on what the user types.

### Behind the Scenes
- `input()` blocks the main thread of execution, prompting the terminal line buffer. When the user hits `Enter`, it reads the buffer stream, converts it to a string, and resumes execution.
- `.strip()` removes leading and trailing whitespaces. This prevents users from sending empty prompts containing only spaces.
- The `f"..."` format dynamically interpolates the string value directly into our JSON messages array.

### New Concepts
- **Standard Input (`stdin`):** The input stream channel from which a program reads text data (typically keyboard inputs).
- **String Interpolation (f-strings):** Formatting strings dynamically by embedding variables directly inside curly braces.
- **Empty Check Safety:** Validating user input to avoid sending empty network requests that waste API credits.

### Verify
Run the file in your active terminal:

```powershell
python sprint_1/lesson_1_2_interactive.py
```

*Verification flow:*
```text
Enter a topic for the publication: Deep space exploration

Sending request to OpenRouter...

=== Response ===
"Sailing the Silent Sea: Why Humans Dare to Explore Deep Space"
================
Prompt Tokens: 20
Response Tokens: 14
```

---

## Step 3: Commit and Push to GitHub

### Do

Run the following commands in your terminal to save your changes to GitHub:

```powershell
git add .
git commit -m "sprint 1: lesson 1.2 interactive input complete"
git push
```

### What
We are staging our new file, committing it locally, and pushing it to our GitHub repository.

### Why
Saving incremental commits makes tracking simple and updates your remote repository checkpoint on GitHub.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Program exits immediately | Hitting Enter without typing anything or inputting only spaces. | Type a valid topic prompt. The code's `.strip()` check will catch empty strings. |

---

## Key Takeaways

- Python's built-in `input()` blocks program execution to read data from `stdin`.
- Always validate inputs (like using `.strip()`) before spending API tokens.
- F-strings allow you to dynamically insert input values into API request payloads.

---

## Next Lesson

[Lesson 1.3 - Conversation Memory Loop](lesson_1_3_memory.md) - Learn how to wrap your script in a continuous loop and maintain a memory of previous messages.
