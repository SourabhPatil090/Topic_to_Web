# Lesson 2.2 - File I/O Tools

## Objective

Build secure, path-escaped functions for reading and writing files within your project directory to create tools that your agents can use without risking directory escape vulnerability.

---

## Why

Specialist agents like the Developer Agent (which writes code) and the Reviewer Agent (which reads code) need access to the disk. However, if you simply expose raw Python `open()` functions to an LLM, the model could easily input absolute paths or relative escape paths (like `../../windows/system32/` or `../../etc/passwd`) and read or corrupt files outside your project. We must build secure wrapper functions that programmatically validate paths before reading or writing.

---

## What We Are Building

A Python script (`lesson_2_2_file_io.py`) containing two core functions:
1.  `read_file(file_path)`: Reads a file and returns its string contents.
2.  `write_file(file_path, content)`: Creates or overwrites a file with the given content.

Both functions are restricted to a relative `working_dir` (defaulting to the `output/` directory) and use path validation to prevent escape attacks.

---

## Architecture

```text
+---------------------+
|     Agent Call      |
+----------+----------+
           | (passes "output/index.html")
           v
+----------+----------+      Path Validation Check      +----------------------+
|  read_file() /      | ──────────────────────────────> | Write Allowed? (Yes) |
|  write_file() Tools | <────────────────────────────── |  Proceed to Disk     |
+---------------------+    Escapes Workspace? (No)      +----------------------+
```

---

## Prerequisites

- Complete Lesson 2.1.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the Secure File Utility Script

### Do

Create a file named `sprint_2/lesson_2_2_file_io.py` and write the following code:

```python
import os

# Define the absolute path of the workspace root and the allowed output folder
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ALLOWED_DIR = os.path.join(BASE_DIR, "output")

def safe_path(relative_path: str) -> str:
    """
    Validates that the target path resolves safely inside the ALLOWED_DIR.
    Returns the absolute path if safe; raises ValueError if unsafe.
    """
    # Join target path to Allowed Directory and resolve its absolute path
    target_abs = os.path.abspath(os.path.join(ALLOWED_DIR, relative_path))
    
    # Check if the resolved path starts with the allowed directory prefix
    # This prevents directory traversal attacks like ../../
    if not target_abs.startswith(ALLOWED_DIR):
        raise ValueError(f"Security Alert: Blocked access to path outside allowed directory: {relative_path}")
        
    return target_abs

def read_file(file_path: str) -> str:
    """
    Safely reads file contents from inside the allowed directory.
    """
    try:
        abs_path = safe_path(file_path)
        
        if not os.path.exists(abs_path):
            return f"Error: File '{file_path}' does not exist."
            
        if os.path.isdir(abs_path):
            return f"Error: Target path '{file_path}' is a directory, not a file."
            
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(file_path: str, content: str) -> str:
    """
    Safely writes content to a file inside the allowed directory,
    automatically creating parent directories if they do not exist.
    """
    try:
        abs_path = safe_path(file_path)
        
        # Ensure parent directories exist
        parent_dir = os.path.dirname(abs_path)
        os.makedirs(parent_dir, exist_ok=True)
        
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Success: File '{file_path}' written successfully."
        
    except Exception as e:
        return f"Error writing file: {e}"

# --- Local Testing Block ---
if __name__ == "__main__":
    # Ensure allowed directory exists for our local tests
    os.makedirs(ALLOWED_DIR, exist_ok=True)
    
    print("=== Testing Safe File I/O Tools ===\n")
    
    # 1. Test Safe Write
    write_result = write_file("essays/test_essay.txt", "Topic: Space exploration is a journey of hope.")
    print(f"Write Test: {write_result}")
    
    # 2. Test Safe Read
    read_result = read_file("essays/test_essay.txt")
    print(f"Read Test Output:\n'{read_result}'\n")
    
    # 3. Test Security Guardrail (Directory Escape Attack)
    print("Attempting directory escape attack...")
    attack_path = "../secrets.txt"
    attack_result = write_file(attack_path, "This should be blocked!")
    print(f"Escape Attack Result: {attack_result}")
```

### What
We define a path validation function `safe_path()` using `os.path.abspath()`. It compares target path prefixes against the allowed `output` directory. We build wrappers `read_file()` and `write_file()` that validate inputs against `safe_path()`, handle exceptions gracefully, and return clean strings.

### Why
By using `os.path.abspath()`, Python resolves all relative path modifiers (`..` and `.`) out of the string before comparisons occur. Checking `.startswith()` blocks directory traversal attacks.

### Behind the Scenes
- `__file__` is a special variable containing the path of the script currently executing. `os.path.dirname(__file__)` gets its parent folder.
- `os.path.abspath()` resolves symlinks, standardizes folder separators, and expands relative segments into absolute paths based on the OS.
- `os.makedirs(..., exist_ok=True)` recursively creates all required folders (like `essays/` inside `output/`) without throwing an error if the directory already exists.

### New Concepts
- **Directory Traversal Attack:** An exploit targeting directories to access files outside the application root directory.
- **Path Resolution:** Expanding relative references into their absolute target filesystem keys.
- **File I/O Streams:** Opening stream pipes to write or read file bytes to disk.

### Verify
Run the script directly in your terminal:

```powershell
python sprint_2/lesson_2_2_file_io.py
```

*Expected Output:*
```text
=== Testing Safe File I/O Tools ===

Write Test: Success: File 'essays/test_essay.txt' written successfully.
Read Test Output:
'Topic: Space exploration is a journey of hope.'

Attempting directory escape attack...
Escape Attack Result: Error writing file: Security Alert: Blocked access to path outside allowed directory: ../secrets.txt
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your files and sync your repository changes:

```powershell
git add .
git commit -m "sprint 2: lesson 2.2 file io tools complete"
git push
```

### What
Staging, committing, and pushing the new code updates.

### Why
Ensures that all system helpers are versioned.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| Security alert occurs during legitimate file writes | Supplying absolute paths (like `C:/Users/...`) instead of relative paths (like `essays/text.html`). | Ensure that all paths passed into `write_file()` or `read_file()` are written relative to the output folder. |

---

## Key Takeaways

- Never expose raw Python file operations directly to an LLM agent.
- Use `os.path.abspath()` to resolve traversal characters before evaluating paths.
- Enforce prefix validation (`.startswith()`) to implement workspace guardrails.

---

## Next Lesson

[Lesson 2.3 - Input Shield & Data Truncation](lesson_2_3_guardrails.md) - Learn how to block unsafe inputs and programmatically slice text lengths to control context tokens.
