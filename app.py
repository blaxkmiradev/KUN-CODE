from flask import Flask, render_template, request, jsonify
from gemini_client import GeminiClient
from tools_ai import TOOLS_LIST, create_file, read_file, list_files, run_command
import os
import json
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
client = None
WORK_DIR = os.getcwd()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_client():
    global client
    if client:
        return client
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            client = GeminiClient(api_key=api_key)
            return client
        except Exception:
            return None
    return None

@app.route('/')
def index():
    has_key = os.getenv("GEMINI_API_KEY") is not None
    return render_template('index.html', has_key=has_key)

@app.route('/api/setup', methods=['POST'])
def setup():
    global client
    data = request.json
    api_key = data.get('api_key')
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400
    
    # Save to .env (simple approach for local dev)
    try:
        with open('.env', 'w') as f:
            f.write(f"GEMINI_API_KEY={api_key}")
        
        # Reload env and re-init client
        os.environ["GEMINI_API_KEY"] = api_key
        client = GeminiClient(api_key=api_key)
        return jsonify({"status": "success", "message": "API Key saved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    try:
        # List files in the WORK_DIR, excluding some ignored patterns
        files = []
        for root, dirs, filenames in os.walk(WORK_DIR):
            # Prune hidden dirs and pycache
            to_remove = [d for d in dirs if d.startswith('.') or d == '__pycache__']
            for d in to_remove:
                dirs.remove(d)
            
            for f in filenames:
                rel_path = os.path.relpath(os.path.join(root, f), WORK_DIR)
                if not rel_path.startswith('.') and '__pycache__' not in rel_path:
                    files.append(rel_path)
        return jsonify({"files": sorted(files), "work_dir": WORK_DIR})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

MODEL_MAPPING = {
    "kun-2.5-pro": "gemini-2.5-pro", 
    "kun-2.5-flash": "gemini-2.5-flash",
    "kun-2.5-lite": "gemini-2.5-flash-lite",
    "kun-2.0-pro": "gemini-2.5-pro",
    "kun-1.5-pro": "gemini-pro-latest",
    "kun-1.5-flash": "gemini-flash-latest",
    "kun-1.5-flash-8b": "gemini-flash-lite-latest"
}

@app.route('/api/model', methods=['POST'])
def set_model():
    current_client = get_client()
    if not current_client:
        return jsonify({"error": "Gemini API key is not configured."}), 403
    
    data = request.json
    kun_model_name = data.get('model')
    real_model_name = MODEL_MAPPING.get(kun_model_name)
    
    if real_model_name:
        try:
            current_client.switch_model(real_model_name)
            return jsonify({"status": "success", "model": kun_model_name})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid model name"}), 400

@app.route('/api/workspace', methods=['POST'])
def set_workspace():
    global WORK_DIR
    data = request.json
    new_path = data.get('path')
    if not new_path:
        return jsonify({"error": "No path provided"}), 400
    
    if os.path.isdir(new_path):
        WORK_DIR = os.path.abspath(new_path)
        return jsonify({"status": "success", "work_dir": WORK_DIR})
    else:
        return jsonify({"error": "Invalid directory path"}), 400

@app.route('/api/chat', methods=['POST'])
def chat():
    current_client = get_client()
    if not current_client:
        return jsonify({"error": "Gemini API key is not configured. Please go to Setup."}), 403

    data = request.json
    user_prompt = data.get('prompt')
    history = data.get('history', [])

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Simplistic implementation of iterative tool calling
        # In a robust version, we'd handle nested function calls correctly
        response = current_client.model.generate_content(
            user_prompt,
            tools=TOOLS_LIST
        )

        final_response_text = ""
        
        # Check for function calls
        if response.candidates[0].content.parts:
            parts = response.candidates[0].content.parts
            for part in parts:
                if part.function_call:
                    fn_name = part.function_call.name
                    args = part.function_call.args
                    
                    # Execute tool
                    tool_args = dict(part.function_call.args)
                    tool_args['base_dir'] = WORK_DIR
                    
                    if fn_name == 'create_file':
                        result = create_file(**tool_args)
                    elif fn_name == 'read_file':
                        result = read_file(**tool_args)
                    elif fn_name == 'list_files':
                        result = list_files(**tool_args)
                    elif fn_name == 'run_command':
                        result = run_command(**tool_args)
                    else:
                        result = f"Unknown tool: {fn_name}"
                    
                    # Send result back to model to get final response
                    # (Simplified loop: one level of tool calling for now)
                    second_response = current_client.model.generate_content(
                        [
                            {"role": "user", "parts": [user_prompt]},
                            response.candidates[0].content,
                            {
                                "role": "model",
                                "parts": [{
                                    "function_response": {
                                        "name": fn_name,
                                        "response": {"result": result}
                                    }
                                }]
                            }
                        ]
                    )
                    final_response_text = second_response.text
                else:
                    final_response_text = response.text

        return jsonify({
            "response": final_response_text,
            "status": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
