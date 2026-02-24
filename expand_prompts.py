import json
import os
from visual_schema import Trend, SubjectCategory, Style, Lighting, Composition, ColorPalette, VisualAttributes
from prompt_engine import PromptEngine

def expand_prompts():
    file_path = "seasonal_prompts.json"
    
    # Load existing
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
        
    current_count = len(existing_data)
    last_id = existing_data[-1]['id'] if existing_data else 0
    target_count = 16
    needed = target_count - current_count
    
    if needed <= 0:
        print(f"Already have {current_count} prompts. No need to add more.")
        return

    print(f"Generating {needed} new prompts...")
    engine = PromptEngine()
    new_prompts = []
    
    # Define scenarios for the new 12 images
    # Mix of Valentine (Feb), Spring/Easter (Mar/Apr), and general Spring Bestsellers
    
    scenarios = [
        # Valentine's Day (4)
        (
            VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE, Style.CINEMATIC, Lighting.GOLDEN_HOUR, Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
            "Valentine's Day",
            "Couple holding hands walking on beach at sunset, romantic silhouette, love, peaceful atmosphere, valentines day date"
        ),
        (
            VisualAttributes(Trend.IMMERSIVE_APPEAL, SubjectCategory.FOOD, Style.PHOTOREALISTIC, Lighting.NATURAL_SOFT, Composition.MACRO, ColorPalette.WARM_COZY),
            "Valentine's Day",
            "Artisan heart shaped chocolates in a gift box, cocoa dusting, rich texture, delicious dessert, valentines gift"
        ),
         (
            VisualAttributes(Trend.GENERIC_BESTSELLER, SubjectCategory.NATURE, Style.PHOTOREALISTIC, Lighting.STUDIO_LIGHTING, Composition.CENTERED, ColorPalette.VIBRANT),
            "Valentine's Day",
             "Luxurious bouquet of fresh red roses, velvet texture, water droplets on petals, romantic gift, black background"
        ),
        (
            VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.ABSTRACT, Style.MINIMALIST, Lighting.NATURAL, Composition.NEGATIVE_SPACE, ColorPalette.PASTEL),
            "Valentine's Day",
            "Single elegant gift box with red ribbon on pink background, minimalism, surprise, present, love symbol"
        ),
        
        # Spring/Easter (4)
        (
            VisualAttributes(Trend.GENERIC_BESTSELLER, SubjectCategory.NATURE, Style.PHOTOREALISTIC, Lighting.NATURAL_SOFT, Composition.MACRO, ColorPalette.PASTEL),
            "Easter Spring",
            "Colorful Easter eggs in a woven basket on green grass, soft spring sunlight, blurred nature background, tradition"
        ),
        (
            VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.FOOD, Style.SCANDINAVIAN, Lighting.NATURAL, Composition.KNOLLING, ColorPalette.PASTEL),
            "Easter Spring",
            "Minimalist Easter brunch table setting, white plates, pastel napkins, tulips, clean and fresh atmosphere"
        ),
        (
            VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE, Style.REALISTIC_PHOTOGRAPHY, Lighting.GOLDEN_HOUR, Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
            "Easter Spring",
            "Happy family hunting for easter eggs in backyard garden, children running, spring flowers, joyful moment"
        ),
         (
            VisualAttributes(Trend.FANTASTIC_FRONTIERS, SubjectCategory.ABSTRACT, Style.DIGITAL_ART_3D, Lighting.NATURAL_SOFT, Composition.CENTERED, ColorPalette.PASTEL_DREAM),
            "Easter Spring",
            "Surreal giant easter egg floating in clouds, dreamlike atmosphere, pastel colors, fantasy spring concept"
        ),
        
        # Spring Nature/Bestseller (4)
        (
            VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.NATURE, Style.PHOTOREALISTIC, Lighting.NATURAL, Composition.NEGATIVE_SPACE, ColorPalette.EARTH_TONES),
            "Spring Nature",
            "Fresh green sprout growing from soil, blurry background, new life concept, growth, spring season, environment"
        ),
        (
            VisualAttributes(Trend.GENERIC_BESTSELLER, SubjectCategory.NATURE, Style.PHOTOREALISTIC, Lighting.NATURAL, Composition.RULE_OF_THIRDS, ColorPalette.VIBRANT),
            "Spring Nature",
            "Field of yellow daffodils under blue sky, vibrant spring landscape, blooming flowers, hope and energy"
        ),
        (
            VisualAttributes(Trend.WORKPLACE_EVOLUTION, SubjectCategory.BUSINESS_WORK, Style.MINIMALIST, Lighting.NATURAL_SOFT, Composition.KNOLLING, ColorPalette.PASTEL),
            "Spring Nature",
            "Clean home office desk with fresh potted plant, laptop, notebook, eco-friendly workspace, spring cleaning concept"
        ),
        (
            VisualAttributes(Trend.IMMERSIVE_APPEAL, SubjectCategory.ABSTRACT, Style.MINIMALIST, Lighting.DRAMATIC, Composition.ABSTRACT_GEOMETRIC, ColorPalette.PASTEL),
            "Spring Nature",
            "Abstract shadow of palm leaves on pink wall, summer spring vibe, copy space, minimal background, tropical feel"
        )
    ]

    # Process scenarios
    for i, (attrs, theme, specific_subject) in enumerate(scenarios):
        # Create full prompt from attributes
        full_prompt_dict = engine.construct_full_prompt(attrs)
        base_prompt = full_prompt_dict['positive']
        
        # Simple replacement of generic subject holder if present, or append
        # The prompt engine usually constructs generic sentences. 
        # We will prepend the specific subject description to ensure it's the main focus.
        
        final_prompt = f"{specific_subject}, {base_prompt}"
        
        new_prompts.append({
            "id": last_id + 1 + i,
            "theme": theme,
            "subject": specific_subject,
            "prompt": final_prompt,
            "negative_prompt": full_prompt_dict['negative']
        })

    # Append and save
    existing_data.extend(new_prompts)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully added {len(new_prompts)} prompts. Total: {len(existing_data)}")

if __name__ == "__main__":
    expand_prompts()
