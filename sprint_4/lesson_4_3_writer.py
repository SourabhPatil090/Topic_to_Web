import os
import sys

# Ensure parent directory is in path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Base Agent class from Lesson 4.1
from sprint_4.lesson_4_1_base_agent import Agent

# Define the specialized system prompt for the Writer persona
WRITER_SYSTEM_INSTRUCTION = (
    "You are an expert Creative Writer and content creator. Your job is to take raw research notes "
    "and synthesize them into a polished, structured, and engaging essay.\n"
    "Your essay MUST adhere to the following format:\n"
    "1. Start with a compelling H1 title (# Title).\n"
    "2. Include a brief, engaging Introduction paragraph.\n"
    "3. Structure the body content using at least two descriptive H2 subheadings (## Subheading).\n"
    "4. End with a reflective Conclusion paragraph.\n"
    "Write in a professional, clear, and informative tone. Output ONLY the completed Markdown essay."
)

class WriterAgent(Agent):
    def __init__(self):
        # Initialize the parent class with specific settings (no tools)
        super().__init__(
            name="Writer",
            system_instruction=WRITER_SYSTEM_INSTRUCTION,
            tools=None
        )

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing Writer Agent ===\n")
    
    try:
        writer = WriterAgent()
        print(f"Agent '{writer.name}' successfully initialized.")
        
        # Mock search notes to feed into the writer
        mock_research_notes = (
            "Research notes on Space Exploration 2026:\n"
            "- SpaceX launched Starship 6 successfully, testing orbital refuel systems.\n"
            "- NASA's Artemis III mission plans landing astronauts on lunar south pole by late 2026.\n"
            "- Commercial space stations (Axiom, Orbital Reef) are finalizing designs as ISS retirement nears.\n"
            "- Scientific consensus: lunar ice holds key to hydrogen refueling stations in space."
        )
        
        print("Sending research notes to Writer...\n")
        essay_output = writer.execute(mock_research_notes)
        
        print("=== Generated Essay ===")
        print(essay_output)
        print("=======================")
        
    except Exception as e:
        print(f"Test Failed: {e}")
