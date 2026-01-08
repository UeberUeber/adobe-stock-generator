import json
import os
import datetime
import re

def clean_filename(text):
    # Keep only alphanumeric and spaces, then replace spaces with underscores
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return clean.strip().replace(' ', '_').lower()

def process_metadata():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("generations", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    with open("seasonal_prompts.json", "r", encoding="utf-8") as f:
        prompts = json.load(f)
        
    keyword_map = {
        "January": "new year, fresh start, wellness, resolution, winter, cozy, healthy, productivity",
        "February": "valentine, love, romance, connection, heart, warmth, couple, emotion",
        "March": "spring, growth, nature, women's day, easter, renewal, green, fresh",
        "New Year": "social event, party, celebration, new year, holiday, happiness, togetherness, festive",
        "Valentine": "love, romance, couple, valentine, heart, gift, affection, passion, red"
    }
    
    file_mapping = {}
    
    for item in prompts:
        theme = item['theme'] 
        prompt_text = item['prompt']
        subject_desc = item.get('subject', '')
        
        # Generate filename from subject (first few words)
        # e.g. "Authentic Woman practicing yoga..." -> "authentic_woman_practicing_yoga"
        short_desc = " ".join(subject_desc.split()[:5])
        filename_base = f"{clean_filename(short_desc)}_{timestamp}"
        json_filename = f"{filename_base}.json"
        
        # Keywords generation
        base_keywords = keyword_map.get(theme, "stock, seasonal").split(", ")
        extra_keywords = [w for w in clean_filename(subject_desc).split('_') if len(w) > 3]
        keywords = base_keywords + extra_keywords[:5]
        
        keywords.extend(["no people" if "no people" in prompt_text.lower() else "people", "horizontal", "copy space", "photography" if "3D" not in prompt_text else "illustration"])
        
        # Determine Category ID based on keywords/theme
        # 13: People, 14: Plants/Flowers, 15: Religion/Culture, 7: Food, 4: Business, 17: Sports (Yoga)
        cat_id = 15 # Default
        lower_sub = subject_desc.lower()
        if "yoga" in lower_sub or "workout" in lower_sub: cat_id = 17 # Sports
        elif "food" in lower_sub or "vegetables" in lower_sub or "meal" in lower_sub or "chocolate" in lower_sub: cat_id = 7 # Food
        elif "flower" in lower_sub or "plant" in lower_sub or "garden" in lower_sub: cat_id = 14 # Plants
        elif "office" in lower_sub or "work" in lower_sub or "financial" in lower_sub or "laptop" in lower_sub: cat_id = 4 # Business
        elif "couple" in lower_sub or "grandmother" in lower_sub or "woman" in lower_sub or "friends" in lower_sub: cat_id = 13 # People
        elif "easter" in lower_sub or "valentine" in lower_sub or "new year" in lower_sub: cat_id = 15 # Culture
        
        metadata = {
            "filename": f"{filename_base}.png",
            "title": f"{theme} Concept: {subject_desc[:50]}...",
            "keywords": list(set(keywords)), # Deduplicate
            "category": cat_id,
            "category_name": str(cat_id), 
            "asset_type": "illustration" if "3D" in prompt_text or "Digital Art" in prompt_text else "photo",
            "prompt": prompt_text,
            "is_ai_generated": True,
            "is_fictional": True
        }
        
        # Save JSON
        with open(os.path.join(output_dir, json_filename), "w", encoding="utf-8") as jf:
            json.dump(metadata, jf, indent=2, ensure_ascii=False)
            
        file_mapping[item['id']] = {
            "filename_base": filename_base,
            "full_path": os.path.abspath(os.path.join(output_dir, f"{filename_base}.png")),
            "prompt": prompt_text
        }
        
    print(f"OUTPUT_DIR: {output_dir}")
    print(json.dumps(file_mapping, indent=2))

if __name__ == "__main__":
    process_metadata()
