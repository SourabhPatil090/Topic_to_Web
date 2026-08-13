# Lesson 2.1 - `web_search` Tool Function

## Objective

Build a standalone, reusable Python tool function that queries an external search engine API (Tavily or Serper) to gather search context, parses the JSON payload response, and formats the results into a consolidated text output.

---

## Why

Specialist agents cannot rely solely on their internal pre-trained knowledge base to research modern topics. They need the ability to search the live web to fetch factual context, extract summaries, and reference up-to-date data. Wrapping this API call in a clean, self-contained Python function creates a tool that our Researcher Agent can call dynamically at runtime.

---

## What We Are Building

A Python function (`web_search`) inside `sprint_2/lesson_2_1_web_search.py`. 

The function reads a search API key from your `.env` configuration, executes an HTTP request to the search engine (defaulting to Tavily, with Serper as a fallback), parses the returned JSON, and formats the top results (title, URL, and snippet content) into a unified string.

---

## Architecture

```text
+-------------------+
|  Researcher Agent |
|  (Passes Query)   |
+---------+---------+
          | (calls tool function)
          v
+---------+---------+      HTTP POST (JSON)     +--------------------+
|    web_search()   | ────────────────────────> |     Search API     |
|   Tool Function   | <──────────────────────── |  (Tavily / Serper) |
+-------------------+      JSON Response        +--------------------+
```

---

## Prerequisites

- Complete Sprint 1.
- Have a Tavily API Key (or Serper API Key) configured in your `.env` file at your workspace root:
  ```env
  TAVILY_API_KEY=your_actual_tavily_key_here
  # OR (for Serper fallback):
  SERPER_API_KEY=your_actual_serper_key_here
  ```

---

## Step 1: Write the Tool Function

### Do

Create a new directory named `sprint_2/` in the root of your project. 

Create a file named `sprint_2/lesson_2_1_web_search.py` and write the following code:

```python
import os
import json
import urllib.request
from dotenv import load_dotenv

# Load environmental variables locally for testing
load_dotenv()

def web_search(query: str, max_results: int = 3) -> str:
    """
    Queries Tavily (or Serper fallback) search API and returns a formatted text summary of results.
    """
    # 1. Retrieve Tavily Key
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if tavily_key:
        # Construct Tavily API Request
        url = "https://api.tavily.com/search"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "api_key": tavily_key,
            "query": query,
            "max_results": max_results
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                # Format the Tavily search results into a clean string
                formatted_results = []
                for idx, item in enumerate(result.get("results", []), 1):
                    title = item.get("title", "No Title")
                    url_link = item.get("url", "No URL")
                    content = item.get("content", "No Content")
                    
                    formatted_results.append(
                        f"[{idx}] Title: {title}\n    URL: {url_link}\n    Summary: {content}\n"
                    )
                
                if not formatted_results:
                    return "No search results found."
                    
                return "\n".join(formatted_results)
                
        except Exception as e:
            return f"Error executing Tavily search: {e}"
            
    # 2. Retrieve Serper Key (Fallback)
    serper_key = os.getenv("SERPER_API_KEY")
    
    if serper_key:
        # Construct Serper API Request
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": serper_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": max_results
        }
        
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                # Format the Serper organic search results into a clean string
                formatted_results = []
                for idx, item in enumerate(result.get("organic", []), 1):
                    title = item.get("title", "No Title")
                    url_link = item.get("link", "No URL")
                    snippet = item.get("snippet", "No Snippet")
                    
                    formatted_results.append(
                        f"[{idx}] Title: {title}\n    URL: {url_link}\n    Summary: {snippet}\n"
                    )
                
                if not formatted_results:
                    return "No search results found."
                    
                return "\n".join(formatted_results)
                
        except Exception as e:
            return f"Error executing Serper search: {e}"
            
    return "Error: No valid Search API keys (TAVILY_API_KEY or SERPER_API_KEY) configured."

# --- Local Testing Block ---
# This block only runs when we execute the script directly, not when we import it.
if __name__ == "__main__":
    test_query = "AI impacts on software developer jobs"
    print(f"Testing search tool with query: '{test_query}'...\n")
    search_output = web_search(test_query)
    print("=== Search Output ===")
    print(search_output)
    print("=====================")
```

### What
We are writing a standalone function `web_search()` that checks `.env` configuration keys, constructs HTTP POST headers and body dictionaries tailored for either Tavily or Serper, executes the HTTP request, parses the returned JSON, loops through the organic results array, and formats them into a readable text block. We wrap our testing block in `if __name__ == "__main__":`.

### Why
By keeping this function self-contained, we can import it directly into our future agents. Wrapping the testing execution block in `if __name__ == "__main__":` ensures we can run and test this file in isolation, but when other scripts import this file, the testing code is automatically skipped.

### Behind the Scenes
- When you run a file directly, Python sets a special internal variable `__name__` to the string `"__main__"`. If the file is imported by another script, `__name__` is set to the name of the file module itself.
- Tavily returns summary snippets directly in the `"content"` key of its results. Serper (which scrapes organic Google pages) returns snippets in the `"snippet"` key under the `"organic"` array. We handle both custom shapes.

### New Concepts
- **`__main__` Guard Block:** Code guard pattern that ensures testing routines do not run when a file is imported as a package.
- **API Payload Normalization:** Parsing different API payload shapes (Tavily vs. Serper) and outputting a single, consistent data type (our formatted string).

### Verify
Run the script directly in your terminal:

```powershell
python sprint_2/lesson_2_1_web_search.py
```

*Expected Output (results will vary based on current web data):*
```text
Testing search tool with query: 'AI impacts on software developer jobs'...

=== Search Output ===
[1] Title: How Generative AI Is Changing Software Developer Jobs - Forbes
    URL: https://www.forbes.com/sites/forbeshumanresourcescouncil/...
    Summary: Generative AI is transforming the role of developers, automating boilerplate code generation and changing how teams debug...

[2] Title: The Future of Software Developers in the Age of AI
    URL: https://example.com/future-developers-ai
    Summary: Statistics show that developer job demand remains high, but shifting from syntax-writing to architecture and auditing...
=====================
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your changes and push the new sprint files to GitHub:

```powershell
git add .
git commit -m "sprint 2: lesson 2.1 web search tool complete"
git push
```

### What
Saving local edits and uploading changes to the remote branch on GitHub.

### Why
Keeps version milestones synced and ready for compilation.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Returns "Error: No valid Search API keys configured" | Missing keys in `.env` or run from wrong directory. | Verify your `.env` contains either `TAVILY_API_KEY` or `SERPER_API_KEY`. Make sure terminal path is in `topic-to-web/`. |

---

## Key Takeaways

- Wrap utility operations in functions to create reusable "tools" for your agents.
- Use `if __name__ == "__main__":` to separate test scripts from utility imports.
- Normalizing API response structures allows you to swap backend APIs (Tavily to Serper) without breaking the client code.

---

## Next Lesson

[Lesson 2.2 - File I/O Tools](lesson_2_2_file_io.md) - Learn how to build secure file reading and writing functions that contain path-escape guardrails.
