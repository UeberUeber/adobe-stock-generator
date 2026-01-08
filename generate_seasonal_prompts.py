import json
import datetime
from visual_schema import Trend, SubjectCategory, Style, Lighting, Composition, ColorPalette, VisualAttributes
from prompt_engine import PromptEngine

def generate_seasonal_prompts():
    engine = PromptEngine()
    
    # New Year Scenarios
    ny_scenarios = [
        # 1. Champagne Toast
        (
            VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE, Style.REALISTIC_PHOTOGRAPHY, Lighting.DRAMATIC, Composition.DYNAMIC_ANGLES, ColorPalette.WARM_COZY),
            "People & Lifestyle",
            "Close up of friends toasting with champagne glasses, golden bubbles, sparkles, celebration atmosphere, new year eve party, happiness"
        ),
        # 2. Fireworks
        (
            VisualAttributes(Trend.NEON_SURREALISM, SubjectCategory.ABSTRACT, Style.DIGITAL_ART_3D, Lighting.NEON_CYBERPUNK, Composition.SYMMETRICAL, ColorPalette.VIBRANT_NEON),
            "Abstract",
            "Colorful fireworks exploding in the night sky, vibrant colors, reflection on water, festive celebration, new beginnings"
        ),
        # 3. Clock
        (
            VisualAttributes(Trend.TIME_WARP, SubjectCategory.ABSTRACT, Style.CINEMATIC, Lighting.GOLDEN_HOUR, Composition.MACRO, ColorPalette.BOLD_CONTRAST),
            "Abstract",
            "Vintage golden pocket watch showing almost midnight, bokeh lights background, anticipation, classic new year countdown concept"
        ),
        # 4. Confetti Background
        (
            VisualAttributes(Trend.IMMERSIVE_APPEAL, SubjectCategory.ABSTRACT_TEXTURES, Style.MINIMALIST, Lighting.STUDIO_LIGHTING, Composition.KNOLLING, ColorPalette.PASTEL_DREAM),
            "Abstract & Textures",
            "Falling colorful confetti on plain background, festive texture, party decoration, minimal celebration pattern"
        ),
        # 5. Resolution/Planner
        (
            VisualAttributes(Trend.WORKPLACE_EVOLUTION, SubjectCategory.BUSINESS_WORK, Style.SCANDINAVIAN, Lighting.NATURAL_SOFT, Composition.KNOLLING, ColorPalette.EARTH_TONES),
            "Business & Work",
            "Open planner notebook with pen and coffee cup on wooden desk, clean page, fresh start, new year resolution concept"
        )
    ]

    # Valentine Scenarios
    val_scenarios = [
        # 1. Couple Sunset
        (
            VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE, Style.CINEMATIC, Lighting.GOLDEN_HOUR, Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
            "People & Lifestyle",
            "Couple holding hands walking on beach at sunset, romantic silhouette, love, peaceful atmosphere, valentines day date"
        ),
        # 2. Red Roses
        (
            VisualAttributes(Trend.GENERIC_BESTSELLER, SubjectCategory.NATURE, Style.PHOTOREALISTIC, Lighting.STUDIO_LIGHTING, Composition.CENTERED, ColorPalette.VIBRANT),
            "Nature",
            "Luxurious bouquet of fresh red roses, velvet texture, water droplets on petals, romantic gift, black background"
        ),
        # 3. Chocolates
        (
            VisualAttributes(Trend.IMMERSIVE_APPEAL, SubjectCategory.FOOD, Style.PHOTOREALISTIC, Lighting.NATURAL_SOFT, Composition.MACRO, ColorPalette.WARM_COZY),
            "Food",
            "Artisan heart shaped chocolates in a gift box, cocoa dusting, rich texture, delicious dessert, valentines gift"
        ),
        # 4. Gift Box
        (
            VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.ABSTRACT, Style.MINIMALIST, Lighting.NATURAL, Composition.NEGATIVE_SPACE, ColorPalette.PASTEL),
            "Abstract",
            "Single elegant gift box with red ribbon on pink background, minimalism, surprise, present, love symbol"
        ),
        # 5. Neon Heart
        (
            VisualAttributes(Trend.NEON_SURREALISM, SubjectCategory.ABSTRACT, Style.DIGITAL_ART_3D, Lighting.NEON, Composition.SYMMETRICAL, ColorPalette.NEON_DARK),
            "Abstract",
            "Glowing neon heart sign on brick wall, cyberpunk romance, future love, electric pink and blue light"
        )
    ]

    all_scenarios = ny_scenarios + val_scenarios
    results = []

    for i, (attrs, generic_name, specific_subject) in enumerate(all_scenarios):
        full_prompt_dict = engine.construct_full_prompt(attrs)
        base_prompt = full_prompt_dict['positive']
        
        # Replace the injected generic subject with our specific subject
        # Note: PromptEngine puts 'Trend Prefix' which often includes the SubjectCategory name
        # e.g. "Dynamic People & Lifestyle, action..."
        # We need to find the SubjectCategory string and replace it, or just append/prepend if not found exactly.
        # Ideally we replace the core subject description.
        
        # Taking a simpler approach: Reconstruct the prompt parts manually-ish or robust replace.
        # But Prompt engine output is a string.
        # Let's try flexible replacement: Replace the SubjectCategory value with specific subject.
        
        final_prompt = base_prompt.replace(generic_name, specific_subject)
        
        # Fallback if replace didn't work (e.g. if Trend prefix changed the wording slightly?? No, VisualAttributes uses Enum value)
        # VisualAttributes Enum values are exactly "People & Lifestyle" etc.
        
        results.append({
            "id": i+1,
            "theme": "New Year" if i < 5 else "Valentine",
            "subject": specific_subject,
            "prompt": final_prompt,
            "negative_prompt": full_prompt_dict['negative']
        })

    with open("seasonal_prompts.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    generate_seasonal_prompts()
