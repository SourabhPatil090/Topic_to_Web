# Lesson 2.4 - JSON Schema Validation

## Objective

Build an **accumulative error validation checker** function that cleans string outputs, verifies JSON syntax structure, checks for nested configuration keys, and accumulates all issues into a single error report to optimize agent self-correction.

---

## Why

When connecting multiple agents in a pipeline, we often require structured data exchanges (like our Designer Agent outputting style configurations). However, LLMs are text models—they can easily output invalid JSON strings containing trailing commas, missing quotes, markdown wrappers (like ` ```json `), or missing keys. 

If we use a simple "fail-fast" check that stops at the very first key mismatch, the LLM will have to run multiple API calls (one for each missing key) to fix them. By building an **Accumulative Error validation** system, we compile every single formatting and schema issue into one comprehensive error list. This allows the LLM to self-correct all issues in a single retry loop, saving substantial token costs and processing time.

---

## What We Are Building

A Python script (`lesson_2_4_json_validation.py`) containing the validation checker function:
*   `validate_designer_json(raw_text)`: Standardizes the input string by stripping markdown wrapper blocks, parses it using native JSON libraries, and uses an internal list to collect all missing or malformed keys (primary and nested under `theme`). It returns the parsed dictionary if valid, or raises a combined `ValueError` containing the entire error list.

---

## Architecture

```text
[Raw LLM Output] ──► [Standardize String] (strips ```json wrappers)
                           │
                           ▼
                     [json.loads()] ──(JSONDecodeError?)──► [Raise ValueError]
                           │ (valid JSON syntax)
                           ▼
                 [validation_errors = []] (initialize list)
                           │
                           ├─► Check key presence ──► (Missing?) ──► [Append to list]
                           │
                           ▼
                     (List Empty?)
                      /         \
                 (Yes)           (No)
                  /                 \
        [Return parsed dict]    [Raise combined ValueError]
```

---

## Prerequisites

- Complete Lesson 2.3.
- Virtual environment activated (`(.venv)` visible in terminal).

---

## Step 1: Create the JSON Validation Script

### Do

Create a file named `sprint_2/lesson_2_4_json_validation.py` and write the following code:

```python
import json

# Define the expected JSON Schema keys for the Designer output
REQUIRED_KEYS = ["detected_sentiment", "theme", "layout_style"]
REQUIRED_THEME_KEYS = ["background_color", "primary_text", "accent_color", "font_family_heading", "font_family_body"]

def validate_designer_json(raw_text: str) -> dict:
    """
    Cleans raw text, parses it as JSON, and validates that it contains
    all required schema keys for the Designer Agent.
    Collects all errors into a list to provide accumulative feedback.
    """
    cleaned_text = raw_text.strip()
    
    # 1. Strip Markdown code block wrappers if present (e.g. ```json ... ```)
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]  # Slice out starting marker
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]  # Slice out ending marker
        
    cleaned_text = cleaned_text.strip()
    
    # 2. Attempt JSON Deserialization
    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as je:
        raise ValueError(f"JSON Syntax Error: Failed to parse string. Detail: {je}")
        
    # 3. Check for dictionary object type
    if not isinstance(data, dict):
        raise ValueError("JSON Schema Error: Output must be a JSON object (dictionary), not a list or basic value.")
        
    # Initialize a list to accumulate schema errors
    validation_errors = []

    # 4. Validate presence of primary required keys
    for key in REQUIRED_KEYS:
        if key not in data:
            validation_errors.append(f"Missing required primary key: '{key}'")
            
    # 5. Validate presence of nested theme keys
    theme = data.get("theme")
    if not isinstance(theme, dict):
        validation_errors.append("Missing or invalid 'theme' configuration dictionary.")
    else:
        for t_key in REQUIRED_THEME_KEYS:
            if t_key not in theme:
                validation_errors.append(f"Missing required theme configuration key: 'theme.{t_key}'")
                
    # If any errors were accumulated, raise a combined exception report
    if validation_errors:
        combined_error_msg = "JSON Schema Validation Failed:\n" + "\n".join(f"- {err}" for err in validation_errors)
        raise ValueError(combined_error_msg)
            
    return data

# --- Local Testing Block ---
if __name__ == "__main__":
    print("=== Testing JSON Validation Guardrails ===\n")
    
    # Test 1: Valid formatted JSON with Markdown wrappers
    valid_input = """
    ```json
    {
      "detected_sentiment": "melancholic_optimism",
      "theme": {
        "background_color": "#1a1c23",
        "primary_text": "#e2e8f0",
        "accent_color": "#cca43b",
        "font_family_heading": "'Playfair Display', serif",
        "font_family_body": "'Inter', sans-serif"
      },
      "layout_style": "minimalist-single-column-spacious"
    }
    ```
    """
    try:
        print("Testing valid JSON input...")
        parsed_data = validate_designer_json(valid_input)
        print("Test 1 Result: Successful parse and validation!")
        print(f"Parsed Background: {parsed_data['theme']['background_color']}\n")
    except ValueError as e:
        print(f"Test 1 Failed: {e}\n")
        
    # Test 2: Invalid JSON Syntax (missing comma)
    invalid_syntax = """
    {
      "detected_sentiment": "joyful"
      "theme": {}
    }
    """
    try:
        print("Testing invalid JSON syntax (missing comma)...")
        validate_designer_json(invalid_syntax)
    except ValueError as e:
        print(f"Test 2 Caught Syntax Error:\n{e}\n")
        
    # Test 3: Multiple Missing Keys (testing accumulative errors)
    missing_keys = """
    {
      "detected_sentiment": "joyful",
      "theme": {
        "background_color": "#ffffff"
      }
    }
    """
    try:
        print("Testing JSON with multiple missing keys...")
        validate_designer_json(missing_keys)
    except ValueError as e:
        print(f"Test 3 Caught Accumulative Schema Error:\n{e}\n")
```

### What
We define key validation lists. We write `validate_designer_json()` to clean Markdown wrappers, run `json.loads()`, and loop through the required keys. Instead of raising immediately, we append error strings to `validation_errors = []` and throw a combined message if the list is not empty.

### Why
Accumulative validation packages all error feedback together. This is a critical design pattern for agent self-correction: returning a single, unified list of fixes prevents the LLM from executing repeated, expensive feedback loop API calls.

### Behind the Scenes
- `.startswith("```json")` and `.endswith("```")` check string boundary markers. We use Python slicing index offsets `[7:]` and `[:-3]` to remove them.
- `validation_errors.append(f"...")` appends a string message to our list in RAM.
- `"\n".join(...)` joins all the list elements together with a line break to present a clean, bulleted error description to the LLM.

### New Concepts
- **Accumulative Error Checking:** Compiling multiple verification failures into a single report rather than failing instantly.
- **Agent Self-Correction Loop:** Designing feedback prompts containing error summaries to instruct the LLM on how to fix its output.
- **Type Safety Checks (`isinstance`):** Verifying that nested JSON structures are the correct type (dictionaries) before trying to index them.

### Verify
Run the script directly in your terminal:

```powershell
python sprint_2/lesson_2_4_json_validation.py
```

*Expected Output:*
```text
=== Testing JSON Validation Guardrails ===

Testing valid JSON input...
Test 1 Result: Successful parse and validation!
Parsed Background: #1a1c23

Testing invalid JSON syntax (missing comma)...
Test 2 Caught Syntax Error:
JSON Syntax Error: Failed to parse string. Detail: Expecting ',' delimiter: line 4 column 7 (char 42)

Testing JSON with multiple missing keys...
Test 3 Caught Accumulative Schema Error:
JSON Schema Validation Failed:
- Missing required primary key: 'layout_style'
- Missing required theme configuration key: 'theme.primary_text'
- Missing required theme configuration key: 'theme.accent_color'
- Missing required theme configuration key: 'theme.font_family_heading'
- Missing required theme configuration key: 'theme.font_family_body'
```

---

## Step 2: Commit and Push to GitHub

### Do

Save your code and sync your files to GitHub:

```powershell
git add .
git commit -m "sprint 2: lesson 2.4 json validation with accumulative errors complete"
git push
```

### What
Staging, committing, and pushing the new code.

### Why
Saves version milestones.

---

## Common Mistakes

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `TypeError: 'NoneType' object is not iterable` | Accessing nested theme values without checking if theme is a dictionary. | Ensure you run `isinstance(theme, dict)` before checking for sub-keys. |

---

## Key Takeaways

- Slices strings to remove markdown ` ```json ` and ` ``` ` wrappers.
- Wrap `json.loads()` inside a try/except block to catch bad syntax safely.
- Use list arrays to collect all schema errors. Return a single combined error report to minimize LLM rate-limit and token costs.

---

## Next Lesson

[Lesson 3.1 - Tool Schemas (Sprint 3)](../sprint-3-ttw/lesson_3_1_schemas.md) - Learn how to define JSON Schemas describing your tools to the LLM.
