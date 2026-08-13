# Lesson 4.8 - Streamlit Web UI

## Objective

Build an interactive, browser-based web dashboard (`app.py`) using Streamlit that reads a user's publication topic, executes the multi-agent Orchestrator pipeline, displays active status cards for each agent stage, and renders the completed webpage inside the browser.

---

## Why

Command-line interfaces are great for developers, but final users expect a clean, intuitive web interface. Streamlit allows us to build interactive web applications in pure Python without writing HTML, CSS, or JavaScript frontend code. 

By wrapping our `run_publication_pipeline` inside a Streamlit app, we provide a text input box, show dynamic progress indicators (spinners) for each stage of our multi-agent workflow, and render the resulting HTML page inside an iframe directly in the browser.

---

## What We Are Building

A Streamlit web application (`app.py`) in your project's root directory that:
1.  Provides a header title and topic input text field.
2.  Provides a "Generate Publication" trigger button.
3.  Utilizes `st.spinner()` status indicators to show the active agent stage (Researcher, Writer, Designer, etc.).
4.  Displays status panels showing the raw Markdown essay and visual JSON style variables.
5.  Uses `st.components.v1.html()` to embed the final compiled webpage inside the application dashboard.

---

## Architecture

```text
+-----------------------------------------------------------+
|                       Streamlit UI                        |
|                                                           |
|  [ Input Topic Box ] ──► (Click "Generate")               |
|                                                           |
|  Status Cards:                                            |
|  [✓] Researcher Complete  [✓] Writer Complete             |
|                                                           |
|  +-----------------------------------------------------+  |
|  |                   Iframe Container                  |  |
|  |                                                     |  |
|  |  (Displays output/essays/topic.html live page)      |  |
|  |                                                     |  |
|  +-----------------------------------------------------+  |
+-----------------------------+-----------------------------+
                              | (imports and triggers)
                              v
+-----------------------------+-----------------------------+
|               sprint_4/lesson_4_7_orchestrator.py         |
|               - run_publication_pipeline()                |
+-----------------------------------------------------------+
```

---

## Prerequisites

- Complete Lesson 4.7.
- Install Streamlit inside your active virtual environment:
  ```powershell
  pip install streamlit
  ```

---

## Step 1: Create the Streamlit App Script

### Do

Create a file named `app.py` in the **root directory** of your workspace and write the following code:

```python
import streamlit as st
import os
import json
import streamlit.components.v1 as components

# Import the Orchestrator pipeline function from Sprint 4
from sprint_4.lesson_4_7_orchestrator import run_publication_pipeline

# 1. Page Configuration and Title Setup
st.set_page_config(
    page_title="TopicToWeb Multi-Agent Publisher",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 TopicToWeb Multi-Agent Publication Dashboard")
st.write("Enter a topic in natural language. Our specialized AI Agent orchestra will research, write, design, and compile a verified publication page instantly.")

st.markdown("---")

# 2. Setup the User Input Form Layout and History Sidebar
with st.sidebar:
    st.header("Create New Publication")
    user_topic = st.text_input(
        "Enter Publication Topic:",
        placeholder="e.g., The Future of Fusion Energy"
    )
    
    generate_btn = st.button("Generate Web Publication", type="primary")
    
    st.markdown("---")
    st.header("Published Gallery")
    
    # Scan the essays folder to list existing publications
    essays_dir = "output/essays"
    existing_essays = []
    if os.path.exists(essays_dir):
        existing_essays = [f for f in os.listdir(essays_dir) if f.endswith(".html")]
        
    if existing_essays:
        st.write("Select an essay to view:")
        for essay_file in sorted(existing_essays):
            # Format clean title label from file name
            clean_label = essay_file.replace(".html", "").replace("_", " ").title()
            if st.button(f"📄 {clean_label}", key=essay_file, use_container_width=True):
                # Save the selected file to session state for rendering
                st.session_state["selected_essay"] = os.path.join(essays_dir, essay_file)
    else:
        st.info("No publications created yet.")

# 3. Handle Pipeline Trigger Execution
if generate_btn:
    if not user_topic.strip():
        st.error("Error: Please enter a valid topic first.")
    else:
        st.info(f"Initiating multi-agent pipeline for: **'{user_topic}'**...")
        
        # Create an interactive, expanding status log console block
        with st.status("🤖 Multi-Agent Execution Logs", expanded=True) as status_box:
            # UI print callback function
            def ui_log(message: str):
                st.write(message)
                
            # Run Orchestrator Pipeline passing the UI callback hook
            pipeline_result = run_publication_pipeline(user_topic, log_callback=ui_log)
            
            # The pipeline result is now the exact relative path of the file
            target_relative_path = pipeline_result
            
            # Update the status box state when finished
            if target_relative_path and os.path.exists(target_relative_path):
                status_box.update(label="✅ Multi-Agent Pipeline Completed Successfully!", state="complete")
            else:
                status_box.update(label="❌ Pipeline Execution Failed!", state="error")
            
        if target_relative_path and os.path.exists(target_relative_path):
            st.success("✅ Webpage Created successfully! Check the artifacts viewer below.")
            st.session_state["selected_essay"] = target_relative_path
        else:
            st.error(f"Pipeline Failed: {pipeline_result}")

# 4. Handle Rendering Selected Essay Output
if "selected_essay" in st.session_state and os.path.exists(st.session_state["selected_essay"]):
    file_path = st.session_state["selected_essay"]
    
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    col_source, col_render = st.columns([1, 2])
    
    with col_source:
        st.header("Project Artifacts")
        st.info(f"**HTML file loaded from:**\n`{file_path}`")
        
        with st.expander("View Source HTML Code"):
            st.code(html_content, language="html")
            
    with col_render:
        st.header("Live Rendered Publication Card")
        components.html(html_content, height=800, scrolling=True)
            
# --- Default State ---
if not generate_btn and "selected_essay" not in st.session_state:
    st.info("👈 Enter a topic in the sidebar and click 'Generate', or select an existing essay from the Published Gallery.")
```

### What
We import `streamlit` and its `components.v1` iframe builder. We configure the sidebar input layouts using `st.sidebar` and `st.text_input`. When the user clicks the primary trigger button, we run `run_publication_pipeline()`. If the file is successfully created in `output/essays/`, we read its text, wrap it in `components.html()`, and display it on the page.

### Why
Streamlit handles UI state binding, rendering, and thread loops in the background. It allows us to build a web dashboard in under 70 lines of Python without setting up separate node/react servers.

### Behind the Scenes
- `st.set_page_config()` updates the browser tab title and layout settings.
- `st.empty()` creates a placeholder box in the browser. This allows us to overwrite and update the status labels dynamically as stages progress.
- `components.html()` mounts an isolated iframe element inside the DOM. This protects the main Streamlit application layout from getting overridden by the custom background styles of our compiled essay.

### New Concepts
- **Streamlit Iframe mount:** Embedding custom compiled HTML outputs inside an isolated layout sandboxed frame.
- **Form Layout sidebars:** Declaring settings inputs inside a collapsing left margin container.

### Verify
Launch the Streamlit app locally inside your active terminal:

```powershell
streamlit run app.py
```

*Expected Terminal Logs:*
```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.10:8501
```

A new tab will automatically open in your web browser. Type a topic in the sidebar, click the blue button, and watch the multi-agent pipeline compile and render your page live!

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and commit the changes to GitHub:

```powershell
git add .
git commit -m "sprint 4: lesson 4.8 streamlit dashboard complete"
git push
```

### What
Staging, committing, and pushing the new Streamlit dashboard.

### Why
Prepares your online repository for the final Cloud Deployment step.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'streamlit'` | Streamlit was not installed, or you are running from outside the virtual environment. | Ensure you run `pip install streamlit` first. Verify your terminal shows `(.venv)` before running. |

---

## Key Takeaways

- Streamlit allows you to wrap CLI orchestration engines in a clean, visual browser UI.
- Use `st.components.v1.html()` to embed compiled HTML pages in isolated sandboxed frames.
- Place inputs in `st.sidebar` to preserve screen space for visual results.

---

## Next Lesson

[Lesson 4.9 - Streamlit Cloud Deployment](lesson_4_9_deployment.md) - Learn how to deploy your app live to the internet for free using Streamlit Community Cloud.
