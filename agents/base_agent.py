import google.generativeai as genai
from config import MODEL_NAME


class BaseAgent:
    def __init__(self, schema):
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.generation_config = {
            "response_mime_type": "application/json",
            "response_schema": schema
        }

    def generate(self, inputs):
        response = self.model.generate_content(
            inputs,
            generation_config=self.generation_config
        )
        return response.text