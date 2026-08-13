# Lesson 4.6 - The Reviewer Agent (Validation Specialist)

## Objective

Build a specialized `ReviewerAgent` subclass that inherits from the `Agent` base class, and validate that it can inspect compiled HTML pages for visual and structural compliance, returning clean PASS/FAIL reports.

---

## Why

In automated pipelines, agents can make mistakes. The Developer Agent might miss a closing HTML tag, fail to import a font, or omit a CSS color variable. To ensure the final output is of high quality, we need a separate **QA Validation Specialist**. The Reviewer Agent acts as a code auditor: it reviews the generated code against the original guidelines. By validating the output at the end of the pipeline, it acts as a gatekeeper: if there are issues, it reports them so the Orchestrator can trigger a self-correction retry turn.

---

## What We Are Building

A Python subclass module (`sprint_4/lesson_4_6_reviewer.py`) that:
1.  Imports the parent `Agent` class from `lesson_4_1_base_agent`.
2.  Defines the `REVIEWER_SYSTEM_INSTRUCTION` (must output exactly `PASS` if the HTML page contains all components and clean tags, or output `FAIL:` followed by a detailed error list if incorrect).
3.  Initializes the reviewer subclass (no tools required).
4.  Runs a test execution checking a mock webpage code block and outputting a structured report.

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
               |         class ReviewerAgent          |
               |  - name = "Reviewer"                 |
               |  - tools = [] (Pure LLM)             |
               +------------------+-------------------+
                                  │
          (execute("Compiled HTML Code + Guidelines"))
                                  ▼
               +--------------------------------------+
               |        Returns: 'PASS' OR            |
               |        'FAIL:\n- Error details'      |
               +--------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.5.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Reviewer Agent Module

### Do

Create a file named `sprint_4/lesson_4_6_reviewer.py` and write the following code:

```python
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
```

### What
We declare `class ReviewerAgent(Agent):`. We call the parent constructor `super().__init__()` passing the QA code auditor system guidelines. We run a test audit passing a malformed webpage code string to verify that it flags the syntax errors.

### Why
The Reviewer Agent acts as our safety check. If the LLM generates bad HTML, the Reviewer flags the exact syntax errors (e.g. missing `</style>` tags) and outputs `FAIL` with a list. The Orchestrator can capture this feedback and pass it back to the Developer to repair the webpage dynamically.

### Behind the Scenes
- The system instructions dictate that the reviewer must return `PASS` if correct. This makes it easy for our Orchestrator's code logic to execute a simple string comparison: `if "PASS" in report.strip():` to decide if it should terminate the compile loop.
- The bulleted error list returned during a `FAIL` provides dense, specific syntax correction guidelines that are fed directly back to the Developer Agent, facilitating rapid error recovery.

### New Concepts
- **Code Auditing & QA:** Exposing generated code blocks to a separate validator agent to detect logical, styling, or syntactic bugs.
- **PASS/FAIL Routing Indicators:** Configuring outputs to return unique, easy-to-evaluate keyword flags (like `PASS` or `FAIL`) to control loop transitions.

### Verify
Run the reviewer module directly in your terminal:

```powershell
python sprint_4/lesson_4_6_reviewer.py
```

*Expected Output (error feedback list may vary in wording):*
```text
=== Testing Reviewer Agent ===

Agent 'Reviewer' successfully initialized.
Sending malformed HTML to Reviewer Agent...

=== Reviewer Report ===
FAIL
- The HTML is syntactically invalid: the `<style>` tag is never closed with a `</style>` tag.
- The `<head>` tag is never closed with a `</head>` tag.
- The background color (`#0d0d0d`) specified in the style configuration is missing from the CSS.
=======================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.6 reviewer agent subclass complete"
git push
```

### What
Staging, committing, and pushing the new reviewer agent.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Model adds explanations instead of just `PASS` on clean files | Weak prompt guidelines. | Verify the prompt ends with: `Output ONLY the validation report. Do NOT add conversational replies.` |

---

## Key Takeaways

- Reviewer agents act as automated code auditors to verify the structural integrity of final webpage compilations.
- Enforce strict PASS/FAIL return states to allow simple string routing checks in your Orchestrator logic.
- Bulleted failure reports compile specific corrections that can be fed directly back to the compiler for automated healing.

---

## Next Lesson

[Lesson 4.7 - The Orchestrator (Pipeline Loop)](lesson_4_7_orchestrator.md) - Learn how to build the central Orchestrator pipeline script that connects the 5 agents and manages shared states.
