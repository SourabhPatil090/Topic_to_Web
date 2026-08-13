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
