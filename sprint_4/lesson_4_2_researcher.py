import os
import sys

# Ensure parent directory is in path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base Agent class from Lesson 4.1
from sprint_4.lesson_4_1_base_agent import Agent
# Import the TOOLS schemas from Sprint 3
from sprint_3.lesson_3_1_schemas import TOOLS

# Extract only the web_search tool schema from the list
RESEARCHER_TOOLS = [tool for tool in TOOLS if tool["function"]["name"] == "web_search"]

# Define the specialized system prompt for the Researcher persona
RESEARCHER_SYSTEM_INSTRUCTION = (
    "You are an expert Research Analyst. Your job is to research topics thoroughly by using your tools.\n"
    "When the user gives you a topic, you MUST call the 'web_search' tool to gather up-to-date facts.\n"
    "Once you receive the search results, synthesize the findings into a clear, structured research summary report.\n"
    "Focus on extracting concrete facts, statistics, and reputable sources."
)

class ResearcherAgent(Agent):
    def __init__(self):
        # Initialize the parent class with specific settings
        super().__init__(
            name="Researcher",
            system_instruction=RESEARCHER_SYSTEM_INSTRUCTION,
            tools=RESEARCHER_TOOLS
        )

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Researcher Agent ===\n")
    
    try:
        researcher = ResearcherAgent()
        print(f"Agent '{researcher.name}' successfully initialized.")
        
        test_topic = "Latest break-throughs in quantum computing 2026"
        print(f"Sending task: '{test_topic}'...\n")
        
        # Execute the agent
        response = researcher.execute(test_topic)
        
        # Check if the output is a tool call request dictionary
        if isinstance(response, dict) and "tool_calls" in response:
            print("=== Verification Successful ===")
            print("The Researcher Agent successfully requested a tool execution!")
            print(f"Requested Tool: '{response['tool_calls'][0]['function']['name']}'")
            print(f"Arguments: {response['tool_calls'][0]['function']['arguments']}")
            print("================================")
        else:
            print("=== Agent Response (No Tool Called) ===")
            print(response)
            print("=======================================")
            
    except Exception as e:
        print(f"Test Failed: {e}")
