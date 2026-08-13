# Lesson 3.3 - The Agentic Loop (Single Agent)

## Objective

Build a fully interactive CLI chatbot agent that runs an autonomous "Reasoning Loop" (Call LLM → Route & Execute Tool Calls → Feed Outputs Back → Repeat) to complete complex user instructions using web search and file tools.

---

## Why

This is the graduation milestone of the first half of the workshop. Up to this point, our code only handled one-shot, static inputs and outputs. By connecting our Sprint 1 conversation memory loop, our Sprint 2 tools, and our Sprint 3 routing schemas, we create an **autonomous agent**. The agent receives a high-level goal, decides which tools to call, executes them locally on your machine, reads the output results, and continues looping until it decides the objective has been reached.

---

## What We Are Building

An interactive console chatbot (`sprint_3/lesson_3_3_single_agent.py`) that:
1.  Maintains an outer conversational chat loop (`You: `).
2.  Passes our tool definitions (`TOOLS` schemas) to OpenRouter on every turn.
3.  Enters an inner agentic reasoning loop (capped at 5 iterations for safety) if the LLM requests tool execution.
4.  Updates its conversational memory with both the LLM's tool call requests (`assistant` role) and the execution output results (`tool` role) so the model has the context required to solve the task.

---

## Architecture

```text
               +--------------------------------------+
               |          Stateful memory list        |
               |  messages = [                        |
               |    {"role": "user", "content": ...}, |
               |    {"role": "assistant",             |
               |     "tool_calls": [...]},            |
               |    {"role": "tool", "content": ...}  |
               |  ]                                   |
               +------------------+-------------------+
                                  ^
                                  | (appends responses & tool outputs)
                                  v
+------------------+     HTTP Request (with Tools)     +--------------------+
|  Python Loop     | ────────────────────────────────> |    OpenRouter      |
|  (lesson_3_3)    | <──────────────────────────────── |   /chat/complete   |
+--------+---------+       JSON Choices Response       +--------------------+
         │
         ├── (Tool requested?) ──► [route_tool_call()] ──► [Runs Local Tool]
         │                                                        │
         └── (Plain text?) ──► [Prints Response to User] <────────┘
```

---

## Prerequisites

- Complete Lesson 3.2.
- Configure `OPENROUTER_API_KEY` and search credentials (`TAVILY_API_KEY` or `SERPER_API_KEY`) in your `.env` file at the workspace root.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Agentic Loop Script

### Do

Create a file named `sprint_3/lesson_3_3_single_agent.py` and write the following code:

```python
import os
import json
import urllib.request
import sys
from dotenv import load_dotenv

# Ensure parent directory is in path so we can import modules from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schemas and routing logic from Sprint 3
from sprint_3.lesson_3_1_schemas import TOOLS
from sprint_3.lesson_3_2_tool_parsing import route_tool_call

# Load environment variables
load_dotenv()

# Retrieve API Key
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("Error: OPENROUTER_API_KEY not found. Please check your .env file.")
    exit(1)

# OpenRouter target configuration
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Initialize conversational memory history
messages = []

# Inner reasoning loop limit to prevent runaway token costs
MAX_ITERATIONS = 5

print("=== Autonomous Agentic Chatbot Activated ===")
print("Type 'exit' or 'quit' to terminate the session.")
print("Example task: Search the web for AI automation and save results to 'essays/report.txt'\n")

# Main conversational loop
while True:
    user_input = input("You: ")
    
    if user_input.strip().lower() in ["exit", "quit"]:
        print("Session terminated. Goodbye!")
        break
        
    if not user_input.strip():
        continue
        
    # Append the user's instructions to memory
    messages.append({"role": "user", "content": user_input})
    
    # Enter the inner agentic reasoning loop
    for iteration in range(MAX_ITERATIONS):
        print(f"\n[Reasoning Turn {iteration + 1} of {MAX_ITERATIONS}...]")
        
        # Build payload containing both messages memory and tool schemas
        payload = {
            "model": "openai/gpt-oss-20b:free",
            "messages": messages,
            "tools": TOOLS
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                message_obj = result["choices"][0]["message"]
                content = message_obj.get("content")
                tool_calls = message_obj.get("tool_calls")
                
                # CASE A: The LLM returned plain text (Final Answer reached)
                if content and not tool_calls:
                    print(f"\nAI: {content.strip()}\n")
                    # Store final answer to maintain chat history context
                    messages.append({"role": "assistant", "content": content})
                    break
                    
                # CASE B: The LLM requested to execute one or more tools
                if tool_calls:
                    # 1. Append the tool request block to memory (required by API)
                    messages.append(message_obj)
                    
                    # 2. Iterate and execute each requested tool sequentially
                    for tool in tool_calls:
                        tool_id = tool.get("id")
                        function_name = tool["function"]["name"]
                        arguments = json.loads(tool["function"]["arguments"])
                        
                        # Execute local tool
                        tool_output = route_tool_call(
                            function_name=function_name,
                            arguments=arguments
                        )
                        
                        # 3. Append the execution output back to memory.
                        # We MUST include the matching tool_call_id and use the role "tool"!
                        messages.append({
                            "role": "tool",
                            "name": function_name,
                            "tool_call_id": tool_id,
                            "content": tool_output
                        })
                        
        except Exception as e:
            print(f"\nAn error occurred during execution: {e}\n")
            # Clean up the last user message if the turn crashed to prevent memory misalignment
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            break
    else:
        print(f"\n[Agentic Loop Warning: Reached safety limit of {MAX_ITERATIONS} turns without completing.]\n")
```

### What
We wrap our API handler inside an outer conversational `while True:` loop. For every user instruction, we run an inner `for iteration in range(5):` reasoning loop. If the LLM returns `tool_calls` in the JSON metadata payload, we loop through them, extract parameters using `json.loads()`, run the local tool via `route_tool_call()`, and append the results back to `messages` as a `"role": "tool"` block before requesting the next reasoning iteration.

### Why
Because the model is stateless, it cannot remember the results of the tool executions we perform locally on our machine. We must explicitly write the tool results back into the `messages` array history and resubmit them. This gives the model the "eyes" to read its own search or write output results in the next turn and decide what to do next.

### Behind the Scenes
- When the LLM requests a tool call, it returns `tool_calls` containing a unique `id` (e.g. `call_xYz123`). 
- When we return the tool execution result, we must pass that exact `tool_call_id` back in our message dictionary. This maps the tool output directly to the function that requested it, allowing the API gateway to process the conversation context accurately.

### New Concepts
- **Reasoning Loop:** The loop cycle where an agent analyzes context, decides on tool calls, parses results, and repeats until completion.
- **Tool Role (`"role": "tool"`):** The specialized conversation message role used specifically to feed function execution outputs back to the LLM.
- **Safety Capping:** Enforcing iteration limits (`MAX_ITERATIONS`) to prevent runaway recursive loops and protect API token budgets.

### Verify
Run the script in your terminal and try to perform a multi-step task:

```powershell
python sprint_3/lesson_3_3_single_agent.py
```

*Verification flow (testing web search and file writing):*
```text
=== Autonomous Agentic Chatbot Activated ===
Type 'exit' or 'quit' to terminate the session.
Example task: Search the web for AI automation and save results to 'essays/report.txt'

You: Search the web for Mount Everest's height and save the answer in essays/everest.txt.

[Reasoning Turn 1 of 5...]

[Executing Tool: 'web_search' with args: {'query': 'Mount Everest height'}]

[Reasoning Turn 2 of 5...]

[Executing Tool: 'write_file' with args: {'file_path': 'essays/everest.txt', 'content': 'Mount Everest height is approximately 8,848.86 meters (29,031.7 feet).'}]

[Reasoning Turn 3 of 5...]

AI: I have searched the web for Mount Everest's height and saved the result of 8,848.86 meters in essays/everest.txt.

You: exit
Session terminated. Goodbye!
```

Check your `output/essays/everest.txt` file to confirm that the agent successfully wrote the web results to the file!

---

## Step 2: Commit and Push to GitHub

### Do

Save your changes and push the completed Sprint 3 codebase to GitHub:

```powershell
git add .
git commit -m "sprint 3: lesson 3.3 single agent loop complete"
git push
```

### What
Staging, committing, and pushing the final Sprint 3 files.

### Why
Saves version milestones and prepares your workspace for Sprint 4.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| API returns `Invalid tool_call_id` error | The tool response dictionary was appended without the matching `tool_call_id` key, or the assistant's original `tool_calls` request message was not appended to history. | Verify that you append `message_obj` (the assistant's request) to messages *before* running the tools. Make sure the tool output dictionary contains the exact `"tool_call_id": tool_id` mapping. |

---

## Key Takeaways

- An autonomous agent loops reasoning steps (Call API ➔ Run Tool ➔ Feedback Result) to solve multi-step problems.
- Always cap the maximum loop iterations to prevent infinite loops and protect your token costs.
- Tool responses must contain the `"role": "tool"` type and pass the matching `"tool_call_id"` to keep the conversation memory aligned.

---

## Next Lesson

[Lesson 4.1 - The Base Agent Class](../sprint_4-ttw/lesson_4_1_base_agent.md) - Learn how to build an object-oriented `Agent` base class to coordinate multiple specialist agents in a pipeline.
