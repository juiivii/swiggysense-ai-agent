import requests
import os
import json
from ranking import rank_results
from swiggy_ui_agent import search_swiggy
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("Loaded GROQ:", GROQ_API_KEY is not None)

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def extract_constraints(user_message):
    prompt = f"""
You are a food intent extraction system.

Extract structured constraints from this message.

Return ONLY valid JSON in this exact format:

{{
  "intent": "",           
  "dish": "",              
  "budget": null,          
  "veg": null,             
  "high_protein": null,    
  "calories": null,        
  "category": null,        
  "temperature": null,     
  "taste": null            
}}

Rules:
- If user directly names a dish → intent = "search"
- If user says suggest/recommend → intent = "suggest"
- If drink/juice/milkshake → category = "drink"
- If dessert/sweet → category = "dessert"
- If cold/chilled → temperature = "cold"
- If hot → temperature = "hot"
- Extract rupee budget correctly

Message:
{user_message}

Return ONLY JSON.
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
        )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        print("\n🔎 GROQ RAW RESPONSE:")
        print(content)

        return json.loads(content)

    except Exception as e:
        print("❌ Extraction failed:", e)
        return {
            "intent": "search",
            "dish": user_message,
            "budget": None,
            "veg": None,
            "high_protein": None,
            "calories": None,
            "category": None,
            "temperature": None,
            "taste": None
        }

def handle_user_query(user_message):

    print("➡ Extracting constraints...")
    constraints = extract_constraints(user_message)

    all_results = []
    suggestions = []

    try:
        # CASE 1: Direct search
        if constraints.get("intent") == "search" and constraints.get("dish"):
            print("➡ Direct search mode...")
            all_results = search_swiggy(constraints["dish"])

        # CASE 2: Suggestion mode
        else:
            print("➡ Suggestion mode activated...")
            suggestions = generate_multiple_suggestions(constraints)

            print("🤖 Suggestions:", suggestions)

            if not suggestions:
                return "⚠ Couldn't generate suggestions right now. Try again."

            # 🔥 Add delay + safe handling
            import time

            for dish in suggestions:
                clean_dish = dish.strip().replace("\n", "")
                print(f"➡ Searching Swiggy for: {clean_dish}")

                try:
                    dish_results = search_swiggy(clean_dish)
                    all_results.extend(dish_results)
                    time.sleep(4)  # Prevent rate-limit
                except Exception as e:
                    print(f"⚠ Failed searching {clean_dish}: {e}")
                    continue

        # If nothing collected
        if not all_results:
            return "⚠ No good matches found based on your preferences."

        print("➡ Ranking results...")
        ranked_output = rank_results(all_results, constraints)

        # Add suggestion header if suggestion mode
        if suggestions:
            suggestion_text = "🤖 Based on your preferences, I suggest:\n\n"
            for i, s in enumerate(suggestions, 1):
                suggestion_text += f"{i}️⃣ {s}\n"
            suggestion_text += "\n"

            return suggestion_text + ranked_output

        return ranked_output

    except Exception as e:
        print("❌ Unexpected error:", e)
        return "⚠ Something went wrong. Please try again in a moment."

def generate_multiple_suggestions(constraints):

    prompt = f"""
You are an intelligent Indian Swiggy food recommendation engine.

User preferences:
Category: {constraints.get("category")}
Temperature: {constraints.get("temperature")}
Vegetarian: {constraints.get("veg")}
High Protein: {constraints.get("high_protein")}
Budget: ₹{constraints.get("budget")}
Calories Limit: {constraints.get("calories")}
Taste Preference: {constraints.get("taste")}

Strict Rules:
- Suggest realistic Indian dishes.
- Keep names under 4 words.
- Return ONLY a JSON array of 3 dish names.
Example:
["Cold Coffee", "Mango Lassi", "Chocolate Milkshake"]
"""

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6
            }
        )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        print("🔎 SUGGESTION RAW:", content)

        # 🔥 Extract JSON array safely
        import re

        match = re.search(r"\[.*?\]", content, re.DOTALL)

        if match:
            json_array = match.group(0)
            suggestions = json.loads(json_array)
            return suggestions[:3]

        print("⚠ No JSON array found.")
        return []

    except Exception as e:
        print("⚠ Suggestion parsing failed:", e)
        return []