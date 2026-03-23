# Kun Code Entry Point
import os
import sys

# Change directory to the app location if needed
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == "__main__":
    print("--- KUN CODE STARTING ---")
    print("Access the IDE at http://127.0.0.1:5000")
    print("Make sure you have set GEMINI_API_KEY in your environment or .env file.")
    app.run(debug=True, port=5000)