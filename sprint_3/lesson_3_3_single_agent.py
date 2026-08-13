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
        print(f"[Debug] Current messages history size: {len(messages)}")
        
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
                
                # Debug raw API payload structure
                if "choices" not in result:
                    print(f"[Debug Error] Unexpected API Response: {json.dumps(result)}")
                    break
                    
                message_obj = result["choices"][0]["message"]
                content = message_obj.get("content")
                tool_calls = message_obj.get("tool_calls")
                
                print(f"[Debug] LLM Content returned: {repr(content)}")
                print(f"[Debug] LLM Tool Calls returned: {repr(tool_calls)}")
                
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
                    print(f"[Debug] Appended Assistant Tool Request to memory. Total size: {len(messages)}")
                    
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
                        
                        # Truncate debug output for terminal readability
                        truncated_output = tool_output[:100] + "..." if len(tool_output) > 100 else tool_output
                        print(f"[Debug] Tool execution output (first 100 chars): {repr(truncated_output)}")
                        
                        # 3. Append the execution output back to memory.
                        # We MUST include the matching tool_call_id and use the role "tool"!
                        messages.append({
                            "role": "tool",
                            "name": function_name,
                            "tool_call_id": tool_id,
                            "content": tool_output
                        })
                        print(f"[Debug] Appended Tool Response to memory. Total size: {len(messages)}")
                        
        except Exception as e:
            print(f"\n[Debug Error] An error occurred during execution: {e}\n")
            # Clean up the last user message if the turn crashed to prevent memory misalignment
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            break
    else:
        print(f"\n[Agentic Loop Warning: Reached safety limit of {MAX_ITERATIONS} turns without completing.]\n")
