# Lesson 3.2 - Parsing Tool Calls & Routing

## Objective

Build a routing system that intercepts a model's request to execute a tool, extracts the function arguments, maps the request to your local Python functions (from Sprint 2), and executes them.

---

## Why

The LLM does not call your functions directly. Instead, when it decides to use a tool, it outputs a specific text block requesting a tool call, along with the arguments it wants to pass. Your code must act as the routing engine: it intercepts this request, runs the local Python code with the provided arguments, and feeds the resulting output text back to the LLM. 

---

## What We Are Building

A Python script (`sprint_3/lesson_3_2_tool_parsing.py`) that imports our tools (`web_search`, `read_file`, `write_file`) from Sprint 2, defines a `route_tool_call(function_name, arguments)` function, and runs a test case simulating an LLM tool call request.

---

## Architecture

```text
+-------------------+
|  OpenRouter API   | (outputs JSON tool call request)
+---------+---------+
          | (reads "name": "write_file", "arguments": "{...}")
          v
+---------+---------+      Calls matching Python code     +---------------------+
| route_tool_call() | ──────────────────────────────────> | write_file()        |
|  Routing Engine   | <────────────────────────────────── | Sprint 2 Tool File  |
+-------------------+       Returns success/error         +---------------------+
```

---

## Prerequisites

- Complete Lesson 3.1.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Routing Script

### Do

Create a file named `sprint_3/lesson_3_2_tool_parsing.py` and write the following code:

```python
import json
import sys
import os

# Ensure parent directory is in path so we can import modules from sprint_2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our working tools from Sprint 2
from sprint_2.lesson_2_1_web_search import web_search
from sprint_2.lesson_2_2_file_io import read_file, write_file

def route_tool_call(function_name: str, arguments: dict) -> str:
    """
    Routes a tool name and its arguments to the correct local Python function,
    executes it, and returns the output result as a string.
    """
    print(f"\n[Executing Tool: '{function_name}' with args: {arguments}]")
    
    try:
        if function_name == "web_search":
            query = arguments.get("query")
            max_results = arguments.get("max_results", 3)
            return web_search(query=query, max_results=max_results)
            
        elif function_name == "read_file":
            file_path = arguments.get("file_path")
            return read_file(file_path=file_path)
            
        elif function_name == "write_file":
            file_path = arguments.get("file_path")
            content = arguments.get("content")
            return write_file(file_path=file_path, content=content)
            
        else:
            return f"Error: Tool '{function_name}' not found."
            
    except Exception as e:
        return f"Error executing tool '{function_name}': {e}"

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Tool Routing Engine ===\n")
    
    # 1. Simulate a mock tool call request from an LLM API response payload.
    # The API returns arguments as a stringified JSON block.
    mock_tool_request = {
        "name": "write_file",
        "arguments": '{"file_path": "essays/route_test.txt", "content": "Routing system works successfully!"}'
    }
    
    # 2. Parse the stringified arguments into a Python dictionary
    parsed_arguments = json.loads(mock_tool_request["arguments"])
    
    # 3. Route and execute the tool
    execution_result = route_tool_call(
        function_name=mock_tool_request["name"],
        arguments=parsed_arguments
    )
    
    print(f"Execution Result:\n'{execution_result}'")
```

### What
We append the project root directory path using `sys.path.append()`, import our functions from `sprint_2`, write a routing function `route_tool_call()` mapping strings to functions, and run a test block parsing string arguments using `json.loads()`.

### Why
Because Python files are located inside different sub-directories (`sprint_2/` and `sprint_3/`), we modify `sys.path` to let Python locate our imports. The LLM returns tool arguments as a raw stringified JSON block, so we deserialize it to a dictionary before routing.

### Behind the Scenes
- `sys.path` is a list of directory paths where Python searches for modules when you call `import`. We append the parent path so imports resolve cleanly.
- Chaining conditional checks (`if/elif/else`) is the standard routing pattern. It maps the string identifier returned by the LLM (e.g. `"web_search"`) to our active Python functions in memory.

### New Concepts
- **Module Search Path (`sys.path`):** The list of directories Python searches for modules.
- **Routing Layer:** A dispatcher function that maps string identifiers to execution code blocks.
- **Stringified JSON Parsing:** Converting nested string payloads inside dictionaries back into dictionary variables.

### Verify
Run the script directly in your terminal:

```powershell
python sprint_3/lesson_3_2_tool_parsing.py
```

*Expected Output:*
```text
=== Testing Tool Routing Engine ===


[Executing Tool: 'write_file' with args: {'file_path': 'essays/route_test.txt', 'content': 'Routing system works successfully!'}]
Execution Result:
'Success: File 'essays/route_test.txt' written successfully.'
```

Check your `output/essays/` directory to verify that `route_test.txt` was created successfully!

---

## Step 2: Commit and Push to GitHub

### Do

Save your changes and commit to GitHub:

```powershell
git add .
git commit -m "sprint 3: lesson 3.2 tool parsing and routing complete"
git push
```

### What
Staging, committing, and pushing the new code.

### Why
Keeps version milestones synced.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'sprint_2'` | Python cannot locate the sibling directory because `sys.path` was not configured before import. | Ensure that `sys.path.append(...)` lines are run **before** your `from sprint_2...` import lines. |

---

## Key Takeaways

- LLM APIs return function arguments as a stringified JSON text block; parse it using `json.loads()` before usage.
- Map LLM tool strings to local code execution blocks using a clean routing handler.
- Modify `sys.path` to allow imports from sibling directories.

---

## Next Lesson

[Lesson 3.3 - The Agentic Loop (Single Agent)](lesson_3_3_single_agent.md) - Build a single agent that autonomously calls tools in a loop to answer questions.
