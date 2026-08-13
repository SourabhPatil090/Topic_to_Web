import os
import sys
import json

# Ensure parent directory is in path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base Agent class from Lesson 4.1
from sprint_4.lesson_4_1_base_agent import Agent

# Define the specialized system prompt for the Developer persona
DEVELOPER_SYSTEM_INSTRUCTION = (
    "You are an expert Front-End Web Developer. Your job is to compile a raw markdown essay and a visual "
    "JSON style configuration into a single, production-ready, highly aesthetic HTML file.\n"
    "Your output HTML MUST adhere to the following styling guidelines to create a premium, state-of-the-art visual publication:\n"
    "1. It must be a complete single file containing <!DOCTYPE html>, <html>, <head>, and <body> tags.\n"
    "2. Inside <head>, import any custom Google Fonts requested in the theme configuration (if any).\n"
    "3. Inside <head>, write a <style> block that implements the custom theme properties (background_color, primary_text, accent_color, font_family_heading, font_family_body).\n"
    "4. Apply rich aesthetics: instead of a flat background color, combine the background_color with a subtle linear-gradient. "
    "   Wrap the essay content inside a centralized modern layout card with a white/dark glassmorphic container style (box-shadow, border-radius: 16px, border: 1px solid rgba(255,255,255,0.1), padding: 3rem).\n"
    "5. Format headings and text beautifully: use accent_color for headers with a subtle underline accent, "
    "   ensure readable line heights (1.7), and add letter-spacing for headings.\n"
    "6. Inside the <body>, convert the Markdown headings and paragraphs into semantic HTML tags (<h1>, <h2>, <p>).\n"
    "Output ONLY the complete raw HTML code. Do NOT add conversational replies or wrap the code block in markdown backticks."
)

class DeveloperAgent(Agent):
    def __init__(self):
        # Initialize the parent class with specific settings (no tools)
        super().__init__(
            name="Developer",
            system_instruction=DEVELOPER_SYSTEM_INSTRUCTION,
            tools=None
        )

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Developer Agent ===\n")
    
    try:
        developer = DeveloperAgent()
        print(f"Agent '{developer.name}' successfully initialized.")
        
        # Mock Writer Essay (Markdown)
        mock_essay = (
            "# Under the Neon Rain\n"
            "The city never sleeps. It only flickers under the hum of neon signs.\n"
            "## The Corporate Sky\n"
            "Monolithic skyscrapers pierce the clouds, casting shadows over the lower streets.\n"
            "## Conclusion\n"
            "We live in the cracks of the machine."
        )
        
        # Mock Designer Style Configuration (JSON)
        mock_style = {
            "detected_sentiment": "cyberpunk_neon",
            "theme": {
                "background_color": "#0d0e15",
                "primary_text": "#a0a5c0",
                "accent_color": "#ff007f",
                "font_family_heading": "'Orbitron', sans-serif",
                "font_family_body": "'Share Tech Mono', monospace"
            },
            "layout_style": "minimalist-single-column"
        }
        
        # Package both inputs into a single prompt for the compiler
        compiler_prompt = (
            f"Please compile the following content and style guidelines into HTML:\n\n"
            f"=== ESSAY CONTENT ===\n{mock_essay}\n\n"
            f"=== STYLE CONFIGURATION ===\n{json.dumps(mock_style, indent=2)}"
        )
        
        print("Sending content and theme to Developer Agent...\n")
        compiled_html = developer.execute(compiler_prompt)
        
        print("=== Compiled HTML Output ===")
        # Print first 500 characters to verify without cluttering terminal
        print(compiled_html[:500])
        print("\n... [TRUNCATED FOR LOG READABILITY] ...\n")
        print("=============================")
        
    except Exception as e:
        print(f"Test Failed: {e}")
