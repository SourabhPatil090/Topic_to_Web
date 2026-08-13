# Lesson 4.5 - The Developer Agent (HTML/CSS Compiler)

## Objective

Build a specialized `DeveloperAgent` subclass that inherits from the `Agent` base class, and validate that it can combine markdown essay text and a JSON style blueprint to compile a single-file, beautifully styled HTML publication page.

---

## Why

At this stage in our pipeline, we have the raw content (Markdown essay) and the creative theme settings (JSON style). We need a developer persona to merge these files. The Developer Agent acts as a front-end engineer: it reads both inputs, imports any Google Fonts specified in the theme, writes standard CSS variable overrides inside a `<style>` block, parses the markdown content into clean semantic HTML tags, and outputs the finished single-file webpage code.

---

## What We Are Building

A Python subclass module (`sprint_4/lesson_4_5_developer.py`) that:
1.  Imports the parent `Agent` class from `lesson_4_1_base_agent`.
2.  Defines the `DEVELOPER_SYSTEM_INSTRUCTION` containing strict code compiling rules (must write CSS rules using the JSON theme colors, must write semantic HTML layout, must wrap everything in a single, valid HTML document).
3.  Initializes the developer subclass (no tools required, purely focused on file compilation text output).
4.  Runs a test execution rendering a mock markdown essay and design configuration into raw HTML output.

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
               |         class DeveloperAgent         |
               |  - name = "Developer"                |
               |  - tools = [] (Pure LLM)             |
               +------------------+-------------------+
                                  │
          (execute("Essay Markdown + Style JSON"))
                                  ▼
               +--------------------------------------+
               |         Returns single-file          |
               |         HTML/CSS string code         |
               +--------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.4.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Developer Agent Module

### Do

Create a file named `sprint_4/lesson_4_5_developer.py` and write the following code:

```python
import os
import sys

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
```

### What
We declare `class DeveloperAgent(Agent):`. We call the parent constructor `super().__init__()` passing the HTML compiler system instructions. We package both the raw Markdown text and the JSON style dictionary into a single unified input prompt.

### Why
By keeping the Developer Agent as a vibe-coded agent, it utilizes the LLM's vast knowledge of CSS and modern web design grids (like Flexbox and CSS Grid) to compile a premium UI layout dynamically, matching the designer's requested aesthetic guidelines.

### Behind the Scenes
- In the prompt, we enforce: `Output ONLY the complete raw HTML code.` this ensures the output string is a clean, compile-ready document that the Orchestrator can write to a file without extra regex stripping.
- Google Fonts are imported using standard `<link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">` tags.

### New Concepts
- **HTML Compilation:** The process of combining unstructured Markdown text and JSON variables to produce structured web markups.
- **Dynamic CSS Variable injection:** Inserting design properties directly into a global HTML `<style>` layout block.

### Verify
Run the developer module directly in your terminal:

```powershell
python sprint_4/lesson_4_5_developer.py
```

*Expected Output (HTML head metadata details may vary):*
```text
=== Testing Developer Agent ===

Agent 'Developer' successfully initialized.
Sending content and theme to Developer Agent...

=== Compiled HTML Output ===
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Under the Neon Rain</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        body {
            background-color: #0d0e15;
            color: #a0a5c0;
            font-family: 'Share Tech Mono', monospace;
...
=============================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.5 developer agent subclass complete"
git push
```

### What
Staging, committing, and pushing the new developer agent.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| HTML is returned wrapped in ```html ... ``` tags | LLMs have a strong habit of wrapping code outputs in markdown syntax blocks. | Ensure the system prompt contains: `Do NOT wrap the code block in markdown backticks.` |

---

## Key Takeaways

- Developer agents convert unstructured text documents and design keys into semantic HTML and CSS variables.
- Enforce strict layout rules (centered layout, comfortable line heights) inside the system prompt to guarantee visual excellence.
- Package multiple data inputs (Markdown + JSON) into a single input prompt block for the compiler turn.

---

## Next Lesson

[Lesson 4.6 - The Reviewer Agent](lesson_4_6_reviewer.md) - Learn how to build the Reviewer Agent subclass that inspects the compiled file for errors and compiles verification reports.
