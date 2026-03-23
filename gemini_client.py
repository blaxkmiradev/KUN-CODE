import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please provide it in the .env file.")
        
        genai.configure(api_key=self.api_key)
        self.switch_model('gemini-2.5-flash')

    def switch_model(self, model_name):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def generate_response(self, prompt, history=[]):
        chat = self.model.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text, chat.history

    def generate_with_tools(self, prompt, tools, history=[]):
        # This will be used for agentic behavior with function calling
        chat = self.model.start_chat(history=history or [])
        response = chat.send_message(prompt, tools=tools)
        return response
