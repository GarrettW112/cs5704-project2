import json
from PIL import Image
from .base_agent import BaseAgent
from ScanAndSave.config import VISION_MODEL_NAME


class ReceiptExtractionAgent(BaseAgent):
    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "merchant": {"type": "string"},
                "date": {"type": ["string", "null"]},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "raw_name": {"type": "string"},
                            "price": {"type": "number"}
                        },
                        "required": ["raw_name", "price"],
                        "additionalProperties": False
                    }
                },
                "subtotal": {"type": ["number", "null"]},
                "tax": {"type": ["number", "null"]},
                "total": {"type": "number"}
            },
            "required": ["merchant", "date", "items", "subtotal", "tax", "total"],
            "additionalProperties": False
        }

        super().__init__(schema, "ReceiptExtraction")

        self.model = VISION_MODEL_NAME

    def run(self, image_path: str):
        image = Image.open(image_path)

        prompt = """
        Extract receipt data including merchant, date,
        items, subtotal, tax, and total. 
        If a field like tax or date is completely missing, return null for it.
        Return JSON only.
        """

        result = self.generate(prompt, image)
        return json.loads(result)