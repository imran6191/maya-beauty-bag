import json
import os
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT
from openai import OpenAI
import requests
from datetime import datetime

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load product data from JSON
def get_product_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "../backend/data/products.json")
    with open(data_path) as f:
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

def save_order_to_backend(username, bag, products, affirmation):
    order = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "bag": bag,
        "products": products,
        "affirmation": affirmation
    }
    res = requests.post(f"{API_BASE_URL}/save_order", json={
        "user_id": username,
        "order_data": order
    })
    if res.status_code != 200:
        print("❌ Failed to save order:", res.status_code, res.text)
    return res.status_code == 200

# Generate TTS audio from Deepgram
def speak_response(text):
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print("❌ Deepgram TTS failed:", response.text)
        return None

# Main AI function
def chat_with_maya(messages, username=None):
    print("frontend")

    is_first_response = len([m for m in messages if m["role"] == "assistant"]) == 0

    if is_first_response:
        function_call = {"name": "get_bag_options"}
    else:
        function_call = "auto"

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            temperature=0.8,
            functions=get_function_specs(),
            function_call=function_call
        )
    except Exception as e:
        print("❌ OpenAI Error:", e)
        return "I'm having trouble connecting. Please try again."

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

            if bag and selected_products and affirmation:
                result = create_checkout_summary(bag, selected_products, affirmation)
                if username:
                    save_order_to_backend(username, bag, selected_products, affirmation)
            else:
                result = {"error": "Missing required fields."}

        else:
            result = {"error": "Unknown function."}

        messages.append({
            "role": "function",
            "name": func_name,
            "content": json.dumps(result)
        })

        # 🟢 Recursive call to continue conversation
        return chat_with_maya(messages, username=username)

    elif message.content:
        text_response = message.content.strip()

        # 🟢 TTS with Deepgram
        audio_data = speak_response(text_response)
        if audio_data:
            # Write to file
            with open("maya_response.mp3", "wb") as f:
                f.write(audio_data)
            print("✅ Audio saved to maya_response.mp3")

        return text_response

    else:
        return "⚠️ No response from Maya." 
