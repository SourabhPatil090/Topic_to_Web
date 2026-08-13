# Lesson 4.1 - The Base Agent Class

## Objective

Build a reusable, object-oriented `Agent` base class that encapsulates connection setups, memory states, and API execution calls. This base class will serve as the shared foundation for all downstream specialist agents in our pipeline.

---

## Why

In a multi-agent system, every specialist agent (Researcher, Writer, Designer, etc.) needs to communicate with the LLM API, maintain its own conversation memory, and handle potential errors. If we write raw HTTP requests and memory array appends inside every single agent file, we end up with hundreds of lines of duplicate code. 

By designing an object-oriented `Agent` base class, we encapsulate these common variables and network functions. When building a new specialist agent, we simply inherit from the base class, define the specific system persona and tools, and run it instantly.

---

## What We Are Building

A Python class module (`sprint_4/lesson_4_1_base_agent.py`) that contains the core `Agent` class. 

The class provides:
*   `__init__(name, system_instruction, tools, model)`: Initializes private settings, api credentials, and creates a private `self.messages` conversation history list.
*   `execute(user_prompt)`: Handles formatting the payload, prepending system instructions, sending the HTTP POST request to OpenRouter, parsing the choices response, and updating memory safely.

---

## Architecture

```text
       +---------------------------------------------+
       |             class Agent (Base)              |
       |  - self.name                                |
       |  - self.system_instruction                  |
       |  - self.messages = []                       |
       |  - execute(user_prompt)                     |
       +----------------------+----------------------+
                              |
                +-------------+-------------+
                | (Inheritance)             | (Inheritance)
                v                           v
+-------------------------------+   +-------------------------------+
|    class ResearcherAgent      |   |      class WriterAgent        |
|    - name = "Researcher"      |   |    - name = "Writer"          |
|    - tools = [web_search]     |   |    - tools = []               |
+-------------------------------+   +-------------------------------+
```

---

## Prerequisites

- Complete Sprint 3.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Base Agent Module

### Do

Create a new directory named `sprint_4/` in the root of your project.

Create a file named `sprint_4/lesson_4_1_base_agent.py` and write the following code:

```python
import os
import json
import time
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Load environmental variables locally
load_dotenv()

class Agent:
    def __init__(self, name: str, system_instruction: str, tools: list = None, model: str = None):
        """
        Initializes the base agent with a name, system prompt guidelines,
        optional tools, target model, and a private conversation memory list.
        Supports switching between local SLMs (via Ollama) and cloud models (via OpenRouter).
        """
        self.name = name
        self.system_instruction = system_instruction
        self.tools = tools or []
        self.messages = []
        
        # Load local SLM configuration flags
        use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        
        if use_local:
            # Local Ollama config settings
            self.url = "http://localhost:11434/v1/chat/completions"
            self.model = os.getenv("LOCAL_MODEL_NAME", "qwen2.5:1.5b")
            self.api_key = "ollama"  # Ollama server doesn't require authentication
        else:
            # Cloud OpenRouter config settings
            self.url = "https://openrouter.ai/api/v1/chat/completions"
            self.model = model or os.getenv("OPENROUTER_MODEL", "poolside/laguna-m.1:free")
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            
            if not self.api_key:
                raise ValueError(f"[{self.name}] Error: OPENROUTER_API_KEY not found in environment variables.")

    def execute(self, user_prompt: str):
        """
        Executes a single conversational turn with the agent.
        Sends the payload to the LLM, updates memory, and returns the response.
        """
        # 1. Append the user prompt to the local memory history
        self.messages.append({"role": "user", "content": user_prompt})
        
        # 2. Setup Headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 3. Build payload. We inject the system instruction at index 0 of the payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_instruction}
            ] + self.messages
        }
        
        # 4. If tools are declared, pass them to the API payload
        if self.tools:
            payload["tools"] = self.tools
            
        max_retries = 5
        backoff = 2
        
        for attempt in range(max_retries):
            try:
                data = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    
                    message_obj = result["choices"][0]["message"]
                    content = message_obj.get("content")
                    tool_calls = message_obj.get("tool_calls")
                    
                    # CASE A: If the agent returns plain text content
                    if content and not tool_calls:
                        # Append response to memory to preserve history context
                        self.messages.append({"role": "assistant", "content": content})
                        return content
                        
                    # CASE B: If the agent returns a tool execution request
                    if tool_calls:
                        # Return the raw message dictionary object so the Orchestrator
                        # routing layer can intercept and execute the requested tool calls
                        return message_obj
                        
            except urllib.error.HTTPError as http_err:
                if http_err.code == 429 and attempt < max_retries - 1:
                    sleep_time = backoff * (2 ** attempt)
                    print(f"[{self.name}] Rate limit (429) encountered. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                else:
                    # Revert the last user message if the connection failed to keep memory aligned
                    if self.messages and self.messages[-1]["role"] == "user":
                        self.messages.pop()
                    return f"Error executing agent '{self.name}': HTTP Error {http_err.code}: {http_err.reason}"
            except Exception as e:
                if attempt < max_retries - 1:
                    sleep_time = backoff * (2 ** attempt)
                    print(f"[{self.name}] Connection issue encountered: {e}. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                else:
                    # Revert the last user message if the connection failed to keep memory aligned
                    if self.messages and self.messages[-1]["role"] == "user":
                        self.messages.pop()
                    return f"Error executing agent '{self.name}': {e}"

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Base Agent Class ===\n")
    
    # Define a simple Critic Agent to verify inheritance
    critic_persona = (
        "You are a strict critic. Review the user's topic and return "
        "a single, highly critical, analytical sentence. Do not be polite."
    )
    
    try:
        critic_agent = Agent(name="Critic", system_instruction=critic_persona)
        print(f"Agent '{critic_agent.name}' successfully initialized.")
        
        test_topic = "Agentic AI is going to solve all coding tasks."
        print(f"Sending test input: '{test_topic}'...\n")
        response = critic_agent.execute(test_topic)
        
        print("=== Critic Response ===")
        print(response)
        print("=======================")
        
    except Exception as e:
        print(f"Test Failed: {e}")
```

### What
We declare a reusable Python class `Agent` containing constructor `__init__` and executor `execute` methods. We use `self.` scopes to hold state variables (`self.messages`, `self.system_instruction`) bound to each class instance.

### Why
Using object-oriented programming (OOP) allows us to instantiate multiple unique agents in our compiler. Each agent has its own instance of `self.messages`, meaning the Researcher Agent's conversation history cannot leak or mix into the Writer Agent's context history.

### Behind the Scenes
- In Python, `class` defines a prototype structure. `__init__` is the constructor function run automatically when we instantiate an agent (e.g. `agent = Agent(...)`).
- The `self` parameter represents the specific instance of the object in memory. It ensures that variables set inside one agent don't overwrite variables in another agent.
- `execute()` returns the raw `message_obj` containing `tool_calls` if the LLM requests a tool. This shifts the routing responsibility up to our Orchestrator loop.

### New Concepts
- **Object-Oriented Programming (OOP):** A programming paradigm based on the concept of "objects," which can contain data and code.
- **Class Inheritance:** The mechanism where a child class inherits properties and methods from a parent class.
- **Instance Scope (`self`):** Variables that are unique and private to a specific object instance.

### Verify
Run the base agent module directly in your terminal:

```powershell
python sprint_4/lesson_4_1_base_agent.py
```

*Expected Output:*
```text
=== Testing Base Agent Class ===

Agent 'Critic' successfully initialized.
Sending test input: 'Agentic AI is going to solve all coding tasks.'...

=== Critic Response ===
While agentic systems show promise, overhyping them ignores the massive challenges of logic gaps, code security vulnerabilities, and context limit failures.
=======================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your changes and commit to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.1 base agent class complete"
git push
```

### What
Staging, committing, and pushing the new OOP base class.

### Why
Prepares your codebase for building specialist agents.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `TypeError: execute() missing 1 required positional argument: 'user_prompt'` | Calling `execute()` on the class instead of an object instance. | Ensure you instantiate the class first: `agent = Agent(...)`, then call `agent.execute(...)`. |

---

## Key Takeaways

- Reusable base classes prevent code duplication in multi-agent pipelines.
- Use `self` to maintain isolated memory lists for each specialist agent.
- Return raw tool call payloads to let the parent Orchestrator handle routing execution.

---

## Next Lesson

[Lesson 4.2 - The Researcher Agent](lesson_4_2_researcher.md) - Learn how to inherit from the Base Agent to create a specialized Researcher Agent configured with search tools.
