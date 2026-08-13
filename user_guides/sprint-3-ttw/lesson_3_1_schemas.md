# Lesson 3.1 - Tool Schemas (Function Declarations)

## Objective

Define JSON Schema declarations (Function Declarations) for your search and file tools, structuring them to be passed in OpenRouter API requests so the LLM knows what tools are available and how to request them.

---

## Why

LLMs cannot see your local Python functions directly. To inform the model that it has tools available (like `web_search`), we must describe those functions using a standard JSON Schema structure. The schema defines the function's name, its purpose, the parameters it accepts, and which inputs are mandatory. When passed inside the API request, the model evaluates this metadata and decides if it needs to request a tool call.

---

## What We Are Building

A Python module (`sprint_3/lesson_3_1_schemas.py`) containing the `TOOLS` list. 

This list stores the complete JSON Schema declarations for our three utility tools:
1.  `web_search`: Queries the web using search queries.
2.  `read_file`: Reads a file's content.
3.  `write_file`: Writes content to a file.

---

## Architecture

```text
+-----------------------------------------------------------+
|                   lesson_3_1_schemas.py                   |
|  TOOLS = [                                                |
|    { "name": "web_search", "parameters": { ... } },       |
|    { "name": "read_file",  "parameters": { ... } },       |
|    { "name": "write_file", "parameters": { ... } }        |
|  ]                                                        |
+-----------------------------+-----------------------------+
                              | (passed in payload['tools'])
                              v
+-----------------------------+-----------------------------+
|                        OpenRouter                         |
|                     /chat/completions                     |
+-----------------------------------------------------------+
```

---

## Prerequisites

- Complete Sprint 2.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Tool Schema Module

### Do

Create a file named `sprint_3/lesson_3_1_schemas.py` and write the following code:

```python
# Define the JSON schemas describing our local tools to OpenRouter / the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Queries Tavily or Serper search API to search the live web for facts and information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query keywords to look up on the web."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "The maximum number of search results to return (default is 3)."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Safely reads file contents from inside the allowed output directory path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative path to the file to read (e.g. 'essays/space.html')."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Safely writes or overwrites content to a file inside the allowed output directory, creating parent folders if missing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative destination path for the file (e.g. 'essays/deep_space.html')."
                    },
                    "content": {
                        "type": "string",
                        "description": "The raw string content to write inside the file."
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    }
]

# --- Local Testing Block ---
if __name__ == "__main__":
    import json
    print("=== Testing Tool Schema Definitions ===\n")
    print(f"Total Schemas Loaded: {len(TOOLS)}")
    print("\nExample Schema (web_search):")
    print(json.dumps(TOOLS[0], indent=2))
```

### What
We declare a list of dictionaries named `TOOLS`. Each dictionary describes a function using the required JSON Schema properties: `"type": "function"`, `"name"`, `"description"`, and `"parameters"`.

### Why
OpenRouter and standard model engines require a specific nested metadata shape to understand function parameters. Providing detailed descriptions for each parameter (like describing `file_path` as a relative path) helps the model select the correct parameter format.

### Behind the Scenes
- **Why this structure?** This exact nested dictionary structure is defined by the **JSON Schema Standard**, a strict industry formatting standard mandated by LLM API providers (OpenRouter, Google, OpenAI). You **cannot** change the names of the core structural keys (like `"type"`, `"function"`, `"parameters"`, `"properties"`, or `"required"`) or the API will reject the payload with an HTTP 400 Bad Request error.
- **What is custom?** While the structural keys are fixed, you have complete control over the *contents*: the actual function name (e.g. `"web_search"`), the descriptive text fields, parameter names (e.g. `"query"`), and the expected parameter data types.
- **Key-by-Key Breakdown:**
  *   `"type": "function"` tells the model this is an executable code function.
  *   `"parameters": {"type": "object"}` tells the LLM to pack all parameters into a single key-value dictionary (an object) in the response rather than loose text.
  *   `"required"` list ensures the LLM will not attempt a tool call without providing those specific parameters.

### New Concepts
- **JSON Schema Standard:** A strict, predefined metadata specification vocabulary used to declare validation parameters and interfaces to LLMs.
- **Function Declarations:** The specific schema block used to describe program functions to an LLM.
- **Strict Keys vs. Custom Contents:** The distinction between fixed standard API parameter names and custom application variables.

### Verify
Run the script in your terminal to verify that the schema loads correctly:

```powershell
python sprint_3/lesson_3_1_schemas.py
```

*Expected Output:*
```text
=== Testing Tool Schema Definitions ===

Total Schemas Loaded: 3

Example Schema (web_search):
{
  "type": "function",
  "function": {
    "name": "web_search",
    "description": "Queries Tavily or Serper search API to search the live web for facts and information.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query keywords to look up on the web."
        },
        "max_results": {
          "type": "integer",
          "description": "The maximum number of search results to return (default is 3)."
        }
      },
      "required": [
        "query"
      ]
    }
  }
}
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your changes and commit to GitHub:

```powershell
git add .
git commit -m "sprint 3: lesson 3.1 tool schemas complete"
git push
```

### What
Staging, committing, and pushing the new schema module.

### Why
Keeps version checkpoints aligned.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Model ignores the tool or passes wrong parameters | Typos in the schema keywords (e.g. spelling `"required"` as `"require"` or missing the `"type"` field). | Verify that your schema keys match the official structure exactly. |

---

## Key Takeaways

- LLMs discover tools via JSON Schema metadata passed in the API request.
- Provide descriptive comments inside the schema fields to help the model select parameters correctly.
- Mandatory parameters must be listed inside the `"required"` array key.

---

## Next Lesson

[Lesson 3.2 - Parsing Tool Calls & Routing](lesson_3_2_tool_parsing.md) - Learn how to parse tool requests from the API and route them to your local Python functions.
