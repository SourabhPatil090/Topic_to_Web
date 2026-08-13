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
