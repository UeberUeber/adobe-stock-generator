import json
import glob
import os

DIR = r"E:\codeWantigravity\AdobeStock_Automation Service\adobe-stock-generator\generations\2026-03-11_11-24-10"

data_map = {
    "dark_futuristic_apartment_neon_city": {
        "title": "Futuristic neo-noir cyberpunk living room apartment with black leather couch and glowing neon pink and blue city lights through large window",
        "keywords": ["cyberpunk", "neon", "glowing", "city", "night", "futuristic", "apartment", "living room", "interior", "dark", "moody", "sci-fi", "architecture", "black leather", "sofa", "window", "science fiction", "high contrast", "aesthetics", "technology", "metropolitan", "urban", "future", "modern", "purple", "blue", "pink", "glass", "reflection", "room", "indoors"],
        "category": 15
    },
    "dark_log_cabin_living_room": {
        "title": "Cozy rustic wooden log cabin interior living room at winter night with classic leather sofa and warm glowing stone fireplace",
        "keywords": ["rustic", "cabin", "log", "wood", "interior", "living room", "winter", "night", "warm", "cozy", "fireplace", "fire", "glow", "leather", "sofa", "traditional", "holiday", "retreat", "lodge", "timber", "architecture", "comfortable", "heavy shadows", "romantic", "natural", "warm light", "evening", "indoors", "home", "house", "decor"],
        "category": 15
    },
    "exposed_red_brick_concrete_floor": {
        "title": "Modern industrial loft interior living room during daytime with exposed red brick walls concrete floors and metal pipes",
        "keywords": ["industrial", "loft", "interior", "living room", "daytime", "red brick", "exposed brick", "concrete", "floor", "metal", "pipes", "architecture", "modern", "urban", "minimalist", "warehouse", "apartment", "window", "bright", "daylight", "neutral", "cool tones", "design", "decor", "space", "empty wall", "copy space", "indoors", "stylish", "house", "home"],
        "category": 15
    },
    "low_furniture_natural_stone_textures": {
        "title": "Peaceful minimalist Zen interior living room with low modern furniture and natural rough stone textures catching warm sunset light",
        "keywords": ["minimalist", "zen", "interior", "living room", "peaceful", "serene", "meditation", "natural", "stone", "texture", "low furniture", "sunset", "warm light", "monochromatic", "beige", "calm", "relaxation", "quiet", "architecture", "design", "modern", "clean", "simple", "Japanese influence", "wabi-sabi", "indoors", "home", "space", "harmony", "tranquility", "decor"],
        "category": 15
    },
    "marble_floors_high_rise_glass": {
        "title": "Luxury modern high rise penthouse living room at night featuring polished marble floors and large sleek glass walls",
        "keywords": ["luxury", "modern", "penthouse", "living room", "interior", "night", "high rise", "marble", "floor", "glass", "wall", "cool light", "moonlight", "elegant", "rich", "expensive", "architecture", "design", "chic", "sophisticated", "view", "cityscape", "dark", "indoors", "home", "apartment", "decor", "contemporary", "affluent", "estate", "property"],
        "category": 15
    },
    "minimalist_light_wood_living_room": {
        "title": "Bright Scandinavian minimalist interior living room bathed in morning sunlight with light wood floors and white walls",
        "keywords": ["scandinavian", "minimalist", "living room", "interior", "bright", "morning", "sunlight", "light wood", "floor", "white", "beige", "airy", "neutral", "modern", "simple", "clean", "cozy", "decor", "home", "indoors", "architecture", "design", "daylight", "fresh", "peaceful", "space", "copy space", "style", "lifestyle", "house"],
        "category": 15
    },
    "ornate_wood_furniture_dark_green": {
        "title": "Elegant classic traditional interior living room at evening with ornate dark wood furniture and rich green wallpaper",
        "keywords": ["classic", "traditional", "interior", "living room", "elegant", "evening", "ornate", "wood", "furniture", "green", "wallpaper", "gold", "accents", "warm", "glow", "table lamp", "sophisticated", "timeless", "vintage", "antique", "decor", "home", "house", "indoors", "luxury", "rich", "dark", "cozy", "architecture", "design"],
        "category": 15
    },
    "rattan_furniture_abundant_green_plants": {
        "title": "Relaxing bohemian plant oasis interior living room featuring natural rattan furniture and abundant lush green indoor house plants",
        "keywords": ["bohemian", "plant", "oasis", "interior", "living room", "rattan", "furniture", "green", "indoor plants", "lush", "nature", "natural", "earth tones", "dappled light", "afternoon", "sun", "relaxing", "holistic", "decor", "home", "house", "indoors", "cozy", "eclectic", "style", "jungle", "urban jungle", "botany", "vintage", "peace"],
        "category": 15
    },
    "soft_rounded_furniture_pastel_colors": {
        "title": "Playful pastel dream pop-art aesthetic living room with soft cozy rounded furniture in sweet pink and mint green colors",
        "keywords": ["pastel", "dream", "pop-art", "living room", "interior", "playful", "whimsical", "soft", "rounded", "furniture", "pink", "mint", "green", "modern", "bright", "studio", "lighting", "flat", "colorful", "sweet", "cute", "design", "decor", "home", "indoors", "architecture", "clean", "vibrant", "trendy", "aesthetic"],
        "category": 15
    },
    "vintage_retro_furniture_sunset_shadows": {
        "title": "Stylish mid-century modern interior living room with vintage retro furniture and long warm sunset shadows",
        "keywords": ["mid-century", "modern", "living room", "interior", "stylish", "vintage", "retro", "furniture", "geometric", "teal", "orange", "sunset", "shadow", "warm", "golden hour", "lighting", "classic", "1960s", "decor", "home", "house", "indoors", "architecture", "design", "aesthetic", "nostalgia", "property", "estate", "room", "space"],
        "category": 15
    }
}

count = 0
for filepath in glob.glob(os.path.join(DIR, "*.json")):
    name = os.path.basename(filepath)
    for k, v in data_map.items():
        if k in name:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['title'] = v['title']
            data['keywords'] = v['keywords']
            data['category'] = v['category']
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Updated {name}")
            count += 1
            break
            
print(f"Total updated: {count}")
