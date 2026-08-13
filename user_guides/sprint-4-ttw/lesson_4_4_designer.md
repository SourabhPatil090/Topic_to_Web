# Lesson 4.4 - The Designer Agent (Structured Output)

## Objective

Build a specialized `DesignerAgent` subclass that inherits from the `Agent` base class, configured with an aesthetic designer persona, and validate that it can analyze an essay's emotional tone and output a structured JSON style blueprint.

---

## Why

Our pipeline's final step is producing a beautiful, themed web publication. We cannot use generic, hardcoded styles for every topic. A technological topic needs a sleek, dark mode style; a nature essay needs earth tones. The Designer Agent acts as the creative art director: it reads the completed essay, determines its emotional sentiment, selects matching colors and fonts, and packages these guidelines into a structured JSON dictionary. The downstream Developer Agent reads this JSON blueprint to compile the styled HTML.

---

## What We Are Building

A Python subclass module (`sprint_4/lesson_4_4_designer.py`) that:
1.  Imports the parent `Agent` class from `lesson_4_1_base_agent`.
2.  Defines the `DESIGNER_SYSTEM_INSTRUCTION` setting strict formatting constraints (must output valid JSON conforming exactly to our required keys schema).
3.  Initializes the designer subclass (no tools needed, purely focused on structured text generation).
4.  Runs a test execution checking that the designer output is parsed correctly by our JSON validator from Sprint 2.

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
               |         class DesignerAgent          |
               |  - name = "Designer"                 |
               |  - tools = [] (Pure LLM)             |
               +------------------+-------------------+
                                  │
          (execute("Essay content about Space..."))
                                  ▼
               +--------------------------------------+
               |        Returns JSON style config     |
               |        (Parsed by validate_json)     |
               +--------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.3.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Designer Agent Module

### Do

Create a file named `sprint_4/lesson_4_4_designer.py` and write the following code:

```python
import os
import sys

# Ensure parent directory is in path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base Agent class from Lesson 4.1
from sprint_4.lesson_4_1_base_agent import Agent
# Import our JSON validation guardrail from Sprint 2
from sprint_2.lesson_2_4_json_validation import validate_designer_json

# Define the specialized system prompt for the Designer persona
DESIGNER_SYSTEM_INSTRUCTION = (
    "You are an expert Creative UI/UX Designer and brand strategist. Your job is to select the perfect "
    "visual theme guidelines for an essay based on its emotional tone and topic.\n"
    "You MUST analyze the text input and respond with a single, valid JSON block conforming EXACTLY to the following schema:\n"
    "{\n"
    "  \"detected_sentiment\": \"A short description of the emotional tone (e.g. professional_tech, earthy_warm, melancholic)\",\n"
    "  \"theme\": {\n"
    "    \"background_color\": \"HEX color code for background (e.g. #1a1c23)\",\n"
    "    \"primary_text\": \"HEX color code for main body text (e.g. #ffffff)\",\n"
    "    \"accent_color\": \"HEX color code for headings/highlights (e.g. #cca43b)\",\n"
    "    \"font_family_heading\": \"Standard web-safe or Google font family for titles (e.g. 'Playfair Display', serif)\",\n"
    "    \"font_family_body\": \"Standard web-safe or Google font family for body text (e.g. 'Inter', sans-serif)\"\n"
    "  },\n"
    "  \"layout_style\": \"Layout configuration indicator (e.g. minimalist-single-column-spacious)\"\n"
    "}\n"
    "Guidelines:\n"
    "- Output ONLY the JSON block.\n"
    "- Do NOT add conversational replies or explanations.\n"
    "- Ensure all JSON syntax is valid (no trailing commas, correct quotes)."
)

class DesignerAgent(Agent):
    def __init__(self):
        # Initialize the parent class with specific settings (no tools)
        super().__init__(
            name="Designer",
            system_instruction=DESIGNER_SYSTEM_INSTRUCTION,
            tools=None
        )

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Designer Agent ===\n")
    
    try:
        designer = DesignerAgent()
        print(f"Agent '{designer.name}' successfully initialized.")
        
        # Mock essay content to feed into the designer
        mock_essay = (
            "# Starry Dreams: The Future of Lunar Settlements\n"
            "Humanity is building a quiet, permanent home near the moon's south pole. "
            "Living in isolation under a cold, star-lit sky, astronauts feel a deep sense of separation, "
            "coupled with hope for future interstellar exploration..."
        )
        
        print("Sending essay to Designer for analysis...\n")
        raw_design_output = designer.execute(mock_essay)
        
        print("=== Raw Output from LLM ===")
        print(raw_design_output)
        print("===========================\n")
        
        # Validate JSON schema and parse using our Sprint 2 guardrail
        print("Running JSON validation guardrail...")
        parsed_style = validate_designer_json(raw_design_output)
        
        print("\n=== Validation Successful! ===")
        print(f"Detected Tone: {parsed_style['detected_sentiment']}")
        print(f"Background:    {parsed_style['theme']['background_color']}")
        print(f"Heading Font:  {parsed_style['theme']['font_family_heading']}")
        print("==============================")
        
    except Exception as e:
        print(f"\nTest Failed during validation: {e}")
```

### What
We declare `class DesignerAgent(Agent):`. We call the parent constructor `super().__init__()` passing the designer system prompt. In our testing block, we pass the raw text output directly into `validate_designer_json()` to verify format compliance.

### Why
Because LLMs can produce malformed JSON strings, combining the Designer Agent output directly with the JSON validation guardrail validates the reliability of our pipeline block before coordinating it under the main Orchestrator.

### Behind the Scenes
- In the prompt, we specify that the agent must output standard Google Font faces (e.g. `'Playfair Display'`, `'Inter'`). When the Developer Agent generates the HTML, it will import these font libraries automatically.
- Validating the output using `validate_designer_json` strips out markdown code block wrappers (like ` ```json `) automatically, ensuring our pipeline does not crash during execution.

### New Concepts
- **Structured Outputs:** Forcing an LLM to generate formatted data structures (like JSON or XML) instead of free-form text.
- **Sentiment Style Mapping:** Translating textual emotional sentiment into corresponding color schemes and layout typography.

### Verify
Run the designer module directly in your terminal:

```powershell
python sprint_4/lesson_4_4_designer.py
```

*Expected Output:*
```text
=== Testing Designer Agent ===

Agent 'Designer' successfully initialized.
Sending essay to Designer for analysis...

=== Raw Output from LLM ===
```json
{
  "detected_sentiment": "melancholic_optimism",
  "theme": {
    "background_color": "#12141a",
    "primary_text": "#d1d5db",
    "accent_color": "#818cf8",
    "font_family_heading": "'Playfair Display', serif",
    "font_family_body": "'Inter', sans-serif"
  },
  "layout_style": "minimalist-single-column-spacious"
}
```
===========================

Running JSON validation guardrail...

=== Validation Successful! ===
Detected Tone: melancholic_optimism
Background:    #12141a
Heading Font:  'Playfair Display', serif
==============================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.4 designer agent subclass complete"
git push
```

### What
Staging, committing, and pushing the new designer agent.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| JSON validation fails | The model added conversational text at the start (e.g. "Sure, here is your theme:") or used trailing commas. | Verify the system prompt contains: `"Output ONLY the JSON block. Do NOT add conversational replies."` |

---

## Key Takeaways

- Designer agents translate emotional content sentiments into HEX color codes and font styles.
- Specify precise JSON template schemas in the system prompt to enforce formatting compliance.
- Run JSON validation filters immediately after generation to catch syntax errors.

---

## Next Lesson

[Lesson 4.5 - The Developer Agent](lesson_4_5_developer.md) - Learn how to build the Developer Agent subclass that reads layout JSON and compiles styled HTML/CSS pages.
