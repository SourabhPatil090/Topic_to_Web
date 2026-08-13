# Lesson 4.9 - Streamlit Cloud Deployment

## Objective

Deploy your multi-agent publication dashboard live to the internet for free using Streamlit Community Cloud, configure secure environment secrets, and obtain a public URL to share your work.

---

## Why

Developing locally is great for coding, but to share your work with colleagues or showcase it at a hackathon, the app must be accessible live on the web. Streamlit Community Cloud provides free, instant hosting directly from your GitHub repository. 

To deploy securely, we must never commit API keys to our public GitHub code repository. We will configure Streamlit's built-in **Secrets Manager** to store our keys securely in the cloud environment.

---

## What We Are Building

1.  A **`requirements.txt`** file in the workspace root, listing the exact Python libraries (`streamlit`, `python-dotenv`) the cloud server must install.
2.  A guide walking through pushing your code to GitHub, connecting to Streamlit Cloud, and setting up environment variables securely.

---

## Prerequisites

- Complete Lesson 4.8.
- A free GitHub account.
- Your project pushed to a public or private GitHub repository.

---

## Step 1: Create the Requirements Configuration

Streamlit Cloud reads a `requirements.txt` file to understand which third-party packages must be installed before running `app.py`.

### Do

Create a file named `requirements.txt` in the **root directory** of your workspace and write the following dependencies:

```text
streamlit>=1.30.0
python-dotenv>=1.0.0
```

---

## Step 2: Push Your Code to GitHub

Ensure all your Sprint 4 changes and code files are committed and pushed to your remote repository:

```powershell
git add .
git commit -m "Sprint 4 Complete: App and requirements ready for deploy"
git push
```

---

## Step 3: Deploy to Streamlit Community Cloud

### Do

1.  Open your browser and navigate to [share.streamlit.io](https://share.streamlit.io).
2.  Click **"Sign in with GitHub"** and authorize Streamlit using your GitHub credentials.
3.  Once logged in to your Streamlit dashboard, click the blue **"Create app"** button.
4.  In the deployment form, configure the settings using one of these two options:

    *   **Option A: Interactive Picker (Recommended)**
        *   If Streamlit shows three dropdown menus (Repository, Branch, Main file path), simply select your repository (e.g. `topic-to-web`), set the branch to `main` (or `master`), and type `app.py` in the main file path.
        *   *Note: If your repository is Private and doesn't show in the list, click the link to switch to URL input, or authorize Streamlit access to private repos in your GitHub settings.*

    *   **Option B: Direct File URL Input**
        *   If Streamlit shows a single "GitHub URL" input box, you must paste the direct path to the main application file:
            `https://github.com/your-username/topic-to-web/blob/main/app.py`
            *(Replace `main` with `master` if that is your active Git branch name).*

5.  **CRITICAL STEP: Set Environment Secrets**
    *   Before clicking deploy, click the **"Advanced settings..."** link at the bottom of the form.
    *   In the **Secrets** text box, delete any placeholder text.
    *   Paste your OpenRouter and Tavily keys using valid **TOML** format. 
        > [!IMPORTANT]
        > In TOML format, key values **must** be wrapped in double quotes `""`. Leaving quotes out will result in deployment syntax crashes.
        
        ```toml
        OPENROUTER_API_KEY = "your-actual-openrouter-key-here"
        TAVILY_API_KEY = "your-actual-tavily-key-here"
        ```
    *   Set the **Python version** dropdown at the top to a stable version (like **`3.11`** or **`3.12`**) instead of pre-release versions to prevent dependency errors.
    *   Click **"Save"**.
6.  Click **"Deploy!"**.

---

## Modifying Secrets After Deployment

If you need to change your API keys or update settings later, you do not need to redeploy:
1.  Go to your Streamlit Cloud dashboard at [share.streamlit.io](https://share.streamlit.io).
2.  Click the three dots `...` menu next to your running application.
3.  Click **"Settings"** and select the **"Secrets"** tab in the sidebar.
4.  Update your keys in the text area and click **"Save"**. The cloud container will hot-reload your app automatically in under 10 seconds.

---

## Behind the Scenes

*   **Dependency Resolution:** When Streamlit Cloud boots up your app container, it runs `pip install -r requirements.txt` automatically.
*   **Secrets Decoupling:** In Python, `os.getenv("OPENROUTER_API_KEY")` automatically intercepts the keys defined in the Streamlit Secrets manager panel. This allows the exact same code to run locally (reading `.env`) and in the cloud (reading Streamlit Secrets) without making any modifications!
*   **Active Container:** Streamlit Cloud hosts your app on a container. If you make updates to your GitHub repository and run `git push`, Streamlit detects the commit and hot-reloads the live website automatically in 5 seconds.

---

## Verify

Once the deployment logs finish compiling (usually takes 1-2 minutes on first boot), your web page will display:

`✅ Multi-Agent Pipeline Completed Successfully!`

Copy the public URL from the address bar (e.g., `https://topic-to-web.streamlit.app`) and share it with your students and colleagues!

---

## Key Takeaways

- Use `requirements.txt` to manage dependencies in cloud environments.
- **Never commit `.env` or API keys to GitHub.** Use Streamlit Advanced Secrets to configure keys securely.
- Streamlit Cloud automatically rebuilds and deploys updates whenever you push code to GitHub.

---

## Congratulations! 🎉

You have completed the entire **TopicToWeb Multi-Agent Pipeline** curriculum! 
You built security guardrails, JSON validation engines, custom tool call routes, an autonomous single agent loop, an object-oriented multi-agent pipeline, and successfully launched it live in the cloud.

Good luck with your hackathon!
