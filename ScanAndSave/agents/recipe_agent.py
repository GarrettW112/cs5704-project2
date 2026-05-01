from .base_agent import BaseAgent

class RecipeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            system_message=(
                "You are a world renowned chef focused on home cooking. "
                "Analyze the user's inventory and provide a simple recipe. "
                "Structure the recipe as: Recipe Description (including estimated cooked time), Ingredients List, Instructions"
            )
        )

    def run(self, prompt: str):
        response = self.generate_response(prompt)
        return response
    