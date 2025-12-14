import os
import json
import datetime
from visual_schema import Trend, SubjectCategory, Style, Lighting, Composition, ColorPalette, VisualAttributes
from prompt_engine import PromptEngine

def generate_christmas_prompts():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    engine = PromptEngine()
    
    # Define 3 MECE Categories
    p1 = VisualAttributes(
        trend=Trend.WORKPLACE_EVOLUTION,
        subject_category=SubjectCategory.PEOPLE_LIFESTYLE,
        style=Style.PHOTOREALISTIC,
        lighting=Lighting.WARM_GOLDEN_HOUR,
        composition=Composition.CENTERED,
        color_palette=ColorPalette.WARM_COZY
    )
    
    p2 = VisualAttributes(
        trend=Trend.MINIMALIST_WELLNESS,
        subject_category=SubjectCategory.NATURE_OUTDOORS,
        style=Style.CINEMATIC,
        lighting=Lighting.NATURAL_SOFT,
        composition=Composition.NEGATIVE_SPACE,
        color_palette=ColorPalette.PASTEL
    )
    
    p3 = VisualAttributes(
        trend=Trend.IMMERSIVE_APPEAL,
        subject_category=SubjectCategory.ABSTRACT_TEXTURES,
        style=Style.DIGITAL_ART_3D,
        lighting=Lighting.STUDIO_LIGHTING,
        composition=Composition.MACRO,
        color_palette=ColorPalette.VIBRANT_NEON
    )
    
    # We map the VisualAttributes to the specific replacement target based on PromptEngine logic
    prompts_config = [
        (p1, "People & Lifestyle", "Family celebrating Christmas by the fireplace, drinking hot cocoa, cozy sweaters, happiness, authentic interaction"),
        (p2, "Nature & Outdoors", "Snow covered pine forest in winter, peaceful Christmas atmosphere, majestic scenery, untouched nature"),
        (p3, "Abstract & Textures", "Close-up of modern Christmas ornaments, glitter textures, glass reflections, luxury holiday decoration, gold and red")
    ]
    
    results = []
    
    for i, (attrs, generic_subject_name, specific_subject) in enumerate(prompts_config):
        full_prompt_dict = engine.construct_full_prompt(attrs)
        base_prompt = full_prompt_dict['positive']
        
        # Replace the generic localized subject name with our specific one
        # The prompt usually starts with "Professional stock photo... <Trend Prefix> {Subject}..."
        # But PromptEngine puts the custom prefix AFTER "Professional stock photo...".
        # Actually PromptEngine: parts.insert(0, self.base_style) -> "Professional stock photo..."
        # Then parts.append(trend_prefix).
        # So "Professional..., Cozy People & Lifestyle, home office..."
        
        final_prompt = base_prompt.replace(generic_subject_name, specific_subject)
        
        # Also clean up potential grammar issues if needed, but simple replacement should work 
        # as long as we replace the exact Enum value string.
        
        results.append({
            "id": i+1,
            "specific_subject": specific_subject,
            "prompt": final_prompt,
            "negative_prompt": full_prompt_dict['negative'],
            "timestamp": timestamp,
            "category_id": "15" if i == 1 else "14" # Just a guess, we will let metadata generator decide later or force it.
            # actually we don't need category_id here, prompt_metadata.py determines it.
        })

    with open("christmas_prompts.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    generate_christmas_prompts()
