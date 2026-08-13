# Lesson 4.3 - The Writer Agent (Vibe-Coded)

## Objective

Build a specialized `WriterAgent` subclass that inherits from the `Agent` base class, configured with a creative writer persona, and validate that it can synthesize raw research notes into a cohesive, structured markdown essay.

---

## Why

Gathering research facts (Researcher Agent's job) is only half the work. We need a separate specialist agent dedicated entirely to content generation. The Writer Agent reads these compiled research notes, organizes them, manages tone, and writes a structured essay. Because the Writer Agent is a **vibe-coded** agent, it is a pure text-generation model—it does not call tools, making its codebase extremely clean.

---

## What We Are Building

A Python subclass module (`sprint_4/lesson_4_3_writer.py`) that:
1.  Imports the parent `Agent` class from `lesson_4_1_base_agent`.
2.  Defines the `WRITER_SYSTEM_INSTRUCTION` setting creative writing parameters (mandatory title, introduction, body chapters, and concluding paragraphs in clean Markdown).
3.  Initializes the writer subclass with empty tool lists.
4.  Runs a test execution synthesizing mock research notes into a formatted text block.

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
               |          class WriterAgent           |
               |  - name = "Writer"                   |
               |  - tools = [] (Pure LLM)             |
               +------------------+-------------------+
                                  │
      (execute("Raw facts: [1] Quantum computers ..."))
                                  ▼
               +--------------------------------------+
               |      Returns synthesized Markdown     |
               |      Essay text string               |
               +--------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.2.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Writer Agent Module

### Do

Create a file named `sprint_4/lesson_4_3_writer.py` and write the following code:

```python
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
```

### What
We declare `class WriterAgent(Agent):`. We call the parent constructor using `super().__init__()` passing the creative writing system prompt, and set `tools=None` (or leave it empty) since the writer doesn't need to read/write files or perform search requests directly.

### Why
The Writer's sole responsibility is **content synthesis**. Keeping it free of tools keeps the generation clean and fast: the model doesn't need to waste reasoning cycles deciding if it needs to call functions; it immediately goes to work generating the essay.

### Behind the Scenes
- When an agent is called with `tools=None`, the OpenRouter API payload will not contain a `tools` parameter. The model's response is forced to output plain text rather than tool execution requests.
- The system prompt specifies that the output must contain strict Markdown headers (`#` and `##`). This creates a standard format that our Developer Agent can easily compile into styled HTML/CSS later.

### New Concepts
- **Vibe-Coding (Pure LLM):** Building agent classes that rely entirely on prompt instructions to complete tasks, rather than calling external tools.
- **Content Synthesis:** The architectural practice of reading raw data sources and summarizing them into a cohesive story structure.

### Verify
Run the writer module directly in your terminal:

```powershell
python sprint_4/lesson_4_3_writer.py
```

*Expected Output (essay layout may vary slightly):*
```text
=== Testing Writer Agent ===

Agent 'Writer' successfully initialized.
Sending research notes to Writer...

=== Generated Essay ===
# The Dawn of the Starship Era: Space Exploration in 2026

The year 2026 represents a critical inflection point in humanity's journey to the stars. As the retirement of the International Space Station approaches, both commercial enterprises and national space agencies are accelerating their efforts to establish a permanent presence in low Earth orbit and on the Moon.

## Infrastructure and the Starship Catalyst
At the center of this shift is SpaceX's Starship system. The successful testing of orbital refueling systems has proved that heavy cargo can be hauled beyond Earth's gravity, laying the groundwork for Artemis lunar landings...

## The Lunar Frontier and Beyond
NASA's Artemis III mission remains on track to land astronauts near the lunar south pole by late 2026. Scientists agree that mining lunar ice holds the key to hydrogen fueling, unlocking deep space travel...

## Conclusion
The developments of 2026 represent more than just incremental technology updates. They are the structural pillars of a new spacefaring economy that will shape the next century of exploration.
=======================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.3 writer agent subclass complete"
git push
```

### What
Staging, committing, and pushing the new writer agent.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Model attempts to output code blocks or chat filler | System prompt was ignored or was too weak. | Enforce `"Output ONLY the completed Markdown essay."` at the end of your system prompt. |

---

## Key Takeaways

- Vibe-coded agents require no tool configurations; they rely purely on system prompts to execute.
- Writer agents synthesize fragmented raw details into structured, cohesive narrative flows.
- Structuring text output with standard Markdown headers prepares the content for HTML compilers.

---

## Next Lesson

[Lesson 4.4 - The Designer Agent](lesson_4_2_designer.md) - Learn how to build the Designer Agent subclass that outputs structural sentiment style configurations in valid JSON.
