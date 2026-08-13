# Lesson 4.2 - The Researcher Agent

## Objective

Create a specialized subclass `ResearcherAgent` that inherits from the `Agent` base class, configures it with the `web_search` tool, and validates that it can autonomously break a user topic into a search query to gather web summaries.

---

## Why

Our system coordinates multiple agents. The first stage is **Information Gathering**. The Researcher Agent is a specialized persona designed to analyze a raw user topic (e.g. "renewable energy trends"), formulate a clean search query, use the `web_search` tool to fetch live facts from Tavily/Serper, and organize those facts. By inheriting from our `Agent` base class, we can create this researcher with clean, minimal code.

---

## What We Are Building

A Python subclass module (`sprint_4/lesson_4_2_researcher.py`) that:
1.  Imports the parent `Agent` class from `lesson_4_1_base_agent`.
2.  Defines the `RESEARCHER_SYSTEM_INSTRUCTION` setting boundaries (e.g., must use `web_search` to fetch facts, must return structured summaries).
3.  Initializes the researcher subclass passing the `web_search` tool schema declaration.
4.  Runs a test execution checking that the researcher requests a tool call containing search queries.

---

## Architecture

```text
               +--------------------------------------+
               |          class Agent (Base)          |
               +------------------+-------------------+
                                  ^
                                  | (Inherits variables and execute())
                                  v
               +--------------------------------------+
               |        class ResearcherAgent         |
               |  - name = "Researcher"               |
               |  - tools = [web_search schema]       |
               +------------------+-------------------+
                                  │
          (execute("Research climate change trends"))
                                  ▼
               +--------------------------------------+
               |        Returns choices payload       |
               |        asking for: 'web_search'       |
               +--------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.1.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Researcher Agent Module

### Do

Create a file named `sprint_4/lesson_4_2_researcher.py` and write the following code:

```python
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
```

### What
We declare `class ResearcherAgent(Agent):`, indicating that the researcher is a child class of `Agent`. We use the `super().__init__()` method to call the parent class constructor, configuring it with the custom Researcher system instructions and search schemas.

### Why
Using subclass inheritance (`super().__init__`) allows us to reuse the parent's `execute()` method and network connection code without rewriting it. This keeps our specialist agent code short, readable, and easy to maintain.

### Behind the Scenes
- `super()` is a built-in Python function that returns a proxy object delegating method calls to a parent or sibling class.
- We list-comprehend the `TOOLS` list to extract *only* the `web_search` schema dictionary. This guarantees the Researcher Agent is only aware of search capabilities and cannot attempt to read or write disk files.

### New Concepts
- **Subclassing:** Creating a new class that inherits attributes and behaviors from an existing class.
- **`super()` Constructor delegation:** Calling parent class constructor methods inside a child class override.
- **Tool Scoping:** Restricting an agent's access to only the specific tool schemas required for its role.

### Verify
Run the researcher module directly in your terminal:

```powershell
python sprint_4/lesson_4_2_researcher.py
```

*Expected Output:*
```text
=== Testing Researcher Agent ===

Agent 'Researcher' successfully initialized.
Sending task: 'Latest break-throughs in quantum computing 2026'...

=== Verification Successful ===
The Researcher Agent successfully requested a tool execution!
Requested Tool: 'web_search'
Arguments: {"query":"quantum computing breakthroughs 2026"}
================================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and push the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.2 researcher agent subclass complete"
git push
```

### What
Staging, committing, and pushing the new researcher agent.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `NameError: name 'Agent' is not defined` | Missing the import statement for the parent `Agent` class. | Ensure you import `Agent` at the top: `from sprint_4.lesson_4_1_base_agent import Agent`. |

---

## Key Takeaways

- Inherit from the parent `Agent` class to create specialized child agents with minimal code.
- Use `super().__init__()` to delegate constructor variables to the parent class.
- Scope tool access: only pass the specific schemas an agent needs to perform its role (e.g. Researcher only gets `web_search`).

---

## Next Lesson

[Lesson 4.3 - The Writer Agent](lesson_4_3_writer.md) - Learn how to build the Writer Agent subclass that synthesizes raw context facts into structured markdown chapters.
