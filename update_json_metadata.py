import sys
import glob
import os
import json

TARGET_DIR = sys.argv[1]

# Map of substrings in filenames to their keywords and titles
metadata_updates = {
    "anonymous_hacker_dark_room_multiple": {
        "title": "Anonymous hacker typing on keyboard in dark room with multiple glowing monitors",
        "keywords": ["hacker", "cybersecurity", "coding", "programmer", "computer", "dark", "security", "technology", "network", "data", "cyber", "internet", "crime", "virus", "malware", "software", "code", "screen", "green", "neon", "typing", "keyboard", "anonymous", "privacy", "protection", "attack", "system", "breach", "modern", "tech"],
        "category": 16
    },
    "woman_yoga_mountain_peak_sunrise": {
        "title": "Young healthy woman practicing yoga meditation on mountain peak at glowing sunrise",
        "keywords": ["yoga", "meditation", "mountain", "sunrise", "woman", "fitness", "health", "wellness", "nature", "outdoor", "peaceful", "calm", "serene", "morning", "relaxation", "silhouette", "healthy lifestyle", "exercise", "stretching", "mindfulness", "landscape", "sun", "sky", "freedom", "pose", "balance", "harmony", "breathtaking", "active", "tranquility"],
        "category": 12
    },
    "financial_charts_tablet_coffee_desk": {
        "title": "Close-up of digital tablet showing financial growth charts with coffee on wooden table",
        "keywords": ["finance", "graphs", "charts", "business", "growth", "tablet", "technology", "investment", "market", "stock", "analyzing", "data", "report", "coffee", "wooden table", "success", "profit", "planning", "screen", "digital", "economy", "strategy", "workplace", "desk", "analytics", "modern", "wealth", "corporate", "statistics", "concept"],
        "category": 3
    },
    "rustic_autumn_harvest_dinner_table": {
        "title": "Rustic wooden table set for autumn thanksgiving harvest dinner with pumpkins and candles",
        "keywords": ["autumn", "thanksgiving", "harvest", "dinner", "table", "wooden", "pumpkins", "candles", "food", "feast", "fall", "seasonal", "celebration", "traditional", "rustic", "cozy", "warm", "setting", "decoration", "holiday", "family", "meal", "vegetables", "leaves", "dining", "festival", "gathering", "festive", "orange", "traditional"],
        "category": 7
    },
    "modern_wind_turbines_green_field": {
        "title": "Modern wind turbines generating clean renewable energy in lush green field under blue sky",
        "keywords": ["wind turbine", "renewable energy", "green", "sustainable", "environment", "ecology", "power", "nature", "field", "blue sky", "clouds", "landscape", "technology", "electricity", "clean", "alternative", "eco-friendly", "industry", "generator", "mill", "conservation", "future", "innovation", "sunshine", "rural", "outdoors", "climate change", "global warming", "sustainable development"],
        "category": 5
    }
}

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generations", TARGET_DIR)

updated_count = 0
for filepath in glob.glob(os.path.join(base_dir, "*.json")):
    filename = os.path.basename(filepath)
    matched = False
    for k, v in metadata_updates.items():
        if k in filename:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data["title"] = v["title"]
            data["keywords"] = v["keywords"]
            data["category"] = v["category"]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            matched = True
            updated_count += 1
            print(f"Updated {filename} with title '{v['title']}' and {len(v['keywords'])} keywords. Cat: {v['category']}")
            break
            
    if not matched:
        print(f"Warning: No matching metadata found for {filename}")

print(f"Successfully updated {updated_count} files.")
