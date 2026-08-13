# Guide: Running Local Small Language Models (SLMs) with Ollama

When building multi-agent systems, agents frequently communicate, audit, and retry compile steps. This high-frequency API consumption can trigger **HTTP Error 429: Too Many Requests** rate limits or become expensive when using public cloud endpoints (like OpenRouter or OpenAI).

By running a **Small Language Model (SLM)** locally on your machine, you get:
1.  **Zero Cost:** Completely free to run with unlimited token limits.
2.  **No Rate Limits:** No rate limits (429 errors) since the server is running locally on your hardware.
3.  **Privacy & Offline Work:** All queries are processed on your local processor/graphics card without needing internet access.

This guide walks you through setting up **Ollama** and connecting it to your `Agent` pipeline.

---

## Step 1: Install Ollama

Ollama is a lightweight runner that allows you to download and run open-weights models locally.

### On Windows
You can install Ollama on Windows either using the graphical installer or directly from your terminal:

*   **Option A: PowerShell Command Install (Recommended)**
    Open PowerShell as an Administrator and execute the following install command:
    ```powershell
    irm https://ollama.com/install.ps1 | iex
    ```
*   **Option B: Graphical Installer**
    1. Go to the official website: [Ollama Download Page](https://ollama.com/download/windows).
    2. Download the Windows installer (`OllamaSetup.exe`).
    3. Run the installer and follow the prompt instructions.

Once installed, Ollama will start running in your Windows taskbar system tray (look for the llama icon).

### On macOS / Linux
*   **Mac:** Download the zip file from the Ollama homepage, unzip it, and drag the Ollama app to your `Applications` folder.
*   **Linux:** Run the following installation script in your terminal:
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

---

## Step 2: Download a Local SLM

For fast execution speeds on consumer hardware (laptops, PCs), we recommend using lightweight model sizes (1.5B to 8B parameters).

To get a model onto your system, Ollama offers two primary commands depending on whether you want to chat directly in the terminal or just download the files in the background:

### 1. `ollama pull <model>` (Download Only)
Use this command to download the model weights to your local machine without starting an active conversational session. This is the cleanest option when you just want to prepare a model to be queried later by your Python agent scripts.
```powershell
ollama pull gemma:2b-instruct-q4_K_M
```

### 2. `ollama run <model>` (Download & Chat in Terminal)
This command checks if you have the model downloaded. If you don't, it downloads it first. Then, it immediately loads the model into your system memory and launches an interactive chat prompt directly inside your terminal window.
```powershell
ollama run qwen2.5:1.5b
```
*Note: Type `/exit` inside the chat prompt to close the terminal session and return to your shell.*

---

### Recommended Models to use:
*   **Qwen 2.5 (1.5B Parameters) - Extremely Fast and Lightweight:**
    *   Command: `ollama pull qwen2.5:1.5b`
*   **Gemma (2B Parameter Instruct - Q4 Quantization) - Highly Optimized:**
    *   Command: `ollama pull gemma:2b-instruct-q4_K_M`
*   **Llama 3.2 (1B Parameter Instruct - Ultra Lightweight):**
    *   Command: `ollama pull llama3.2:1b`
*   **Llama 3.2 (3B Parameter Instruct - Q4 Quantization):**
    *   Command: `ollama pull llama3.2:3b-instruct-q4_K_M`
*   **Phi-3 (3.8B Parameter Instruct - Q4 Quantization):**
    *   Command: `ollama pull phi3:3.8b-instruct-q4_K_M`

*Note: The first time you pull a model, Ollama will download the model weights files (approximately 1GB to 2GB). Once complete, they will be registered locally and ready for immediate, instant redirection.*

---

## Step 3: Verify the Local Server is Active

Ollama starts a local background server listening on port `11434`.

To confirm the server is running, open your web browser and navigate to:
```text
http://localhost:11434
```
You should see a clean response page stating: **"Ollama is running"**.

---

## Step 4: Connecting the Agent to Ollama

Ollama has a built-in **OpenAI-compatible endpoint layout**. This means you do not need to install any new client libraries or custom SDKs! You can connect to Ollama using the exact same `urllib` HTTP POST request logic built in [Lesson 4.1 Base Agent](file:///f:/Lohnour-Pro/Apps/learning-agentic-ai/topic-to-web/sprint_4/lesson_4_1_base_agent.py).

### How the parameters map:
*   **API URL:** `http://localhost:11434/v1/chat/completions` (instead of OpenRouter).
*   **API Key:** Can be any dummy string (e.g. `"ollama"`), since local servers don't require authorization keys.
*   **Model Name:** Set this to the name of the model you downloaded (e.g., `"llama3.2"`).

### Code Integration Example:

To configure your agents to use Ollama, update the base `Agent` class constructor or load different values based on an `.env` toggle. 

Here is how you can modify `sprint_4/lesson_4_1_base_agent.py` to support local model redirection:

```python
class Agent:
    def __init__(self, name: str, system_instruction: str, tools: list = None):
        self.name = name
        self.system_instruction = system_instruction
        self.tools = tools or []
        self.messages = []
        
        # Check if we want to run locally or in the cloud using an environment variable
        USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
        
        if USE_LOCAL_LLM:
            # 1. Local Ollama Settings
            self.url = "http://localhost:11434/v1/chat/completions"
            self.model = os.getenv("LOCAL_MODEL_NAME", "qwen2.5:1.5b")
            self.api_key = "ollama"  # Ollama does not require real keys
        else:
            # 2. OpenRouter Cloud Settings
            self.url = "https://openrouter.ai/api/v1/chat/completions"
            self.model = "poolside/laguna-m.1:free"
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError(f"[{self.name}] Error: OPENROUTER_API_KEY missing.")
```

### Environment Config setup (`.env`):
Simply add these lines to your `.env` configuration file to toggle between cloud and local SLM processing instantly:

```ini
# Toggle local SLM processing
USE_LOCAL_LLM=true
LOCAL_MODEL_NAME=qwen2.5:1.5b
```

---

## Step 5: Test Execution

Relaunch your Streamlit web application dashboard or run the orchestrator script:

```powershell
python sprint_4/lesson_4_7_orchestrator.py
```

*   Watch your terminal/app logs. You should see agent generation operations execute immediately with **zero network lag** and **zero 429 HTTP rate-limit errors**!
