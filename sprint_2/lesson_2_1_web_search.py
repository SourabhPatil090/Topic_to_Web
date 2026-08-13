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
