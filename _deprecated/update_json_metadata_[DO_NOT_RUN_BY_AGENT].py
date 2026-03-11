import sys
import glob
import os
import json

TARGET_DIR = sys.argv[1]

# Map of substrings in filenames to their keywords and titles
metadata_updates = {
    "cyberpunk_city_street_rainy_night": {
        "title": "Cinematic futuristic neon-lit cyberpunk city street on dark rainy night with glowing car",
        "keywords": ["cyberpunk", "city", "street", "rain", "night", "neon", "futuristic", "car", "sci-fi", "urban", "architecture", "dark", "wet", "asphalt", "reflections", "light", "dystopian", "modern", "metropolis", "glow", "vehicle", "technology", "transportation", "future", "downtown", "atmosphere", "cinematic", "background", "skyscraper"],
        "category": 2
    },
    "surreal_floating_islands_alien_sky": {
        "title": "Breathtaking surreal floating islands covered with glowing flora in dreamy alien purple sky",
        "keywords": ["surreal", "floating", "island", "alien", "sky", "glowing", "flora", "fantasy", "landscape", "magic", "dreamy", "purple", "waterfall", "nature", "background", "beautiful", "mystical", "environment", "concept", "art", "3d", "render", "digital", "ethereal", "space", "breathtaking", "unreal", "creative", "imagination"],
        "category": 8
    },
    "retro_futuristic_1950s_robot_helper": {
        "title": "Friendly retro-futuristic 1950s metallic robot helper offering drinks in pastel living room",
        "keywords": ["robot", "retro", "futuristic", "1950s", "vintage", "helper", "living room", "interior", "technology", "sci-fi", "nostalgia", "pastels", "design", "mid-century", "modern", "automation", "friendly", "machine", "character", "concept", "artificial intelligence", "home", "domestic", "service", "lifestyle", "future", "classic", "metal"],
        "category": 16
    },
    "microscopic_glowing_dna_double_helix": {
        "title": "Ultra close-up microscopic view of glowing bioluminescent DNA double helix structure",
        "keywords": ["dna", "microscopic", "helix", "glowing", "bioluminescent", "structure", "genetics", "science", "biology", "research", "medical", "health", "technology", "molecule", "cell", "laboratory", "life", "gene", "abstract", "background", "3d", "illustration", "blue", "code", "evolution", "human", "medicine", "concept"],
        "category": 16
    },
    "3d_geometric_abstract_glassmorphism": {
        "title": "Elegant 3D geometric abstract background with frosted glassmorphism spheres and neon lights",
        "keywords": ["abstract", "geometric", "3d", "glassmorphism", "neon", "background", "elegant", "frosted", "glass", "spheres", "pedestal", "display", "product", "presentation", "modern", "design", "creative", "shape", "template", "copy space", "glow", "art", "graphic", "minimalist", "clean", "render", "light", "texture", "studio"],
        "category": 8
    },
    "macro_antique_mechanical_watch_movement": {
        "title": "Extreme macro photography of intricate working gears inside antique mechanical watch movement",
        "keywords": ["macro", "antique", "mechanical", "watch", "movement", "gears", "mechanism", "engineering", "precision", "time", "clock", "vintage", "metal", "industrial", "complex", "machinery", "parts", "brass", "steel", "technology", "close-up", "detail", "engine", "instrument", "timepiece", "craftsmanship", "luxury", "ruby", "work"],
        "category": 10
    },
    "futuristic_automated_factory_assembly": {
        "title": "Advanced futuristic automated factory assembly line with orange robotic arms and bright sparks",
        "keywords": ["futuristic", "automated", "factory", "assembly", "line", "robotic", "arms", "sparks", "industry", "manufacturing", "technology", "robot", "production", "machine", "engineering", "automation", "modern", "equipment", "plant", "business", "heavy", "metal", "innovation", "industrial", "future", "process", "work", "concept"],
        "category": 10
    },
    "conceptual_scale_balancing_nature": {
        "title": "Conceptual golden scale precisely balancing lush green tree and glowing advanced circuit board",
        "keywords": ["conceptual", "scale", "balance", "nature", "tree", "technology", "circuit", "board", "sustainability", "environment", "ecology", "green", "future", "global", "warming", "earth", "concept", "art", "3d", "ideas", "business", "life", "choice", "comparison", "electronic", "growth", "protect", "save", "world"],
        "category": 5
    },
    "zen_rock_garden_minimalist_sand_night": {
        "title": "Peaceful traditional Japanese Zen rock garden with raked sand patterns under soft moonlight",
        "keywords": ["zen", "rock", "garden", "sand", "night", "moonlight", "peaceful", "traditional", "japanese", "minimalist", "pattern", "culture", "meditation", "calm", "serenity", "stone", "tranquility", "mindfulness", "spirituality", "harmony", "nature", "relax", "background", "empty", "space", "landscape", "yin yang", "asia", "oriental"],
        "category": 15
    },
    "abstract_brainstorm_creative_colorful": {
        "title": "Spectacular creative brainstorm explosion of vibrant liquid paint colors bursting outward",
        "keywords": ["abstract", "brainstorm", "creative", "colorful", "paint", "explosion", "liquid", "burst", "vibrant", "art", "inspiration", "concept", "design", "background", "splash", "color", "dynamic", "energy", "motion", "rainbow", "creative process", "idea", "imagination", "water", "fluid", "bright", "white", "flying", "action"],
        "category": 6
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
