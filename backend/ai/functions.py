# backend/ai/functions.py
import json
import os
from backend.core.config import settings

# Load product data
def get_product_data():
    products_file = os.path.join(os.path.dirname(__file__), "..", "data", "products.json")
    products_file = os.path.abspath(products_file)

    if not os.path.exists(products_file):
        raise FileNotFoundError(f"products.json not found at {products_file}")

    with open(products_file, "r", encoding="utf-8") as f:
        return json.load(f)

# Function specs for OpenAI
def get_function_specs():
    return [
        {
            "name": "get_bag_options",
            "description": "Returns the list of available beauty bags.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_products_by_category",
            "description": "Get products for a specific category ONLY using this function. Do not guess or generate product names. Use only categories: 'skin_prep', 'eyes', 'lips'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["skin_prep", "eyes", "lips"]
                    }
                },
                "required": ["category"]
            }
        },
        {
            "name": "create_checkout_summary",
            "description": "Creates a summary with selected bag, products, and affirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bag_name": {"type": "string"},
                    "products": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "affirmation": {"type": "string"}
                },
                "required": ["bag_name", "products", "affirmation"]
            }
        }
    ]

# Actual functions OpenAI can call
def get_bag_options():
    return get_product_data()["bags"]

def get_products_by_category(category):
    return get_product_data()["products"][category]

def create_checkout_summary(bag_name, products, affirmation):
    return {
        "summary": f"Here's your bag: {bag_name} with " + ", ".join(products) + ".",
        "affirmation": affirmation
    }