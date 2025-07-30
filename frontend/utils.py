import json
import os
from dotenv import load_dotenv
from constants import SYSTEM_PROMPT  # ✅ CORRECT
from openai import OpenAI
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load product data from JSON
def get_product_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))  # directory of utils.py
    data_path = os.path.join(base_dir, "../backend/data/products.json")
    with open(data_path) as f:
        return json.load(f)

# Function tools
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

# Functions LLM can call
def get_bag_options():
    return get_product_data()["bags"]

def get_products_by_category(category):
    return get_product_data()["products"][category]

def create_checkout_summary(bag_name, products, affirmation):
    return {
        "summary": f"Here's your bag: {bag_name} with " + ", ".join(products) + ".",
        "affirmation": affirmation
    }

from datetime import datetime

def save_order_to_backend(username, bag, products, affirmation):
    order = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "bag": bag,
        "products": products,
        "affirmation": affirmation
    }

    print("🚀 Saving order to backend:", username, order)
    res = requests.post("https://maya-beauty-bag-1.onrender.com/save_order", json={
        "user_id": username,
        "order_data": order
    })

    if res.status_code != 200:
        print("❌ Failed to save order:", res.status_code, res.text)

    return res.status_code == 200


# Router for function calls
function_router = {
    "get_bag_options": lambda _: get_bag_options(),  # <-- no argument passed
    "get_products_by_category": lambda args: get_products_by_category(args.get("category")),
    "create_checkout_summary": lambda args: create_checkout_summary(
        args["bag_name"], args["products"], args["affirmation"]
    )
}
# Core function to call OpenAI with tools
def chat_with_maya(messages, username=None):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages,
        temperature=0.8,
        functions=get_function_specs(),
        function_call="auto"
    )

    message = response.choices[0].message

    if message.function_call:
        func_name = message.function_call.name
        args = json.loads(message.function_call.arguments)

        if func_name == "get_bag_options":
            result = get_bag_options()

        elif func_name == "get_products_by_category":
            category = args.get("category")
            result = get_products_by_category(category) if category else {"error": "Missing category"}

        elif func_name == "create_checkout_summary":
            bag = args.get("bag_name")
            selected_products = args.get("products")
            affirmation = args.get("affirmation")

            # Only proceed if all required args are present
            if bag and selected_products and affirmation:
                result = create_checkout_summary(bag, selected_products, affirmation)

                # Save to backend
                if username:
                    save_order_to_backend(username, bag, selected_products, affirmation)
            else:
                result = {"error": "Missing bag_name, products, or affirmation."}

        else:
            result = {"error": "Unknown function."}

        # Append function result
        messages.append({
            "role": "function",
            "name": func_name,
            "content": json.dumps(result)
        })

        # Recurse to continue the conversation
        return chat_with_maya(messages, username=username)

    return message.content.strip()