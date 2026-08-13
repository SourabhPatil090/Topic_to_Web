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