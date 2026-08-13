import os
import sys

# Ensure parent directory is in path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base Agent class from Lesson 4.1
from sprint_4.lesson_4_1_base_agent import Agent

# Define the specialized system prompt for the Reviewer persona
REVIEWER_SYSTEM_INSTRUCTION = (
    "You are an expert Quality Assurance (QA) engineer and Code Auditor.\n"
    "Your job is to inspect the compiled HTML code produced by the Developer Agent and verify that it matches "
    "the original essay content and style configuration.\n"
    "You MUST verify the following checkpoints:\n"
    "1. Is the HTML syntactically valid (no missing closing tags, correct structure)?\n"
    "2. Are the fonts and colors requested in the style configuration successfully imported and applied inside the CSS?\n"
    "3. Is the complete text of the original essay present (no truncated sections)?\n\n"
    "Evaluation Rules:\n"
    "- If the code passes all checkpoints, output exactly one word: PASS\n"
    "- If the code fails any checkpoint, output: FAIL followed by a bulleted list of specific correction instructions.\n"
    "Output ONLY the validation report. Do NOT add conversational replies."
)

class ReviewerAgent(Agent):
    def __init__(self):
        # Initialize the parent class with specific settings (no tools)
        super().__init__(
            name="Reviewer",
            system_instruction=REVIEWER_SYSTEM_INSTRUCTION,
            tools=None
        )

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Reviewer Agent ===\n")
    
    try:
        reviewer = ReviewerAgent()
        print(f"Agent '{reviewer.name}' successfully initialized.")
        
        # Mock inputs to evaluate
        original_essay = "# Space Travel\nThis is a short essay about space flight."
        original_style = {"theme": {"background_color": "#0d0d0d", "accent_color": "#ff00ff"}}
        
        # 1. Test case: Malformed HTML (Missing closing style tag and background color)
        bad_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    color: #ffffff;
                /* Note: missing background color and missing closing style/head tags */
        <body>
            <h1>Space Travel</h1>
            <p>This is a short essay about space flight.</p>
        </body>
        </html>
        """
        
        review_prompt = (
            f"Please audit the following compiled HTML code:\n\n"
            f"=== ORIGINAL ESSAY ===\n{original_essay}\n\n"
            f"=== STYLE CONFIGURATION ===\n{original_style}\n\n"
            f"=== COMPILED HTML ===\n{bad_html}"
        )
        
        print("Sending malformed HTML to Reviewer Agent...\n")
        report = reviewer.execute(review_prompt)
        
        print("=== Reviewer Report ===")
        print(report)
        print("=======================")
        
    except Exception as e:
        print(f"Test Failed: {e}")
