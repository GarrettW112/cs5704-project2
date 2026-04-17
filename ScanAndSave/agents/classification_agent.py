import json
from .base_agent import BaseAgent

class GroceryClassificationAgent(BaseAgent):
    def __init__(self):
        schema = {
            "type": "object", 
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "normalized_name": {"type": "string"},
                            "category": {
                                "type": "string",
                                "enum": [
                                    "Produce", "Dairy", "Meat & Seafood", "Bakery",
                                    "Frozen", "Pantry", "Snacks", "Beverages",
                                    "Household", "Personal Care", "Other"
                                ]
                            },
                            "subcategory": {"type": "string"},
                            "confidence": {"type": "number"}
                        },
                        "required": ["normalized_name", "category", "subcategory", "confidence"],
                        "additionalProperties": False 
                    }
                }
            },
            "required": ["items"],
            "additionalProperties": False
        }

        super().__init__(schema, "GroceryClassification")

    def run(self, items: list):
        prompt = """
        Classify each grocery item into the specified categories.
        Return JSON only.
        """

        text = "\n".join([item["normalized_name"] for item in items])

        result = self.generate(prompt, text)
        
        return json.loads(result).get("items", [])