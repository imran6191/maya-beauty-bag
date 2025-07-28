import json
import os
from dotenv import load_dotenv
from constants import SYSTEM_PROMPT  # ✅ CORRECT
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load product data from JSON
def get_product_data():
    with open("backend/data/products.json") as f:
        return json.load()

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
            "description": "Returns products from a specific category like 'skin_prep', 'eyes', or 'lips'.",
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

# Router for function calls
function_router = {
    "get_bag_options": get_bag_options,
    "get_products_by_category": lambda args: get_products_by_category(args.get("category")),
    "create_checkout_summary": lambda args: create_checkout_summary(
        args["bag_name"], args["products"], args["affirmation"]
    )
}

# Maya's voice
# SYSTEM_PROMPT = """
# You are Maya, a warm, empowering beauty assistant who helps users build personalized beauty bags. 
# Ask questions one step at a time. Always keep a tone that’s affirming, feminine, and confident.
# You can call functions to show bags, show products, or create a checkout summary.
# """

# Core function to call OpenAI with tools
def chat_with_maya(messages):
    response = client.chat.completions.create(
        model="gpt-4o",  # or gpt-4-turbo
        messages=messages,
        tools=[  # ← was `functions` before
            {
                "type": "function",
                "function": f
            } for f in get_function_specs()
        ],
        tool_choice="auto"
    )

    reply = response.choices[0].message

    # Handle function call
    if reply.tool_calls:
        for tool_call in reply.tool_calls:
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            result = function_router[func_name](arguments)

            # Append tool call + result
            messages.append({
                "role": "assistant",
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(result)
            })

        # Recursive call after function call
        return chat_with_maya(messages)
    else:
        return reply.content