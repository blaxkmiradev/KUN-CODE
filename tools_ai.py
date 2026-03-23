import os
import subprocess

def create_file(path, content, base_dir='.'):
    """Creates a file with the given content."""
    try:
        full_path = os.path.join(base_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created file: {path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def read_file(path, base_dir='.'):
    """Reads the content of a file."""
    try:
        full_path = os.path.join(base_dir, path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path='.', base_dir='.'):
    """Lists files in the given directory."""
    try:
        full_path = os.path.join(base_dir, path)
        items = os.listdir(full_path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def run_command(command, base_dir='.'):
    """Runs a shell command and returns the output."""
    try:
        # Use shell=True for convenience, but be mindful of security in a real app
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=base_dir)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except Exception as e:
        return f"Error running command: {str(e)}"

# Define tool metadata for Gemini function calling
TOOLS_LIST = [
    create_file,
    read_file,
    list_files,
    run_command
]
