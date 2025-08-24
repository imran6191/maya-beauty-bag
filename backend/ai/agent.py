# backend/ai/agent.py

from openai import OpenAI
import requests
from backend.ai.functions import get_function_specs, get_bag_options, get_products_by_category, create_checkout_summary
from backend.ai.prompts import SYSTEM_PROMPT
from backend.utils.file_store import read_user_data, write_user_data
from backend.core.config import settings
from backend.ai.tts import speak_response
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def chat_with_maya(messages, username=None):
    print(f"🔥 chat_with_maya called with {len(messages)} messages")

    # Extract state
    selected_bag = None
    skin_product = None
    eye_product = None
    lip_product = None
    user_feeling = None
    user_area = None

    for msg in messages:
        if msg["role"] == "function":
            if msg["name"] == "get_bag_options" and msg.get("content"):
                try:
                    result = json.loads(msg["content"])
                    if isinstance(result, list) and result:
                        selected_bag = result[0]
                except:
                    pass
            elif msg["name"] == "get_products_by_category" and msg.get("content"):
                try:
                    result = json.loads(msg["content"])
                    args = json.loads(msg.get("arguments", "{}"))
                    category = args.get("category")
                    if isinstance(result, list) and result:
                        if category == "skin_prep":
                            skin_product = result[0]
                        elif category == "eyes":
                            eye_product = result[0]
                        elif category == "lips":
                            lip_product = result[0]
                except:
                    pass

    is_first_response = len([m for m in messages if m["role"] == "assistant"]) == 0

    # 1. First message? → Ask for bag
    if is_first_response:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,
                functions=get_function_specs(),
                function_call={"name": "get_bag_options"}
            )
            message = response.choices[0].message
            if message.function_call:
                result = get_bag_options()
                messages.append({
                    "role": "function",
                    "name": "get_bag_options",
                    "content": json.dumps(result)
                })
                # Get AI response
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.8
                )
                ai_response = response.choices[0].message.content
                audio_data = speak_response(ai_response)
                if audio_data:
                    with open("maya_response.mp3", "wb") as f:
                        f.write(audio_data)
                    print("✅ Audio saved to maya_response.mp3")
                return ai_response
        except Exception as e:
            print("❌ OpenAI Error:", e)
            return "I'm having trouble connecting. Please try again."

    # 2. Bag selected but no empowerment? → Ask empowerment
    if selected_bag and not user_feeling:
        user_msg = messages[-1]["content"].lower()
        if "fierce" in user_msg or "radiant" in user_msg or "grounded" in user_msg or "calm" in user_msg or "celebrated" in user_msg:
            user_feeling = user_msg.strip()
            return "What's one area you are stepping into right now? Choose from: Skin glow-up, Confidence boost, Creative reset, Energy renewal, Soft self-care."
        else:
            return "How do you want to feel when you open this bag? Choose from: radiant, grounded, fierce, calm, celebrated."

    if selected_bag and user_feeling and not user_area:
        user_msg = messages[-1]["content"].lower()
        if "skin" in user_msg or "confidence" in user_msg or "creative" in user_msg or "energy" in user_msg or "soft" in user_msg:
            user_area = user_msg.title()
            return "Now, let's pick your products. First, what would you like for skin prep? Say 'Show me skin prep products'."
        else:
            return "Please choose a valid area."

    # 3. Empowerment done → Let OpenAI handle product selection
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            functions=get_function_specs(),
            function_call="auto"
        )
        message = response.choices[0].message
        if message.content:
            audio_data = speak_response(message.content)
            if audio_data:
                with open("maya_response.mp3", "wb") as f:
                    f.write(audio_data)
                print("✅ Audio saved to maya_response.mp3")
            return message.content.strip()
    except Exception as e:
        print("❌ OpenAI Error:", e)
        return "I'm having trouble connecting. Please try again."

    return "Let's continue."