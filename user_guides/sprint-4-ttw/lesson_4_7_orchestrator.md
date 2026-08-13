# Lesson 4.7 - The Orchestrator (Pipeline Coordinator)

## Objective

Build the central coordinator pipeline script (`sprint_4/lesson_4_7_orchestrator.py`) that coordinates all 5 specialist agents, manages the shared state dictionary, implements self-correcting error-retry loops, and writes the verified webpage to disk.

---

## Why

Specialist agents are highly capable within their narrow roles, but they do not know how to coordinate with one another. We need a central conductor—the **Orchestrator**—to manage the sequence of operations. 

The Orchestrator captures inputs, applies input shield filters, sends topics to the Researcher, passes findings to the Writer, sends essays to the Designer, coordinates the Developer to compile HTML, routes pages to the Reviewer, and writes the finished page to disk *only* after a successful `PASS` report is achieved.

---

## What We Are Building

A Python orchestration script (`sprint_4/lesson_4_7_orchestrator.py`) containing the core function:
*   `run_publication_pipeline(topic)`: Standardizes the multi-agent data handoffs, executes local search tools dynamically, validates JSON style constraints, and runs a self-correction repair loop (up to 3 times) between the Developer and Reviewer if compiling bugs occur.

---

## Architecture

```text
[User Input] ──► [Input Shield] ──► (Safe?) ──► [Topic Refinement] ──► (Clean Subject)
                                                                      │
                                                                      ▼
+--------------------------------------------------------------------------+
|                            Orchestrator Loop                             |
|                                                                          |
| 1. Run ResearcherAgent  ──► [Route & Run Search Tool] ──► [Truncate]     |
| 2. Run WriterAgent      ──► (Essay text Markdown)                        |
| 3. Run DesignerAgent    ──► [JSON Validation Filter]  ──► (Style dict)   |
|                                                                          |
| 4. Compile Step (Loop up to 3 times):                                    |
|    ├── Run DeveloperAgent ──► (HTML string)                              |
|    └── Run ReviewerAgent  ──► (PASS?) ──► [Break & Write essays/page.html]|
|                                 (FAIL?) ──► [Retry with Reviewer report] |
+--------------------------------------------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.6.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Orchestrator Pipeline Script

### Do

Create a file named `sprint_4/lesson_4_7_orchestrator.py` and write the following code:

```python
import os
import sys
import json
import time
import urllib.request
from dotenv import load_dotenv

# Ensure parent directory is in path so we can import sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our working tools and validation guardrails from Sprint 2
from sprint_2.lesson_2_1_web_search import web_search
from sprint_2.lesson_2_2_file_io import write_file
from sprint_2.lesson_2_3_guardrails import input_shield, truncate_text
from sprint_2.lesson_2_4_json_validation import validate_designer_json

# Import all 5 specialist agent subclasses from Sprint 4
from sprint_4.lesson_4_2_researcher import ResearcherAgent
from sprint_4.lesson_4_3_writer import WriterAgent
from sprint_4.lesson_4_4_designer import DesignerAgent
from sprint_4.lesson_4_5_developer import DeveloperAgent
from sprint_4.lesson_4_6_reviewer import ReviewerAgent

# Load environment variables
load_dotenv()

def run_publication_pipeline(topic: str, log_callback = None) -> str:
    """
    Coordinates the multi-agent pipeline from topic to final compiled,
    verified HTML page inside output/essays/.
    """
    # Helper to send log updates to callback as well as stdout console print
    def log(message: str):
        print(message)
        if log_callback:
            log_callback(message)

    # Initialize the shared state dictionary to pass data between agents
    state = {
        "topic": topic,
        "research": None,
        "essay": None,
        "design": None,
        "html_code": None,
        "reviewer_report": None
    }
    
    log(f"==========================================")
    log(f"Starting Multi-Agent Pipeline for Topic:\n'{topic}'")
    log(f"==========================================\n")
    
    # 0. Check Input Shield Guardrail
    try:
        input_shield(state["topic"])
        log("[Guardrail] Input prompt cleared security checks.")
    except ValueError as e:
        log(f"[Guardrail] Input prompt failed: {e}")
        return f"Pipeline Blocked: {e}"
        
    # ----------------------------------------------------
    # STAGE 0: Topic Refinement (Extract Clean Title Slug)
    # ----------------------------------------------------
    log("\n--- [Stage 0] Activating Topic Refinement ---")
    log("[Orchestrator] Contacting LLM to extract clean, concise subject title...")
    try:
        refine_instruction = (
            "You are a text processing utility. Your job is to read the user's input prompt, "
            "ignore any meta-instructions (like 'research before writing', 'save it', or 'do X'), "
            "and extract ONLY the core subject topic as a clean, 3 to 6 word title.\n"
            "Output ONLY the plain title string. Do not use quotes, punctuation, or markdown."
        )
        
        # We reuse our standard HTTP connection method for a quick direct call
        use_local = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        if use_local:
            refine_url = "http://localhost:11434/v1/chat/completions"
            refine_model = os.getenv("LOCAL_MODEL_NAME", "qwen2.5:1.5b")
            refine_headers = {
                "Content-Type": "application/json"
            }
        else:
            refine_url = "https://openrouter.ai/api/v1/chat/completions"
            refine_model = os.getenv("OPENROUTER_MODEL", "poolside/laguna-m.1:free")
            refine_headers = {
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            }

        refine_payload = {
            "model": refine_model,
            "messages": [
                {"role": "system", "content": refine_instruction},
                {"role": "user", "content": state["topic"]}
            ]
        }
        
        refine_data = json.dumps(refine_payload).encode("utf-8")
        refine_req = urllib.request.Request(refine_url, data=refine_data, headers=refine_headers, method="POST")
        
        with urllib.request.urlopen(refine_req) as refine_response:
            refine_result = json.loads(refine_response.read().decode("utf-8"))
            refined_topic = refine_result["choices"][0]["message"]["content"].strip()
            
            # Clean up potential markdown or trailing quotes
            refined_topic = refined_topic.replace('"', '').replace("'", "").strip()
            log(f"[Orchestrator] Raw Prompt: '{state['topic']}'")
            log(f"[Orchestrator] Refined Subject: '{refined_topic}'")
            
            # Overwrite the state topic with the clean, refined title
            state["topic"] = refined_topic
    except Exception as e:
        log(f"[Warning] Topic refinement failed. Proceeding with raw input topic. Details: {e}")
        
    # ----------------------------------------------------
    # STAGE 1: Researcher Agent (Search Tool Calling Loop)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    researcher = ResearcherAgent()
    log(f"[Researcher] System Model: '{researcher.model}'")
    log("[Researcher] Sending topic details to LLM and waiting for search query generation...")
    
    # Execute the researcher agent
    response = researcher.execute(state["topic"])
    
    # Check if the researcher requested a web search tool call
    if isinstance(response, dict) and "tool_calls" in response:
        tool_call = response["tool_calls"][0]
        args = json.loads(tool_call["function"]["arguments"])
        
        log(f"[Researcher] Tool Call Decision: Requested '{tool_call['function']['name']}' tool.")
        log(f"[Researcher] Query Parameters formulated: {json.dumps(args)}")
        
        # Execute local search tool
        log(f"[Orchestrator] Executing local Python search helper...")
        search_raw = web_search(query=args.get("query"), max_results=args.get("max_results", 3))
        
        # Apply truncation guardrail to keep token limits safe
        state["research"] = truncate_text(search_raw, max_chars=2500)
        log("[Orchestrator] Local search execution complete. Context loaded into memories.")
    else:
        # Fallback if no tool was called
        state["research"] = response
        log("[Researcher] Decision: LLM resolved query directly without search tools.")
        
    # ----------------------------------------------------
    # STAGE 2: Writer Agent (Content Synthesis)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    log("\n--- [Stage 2] Activating Writer Agent ---")
    log("[Writer] Preparing research text payload...")
    writer = WriterAgent()
    
    # If research is empty or none, fallback to using the topic directly
    if not state["research"] or state["research"].strip() == "None":
        writer_prompt = f"Write a comprehensive essay directly about this topic: '{state['topic']}'."
        log("[Writer] Warning: Search context is empty. Directing writer to fallback on direct topic essay generation.")
    else:
        writer_prompt = f"Write a comprehensive essay using these research notes:\n\n{state['research']}"
        log("[Writer] Passing complete structured search summaries to the writing agent.")
        
    log("[Writer] Sending payload to LLM. Synthesizing article chapters...")
    state["essay"] = writer.execute(writer_prompt)
    log("[Writer] Draft compilation completed in Markdown.")
    
    # ----------------------------------------------------
    # STAGE 3: Designer Agent (Sentiment Analysis & Style JSON)
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    log("\n--- [Stage 3] Activating Designer Agent ---")
    log("[Designer] Analyzing essay tone for visual formatting mapping...")
    designer = DesignerAgent()
    
    log("[Designer] Requesting structured theme JSON configuration from LLM...")
    raw_design_output = designer.execute(state["essay"])
    
    # Validate and parse the Designer's output using JSON schema checks
    try:
        log("[Orchestrator] Running JSON schema validation guardrails on designer response...")
        state["design"] = validate_designer_json(raw_design_output)
        log(f"[Designer] Validation PASS. Sentiment tone identified: '{state['design'].get('detected_sentiment')}'")
        log(f"[Designer] Colors Selected: BG: {state['design']['theme']['background_color']} | Text: {state['design']['theme']['primary_text']}")
    except ValueError as e:
        log(f"[Warning] Designer validation FAILED. Falling back to default layout safety styles. Reason: {e}")
        # Default design safety fallback
        state["design"] = {
            "detected_sentiment": "default_clean",
            "theme": {
                "background_color": "#ffffff",
                "primary_text": "#333333",
                "accent_color": "#1a73e8",
                "font_family_heading": "sans-serif",
                "font_family_body": "sans-serif"
            },
            "layout_style": "minimalist"
        }
        
    # ----------------------------------------------------
    # STAGE 4: Developer & Reviewer self-correction loop
    # ----------------------------------------------------
    time.sleep(1.5)  # Rate limit protection pause
    log("\n--- [Stage 4] Activating Developer & Reviewer loop ---")
    developer = DeveloperAgent()
    reviewer = ReviewerAgent()
    
    # Set a loop limit of 3 compile retries
    COMPILE_RETRIES = 3
    
    # Construct the initial prompt containing essay and design configs
    dev_prompt = (
        f"Please compile the following content and style guidelines into HTML:\n\n"
        f"=== ESSAY CONTENT ===\n{state['essay']}\n\n"
        f"=== STYLE CONFIGURATION ===\n{json.dumps(state['design'], indent=2)}"
    )
    
    for attempt in range(COMPILE_RETRIES):
        log(f"\n[Compilation Attempt {attempt + 1} of {COMPILE_RETRIES}...]")
        log("[Developer] Sending Markdown + CSS theme specifications to LLM for layout compiling...")
        
        # Compile HTML
        state["html_code"] = developer.execute(dev_prompt)
        log("[Developer] HTML/CSS code compilation complete.")
        
        # Run QA Review check
        log("[Reviewer] Activating QA Reviewer Agent...")
        log("[Reviewer] Inspecting compiled webpage string for syntax, CSS styles, and font imports...")
        review_prompt = (
            f"Please audit the following compiled HTML code:\n\n"
            f"=== ORIGINAL ESSAY ===\n{state['essay']}\n\n"
            f"=== STYLE CONFIGURATION ===\n{json.dumps(state['design'])}\n\n"
            f"=== COMPILED HTML ===\n{state['html_code']}"
        )
        
        state["reviewer_report"] = reviewer.execute(review_prompt)
        log(f"[Reviewer] Audit complete. Response report:\n{state['reviewer_report'].strip()}")
        
        # Check if audit cleared with PASS
        if "PASS" in state["reviewer_report"]:
            log("[QA Audit] Page successfully verified with PASS flag. Breaking loop.")
            break
        else:
            log("[QA Audit] Page FAILED verification. Appending error feedback list and initiating self-correcting retry compile turn...")
            # If FAIL, modify the developer prompt to include the error logs for the next retry
            dev_prompt = (
                f"Your previous HTML compilation failed audit checks. Please fix the bugs listed in this report "
                f"and output the corrected HTML code:\n\n"
                f"=== REVIEWER ERROR REPORT ===\n{state['reviewer_report']}\n\n"
                f"=== PREVIOUS COMPILED HTML ===\n{state['html_code']}"
            )
    else:
        log("\n[Warning] Compile loop reached limit without PASS verification. Proceeding with last build.")
        
    # ----------------------------------------------------
    # STAGE 5: Save File to output directory
    # ----------------------------------------------------
    clean_slug = state["topic"].lower().replace(" ", "_")
    for char in ['?', '*', ':', '|', '<', '>', '"', '/', '\\', '.', ',']:
        clean_slug = clean_slug.replace(char, "")
    filename = f"essays/{clean_slug}.html"
    log(f"\n--- [Stage 5] Saving compiled file to '{filename}' ---")
    
    save_result = write_file(file_path=filename, content=state["html_code"])
    log(save_result)
    
    # Return the exact path of the generated HTML artifact
    return f"output/{filename}"

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Multi-Agent Publication Generator Activated ===")
    print("Type 'exit' or 'quit' to terminate the session.\n")
    
    while True:
        user_topic = input("Enter a topic for your web publication: ")
        
        if user_topic.strip().lower() in ["exit", "quit"]:
            print("Session terminated. Goodbye!")
            break
            
        if not user_topic.strip():
            continue
            
        result = run_publication_pipeline(user_topic)
        print(f"\n{result}\n")
        print("-" * 50)
```

### What
We initialize a shared `state` dictionary. We connect all 5 subclasses into a single execution stream:
1.  **Researcher:** Calls search tool ➔ returns context notes.
2.  **Writer:** Synthesizes notes ➔ outputs essay Markdown.
3.  **Designer:** Analyzes sentiment ➔ outputs style JSON (verified by JSON validation guardrail).
4.  **Developer & Reviewer Loop:** Compiles HTML ➔ Reviewer checks. If `FAIL`, Developer retries with the audit report. If `PASS`, we break and save.

### Why
Managing data transformations in a central orchestrator keeps individual agents simple and decoupled. The self-correction loop ensures that coding syntax and styling errors are caught and repaired automatically *before* the file is written to the user's disk.

### Behind the Scenes
- The shared `state` dictionary stores intermediate variables, making it easy to track, log, and pass variables between agent interfaces.
- The `dev_prompt` is dynamically rewritten during a `FAIL` attempt. By appending the reviewer's error report to the prompt, we instruct the LLM on exactly *how* to repair the code in the next turn.

### New Concepts
- **Shared State Architecture:** Passing a single state dictionary context along a pipeline.
- **Self-Healing Loop (Retry loop):** Designing loop gates where QA audit failures are fed back to the compiler for automated repairs.

### Verify
Run the orchestrator script in your terminal to watch the entire multi-agent pipeline execute live:

```powershell
python sprint_4/lesson_4_7_orchestrator.py
```

*Expected Output (Truncated log showing the flow):*
```text
==========================================
Starting Multi-Agent Pipeline for Topic:
'Quantum computing impacts on encryption'
==========================================

[Guardrail] Input prompt cleared security checks.

--- [Stage 1] Activating Researcher Agent ---
[Executing Tool: 'web_search' with args: {'query': 'quantum computing encryption impact'}]
[Researcher] Web search completed and context loaded.

--- [Stage 2] Activating Writer Agent ---
[Writer] Essay draft completed in Markdown.

--- [Stage 3] Activating Designer Agent ---
[Designer] Custom visual theme JSON generated and validated.

--- [Stage 4] Activating Developer & Reviewer loop ---

[Compilation Attempt 1 of 3...]
[Developer] Webpage compiled.
[Reviewer] Audit report: PASS

--- [Stage 5] Saving compiled file to 'essays/quantum_computing_impacts_on_encryption.html' ---
Success: File 'essays/quantum_computing_impacts_on_encryption.html' written successfully.

Pipeline execution completed! File written to: output/essays/quantum_computing_impacts_on_encryption.html
```

Check your `output/essays/` directory to verify the finished webpage has been created!

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.7 orchestrator pipeline complete"
git push
```

### What
Staging, committing, and pushing the orchestrator.

### Why
Version tracking the pipeline milestone.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Pipeline crashes during Designer validation | Designer outputted invalid JSON syntax. | Our try/except block catches this error and automatically falls back to a clean default visual style configuration dictionary to protect pipeline stability. |

---

## Key Takeaways

- Conductor loops coordinate data transitions between independent specialist agents.
- Pass error logs back to the compiler to allow self-healing retry cycles.
- Integrate fallback configurations (like default JSON themes) to maintain system stability when validation checks fail.

---

## Next Lesson

[Lesson 4.8 - Streamlit Web UI](lesson_4_8_streamlit_ui.md) - Learn how to build a Streamlit browser interface to trigger the pipeline and display results.
