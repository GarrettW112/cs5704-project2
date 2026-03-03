import os
import json
import sys
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai


# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=api_key)


# ==========================================================
# 🥇 Agent 1: Receipt Extraction Agent
# ==========================================================
class ReceiptExtractionAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        self.generation_config = {
            "response_mime_type": "application/json",
            "response_schema": {
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
        }

    def run(self, image_path: str) -> dict:
        image = Image.open(image_path)

        prompt = """
        You are a receipt parsing system.

        Extract:
        - merchant name
        - purchase date (ISO format if possible)
        - items (raw_name exactly as printed, numeric price)
        - subtotal (if present)
        - tax (if present)
        - total

        Return valid JSON only.
        """

        response = self.model.generate_content(
            [prompt, image],
            generation_config=self.generation_config
        )

        return json.loads(response.text)


# ==========================================================
# 🥈 Agent 2: Normalization Agent
# ==========================================================
class ItemNormalizationAgent:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        self.generation_config = {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "raw_name": {"type": "string"},
                        "normalized_name": {"type": "string"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["raw_name", "normalized_name"]
                }
            }
        }

    def run(self, merchant: str, items: list) -> list:
        prompt = f"""
        You are a grocery receipt normalization system.

        Merchant: {merchant}

        Expand grocery abbreviations into full, human-readable product names.

        Examples:
        ORG BAN LG -> Organic Banana Large
        MLK 2% GL -> Milk 2 Percent Gallon
        BRD WHL WHT -> Whole Wheat Bread

        Use the merchant context to interpret abbreviations correctly.

        Return a JSON array.
        """

        raw_items_text = "\n".join([item["raw_name"] for item in items])

        response = self.model.generate_content(
            [prompt, raw_items_text],
            generation_config=self.generation_config
        )

        return json.loads(response.text)


# ==========================================================
# 🔄 Pipeline Orchestrator
# ==========================================================
class ReceiptPipeline:
    def __init__(self):
        self.extractor = ReceiptExtractionAgent()
        self.normalizer = ItemNormalizationAgent()

    def run(self, image_path: str) -> dict:
        # Stage 1: Extract
        extraction_result = self.extractor.run(image_path)

        # Stage 2: Normalize item names
        normalized_items = self.normalizer.run(
            extraction_result["merchant"],
            extraction_result["items"]
        )

        # Merge normalized names back into items
        normalization_lookup = {
            item["raw_name"]: item
            for item in normalized_items
        }

        for item in extraction_result["items"]:
            raw = item["raw_name"]
            if raw in normalization_lookup:
                item["normalized_name"] = normalization_lookup[raw]["normalized_name"]
                item["confidence"] = normalization_lookup[raw].get("confidence", None)
            else:
                item["normalized_name"] = raw
                item["confidence"] = 0.0

        return extraction_result


# ==========================================================
# CLI Entry
# ==========================================================
def main():
    if len(sys.argv) < 2:
        print("Usage: python receipt_pipeline.py <receipt_image>")
        sys.exit(1)

    image_path = sys.argv[1]

    pipeline = ReceiptPipeline()

    try:
        result = pipeline.run(image_path)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    main()