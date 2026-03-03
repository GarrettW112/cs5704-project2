import json
from PIL import Image
from .base_agent import BaseAgent


class ReceiptExtractionAgent(BaseAgent):
    def __init__(self):
        schema = {
            "type": "object",
            "properties": {
                "merchant": {"type": "string"},
                "date": {"type": "string"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "raw_name": {"type": "string"},
                            "price": {"type": "number"}
                        },
                        "required": ["raw_name", "price"]
                    }
                },
                "subtotal": {"type": "number"},
                "tax": {"type": "number"},
                "total": {"type": "number"}
            },
            "required": ["merchant", "items", "total"]
        }

        super().__init__(schema)

    def run(self, image_path: str):
        image = Image.open(image_path)

        prompt = """
        Extract receipt data including merchant, date,
        items (raw_name exactly as printed and numeric price),
        subtotal, tax, and total.
        Return JSON only.
        """

        result = self.generate([prompt, image])
        return json.loads(result)