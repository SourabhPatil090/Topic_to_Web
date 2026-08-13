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
        
    # Test 3: Valid JSON syntax, but missing required key (theme)
    missing_keys = """
    {
      "detected_sentiment": "joyful",
      "layout_style": "spacious"
    }
    """
    try:
        print("Testing JSON with missing keys...")
        validate_designer_json(missing_keys)
    except ValueError as e:
        print(f"Test 3 Caught Schema Error:\n{e}\n")
