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
