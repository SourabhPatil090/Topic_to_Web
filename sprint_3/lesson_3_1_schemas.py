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
