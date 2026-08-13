# Lesson 1.1 - Project Setup & First API Call

## Objective

Create your workspace environment, configure environment secrets, and make a raw HTTP API call to OpenRouter's chat completions endpoint using only Python's built-in libraries.

---

## Why

In the real world, many production systems avoid using high-level SDKs because they add unnecessary dependency bloat, restrict control over network requests, and limit custom header optimization. Understanding how to interact with LLMs using raw HTTP requests gives you a foundational understanding of API mechanics and absolute control over your agent's payload structures.

---

## What We Are Building

A Python script (`lesson_1_1_first_call.py`) that loads an API key from an environment configuration, sends a structured JSON payload to OpenRouter, parses the response, and logs metadata including prompt and response tokens.

---

## Architecture

```text
+-------------------+
|    Environment    |
|   (.env config)   |
+---------+---------+
          | (reads api_key)
          v
+---------+---------+      HTTP POST (JSON)     +--------------------+
|  Python Script    | ────────────────────────> |    OpenRouter      |
| (urllib.request)  | <──────────────────────── |   /chat/complete   |
+-------------------+      JSON Response        +--------------------+
```

---

## Prerequisites

- Python 3.10+ installed on your system.
- An OpenRouter API Key saved from your signup.
- A terminal (PowerShell, Command Prompt, or Bash).

---

## Step 1: Initialize the Project Workspace & Git Repository

### Do

Run the following commands in your terminal to create your project folder, initialize Git tracking, configure a virtual environment, and set up your remote repository:

```powershell
# Create the root folder for our application and navigate inside
mkdir topic-to-web
cd topic-to-web

# Initialize a local Git repository and set the default branch to main
git init
git branch -M main

# Configure your remote GitHub repository linking
# (Replace with your actual GitHub username and repository name)
git remote add origin https://github.com/your-username/topic-to-web.git

# Initialize a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install the environment variables library
pip install python-dotenv
```

### What
We are creating the workspace folder, initializing a local Git version control tree, setting its branch name to `main`, linking it to our remote GitHub repository, spawning an isolated Python virtual environment (`.venv`), and installing `python-dotenv`.

### Why
Initializing Git early ensures every lesson milestone is tracked. Setting the remote origin links the project to your GitHub account immediately, making Day 2's Cloud Deployment step straightforward. The virtual environment ensures package isolation.

### Behind the Scenes
- `git init` creates a hidden `.git` folder in your workspace root which stores file change logs.
- `git remote add` records the URL of your online GitHub repository under the alias `origin` so that future `git push` commands know where to upload code.
- `python -m venv` creates an isolated binary tree of Python libraries to prevent package version conflicts.

### New Concepts
- **Git Version Control:** System used to track code edits and coordinate collaborative programming projects.
- **Remote Origin:** The default alias used by Git to identify the cloud repository (e.g., GitHub).
- **Virtual Environment (`venv`):** An isolated space for Python libraries specific to a single project.

### Verify
Verify that Git is initialized and the remote is configured:

```powershell
git status
# Output should show: No commits yet

git remote -v
# Output must list:
# origin  https://github.com/your-username/topic-to-web.git (fetch)
# origin  https://github.com/your-username/topic-to-web.git (push)
```

---

## Step 2: Configure Environment Secrets

### Do

Create a file named `.env` in the root of your `topic-to-web` folder and add your OpenRouter API key:

```env
OPENROUTER_API_KEY=your_actual_openrouter_api_key_here
```

Next, create a `.gitignore` file to ensure you never accidentally share your secret keys on GitHub:

```text
.venv/
.env
__pycache__/
output/
```

### What
We are creating a `.env` file to hold our credentials and a `.gitignore` file to instruct Git to ignore the virtual environment, key credentials, output artifacts, and cache files.

### Why
API keys are secrets. If a malicious actor gets access to your keys, they can run up expensive bills using your account. Storing keys in `.env` and adding `.env` to `.gitignore` ensures your secrets remain local to your machine.

### Behind the Scenes
The `.gitignore` file contains rules that tell Git which directories and files to untrack. The `python-dotenv` package we installed earlier will dynamically read the `.env` file at runtime and inject its key-value pairs directly into Python's native environment variables dictionary (`os.environ`).

### New Concepts
- **Environment Variable:** A dynamic value stored in the operating system environment that processes can read.
- **Git Ignoring:** Instructing version control systems to skip tracking specific private or temporary folders.

### Verify
Verify that the files exist in your directory. Run the following command in PowerShell:

```powershell
Get-ChildItem -Force
# Output must list:
# .env
# .gitignore
# .venv
```

---

## Step 3: Write the Raw API Call Script

### Do

Create a directory named `sprint_1/` in the root of your project. Inside it, create a file named `lesson_1_1_first_call.py` and write the following code:

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

# 4. Define the JSON Request Payload
# We use a free, lightweight model for testing: openai/gpt-oss-20b:free
payload = {
    "model": "openai/gpt-oss-20b:free",
    "messages": [
        {"role": "user", "content": "Explain the concept of Agentic AI in one sentence."}
    ]
}

# 5. Compile and Execute the HTTP Request
# Convert the payload dictionary to a JSON byte stream
data = json.dumps(payload).encode("utf-8")

req = urllib.request.Request(url, data=data, headers=headers, method="POST")

try:
    print("Sending request to OpenRouter...")
    with urllib.request.urlopen(req) as response:
        # Read the raw byte response
        raw_response = response.read()
        
        # Decode bytes and parse to a Python dictionary
        result = json.loads(raw_response.decode("utf-8"))
        
        # Extract the model's text response content
        ai_response = result["choices"][0]["message"]["content"]
        
        # Extract token consumption data
        prompt_tokens = result["usage"]["prompt_tokens"]
        completion_tokens = result["usage"]["completion_tokens"]
        
        # Print results
        print("\n=== Response ===")
        print(ai_response)
        print("================")
        print(f"Prompt Tokens: {prompt_tokens}")
        print(f"Response Tokens: {completion_tokens}")

except Exception as e:
    print(f"\nAn error occurred while connecting to the API: {e}")
```

### What
We are loading our environmental secrets, setting up the API endpoint url and Authorization headers, constructing a JSON request body containing a free model model name and prompt message, sending it using a raw `urllib.request.Request` POST call, parsing the returned byte stream into JSON, and extracting the text response along with its token count data.

### Why
By using `urllib.request` and the native `json` library, we avoid installing SDK packages. This teaches students how the API payloads look when transmitted across networks.

### Behind the Scenes
- `json.dumps()` translates our Python dictionary into a string format that systems understand. `.encode('utf-8')` translates that string into raw bytes required by network sockets.
- `urllib.request.urlopen()` performs the TCP handshake, negotiates SSL, transmits the raw bytes, receives the server's byte response, and returns an I/O stream.
- `raw_response.decode('utf-8')` converts the bytes back to a string, and `json.loads()` converts the string back into a Python dictionary.

### New Concepts
- **JSON Serialization (Dumping):** Converting an in-memory object (like a dict) into a text string.
- **JSON Deserialization (Loading):** Converting a JSON string back into a programmatic object.
- **HTTP POST Request:** A method to send data to a server to write or process state.

### Verify
Run the file in your active terminal:

```powershell
python sprint_1/lesson_1_1_first_call.py
```

*Expected Output:*
```text
Sending request to OpenRouter...

=== Response ===
Agentic AI refers to artificial intelligence systems designed to operate autonomously, making decisions and taking actions to achieve specific goals without constant human intervention.
================
Prompt Tokens: 16
Response Tokens: 28
```

---

## Step 4: Commit and Push to GitHub

### Do

Run the following commands in your terminal to save your progress locally and push it to your GitHub repository:

```powershell
# Check the status of untracked files
git status

# Stage all files for commit (except ignored ones)
git add .

# Create your first local commit
git commit -m "sprint 1: setup and first API call complete"

# Push the local main branch commits to your remote origin repository
# Note: You may be prompted to log in to GitHub on your first push
git push -u origin main
```

### What
We are checking our repository status, staging the modified files (which excludes the files we put in `.gitignore`), creating a local checkpoint commit, and uploading the local history to GitHub.

### Why
Committing at the end of each lesson ensures your changes are saved. Pushing to remote repositories guarantees that your cloud deployment configurations are ready and aligned on GitHub.

### Behind the Scenes
- `git add .` puts file modifications into Git's "index" or staging area.
- `git commit` takes a snapshot of the staging area and appends it to your branch history with a unique hash.
- `git push -u` sends these commits to the remote repository. The `-u` flag sets the upstream tracking so that future runs only require typing `git push`.

### New Concepts
- **Staging Area:** A staging workspace where files are prepared before a commit is finalized.
- **Commit:** A snapshot of code changes saved locally in version control history.
- **Upstream Tracking:** Linking a local branch to a specific remote branch for simplified pushing/pulling.

### Verify
Check your online GitHub repository in your web browser. Refresh the page to verify that the project structure (specifically `.gitignore`, `sprint_1/`, and `lesson_1_1_first_call.py`) is visible online.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'dotenv'` | Script is run outside the virtual environment. | Verify that `(.venv)` is visible in your terminal. If not, run activation script. |
| `HTTP Error 401: Unauthorized` | Missing or invalid API key. | Check your `.env` key spelling. Do not wrap the key in quotation marks. |
| `HTTP Error 400: Bad Request` | Invalid model name or syntax error in payload. | Ensure the model string exactly matches `"google/gemini-2.5-flash:free"`. |

---

## Key Takeaways

- Virtual environments keep project dependencies isolated and clean.
- API keys must always be stored locally in `.env` and kept out of Git version tracking.
- Network communication requires serializing Python variables into JSON bytes, sending them over HTTP, and deserializing the response back into dictionaries.

---

## Next Lesson

[Lesson 1.2 - Interactive Terminal Input](lesson_1_2_interactive.md) - Learn how to capture input from the user dynamically at runtime and send it to the LLM.
