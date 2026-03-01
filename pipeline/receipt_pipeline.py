from agents.extraction_agent import ReceiptExtractionAgent
from agents.normalization_agent import ItemNormalizationAgent
from agents.classification_agent import GroceryClassificationAgent


class ReceiptPipeline:
    def __init__(self):
        self.extractor = ReceiptExtractionAgent()
        self.normalizer = ItemNormalizationAgent()
        self.classifier = GroceryClassificationAgent()

    def run(self, image_path: str):
        extraction = self.extractor.run(image_path)

        normalized = self.normalizer.run(
            extraction["merchant"],
            extraction["items"]
        )

        norm_lookup = {i["raw_name"]: i for i in normalized}

        for item in extraction["items"]:
            raw = item["raw_name"]
            item["normalized_name"] = norm_lookup.get(raw, {}).get("normalized_name", raw)

        classified = self.classifier.run(extraction["items"])

        class_lookup = {i["normalized_name"]: i for i in classified}

        for item in extraction["items"]:
            norm = item["normalized_name"]
            item["category"] = class_lookup.get(norm, {}).get("category", "Other")
            item["subcategory"] = class_lookup.get(norm, {}).get("subcategory", "")

        return extraction