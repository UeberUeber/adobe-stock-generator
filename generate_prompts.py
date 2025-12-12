import os
import datetime
from visual_schema import Trend, SubjectCategory, Style, Lighting, Composition, ColorPalette, VisualAttributes
from prompt_engine import PromptEngine

def get_sample_prompts(count=10):
    """Generate diverse sample prompts using available enums."""
    samples = [
        # 1. Cyberpunk City
        VisualAttributes(Trend.NEON_SURREALISM, SubjectCategory.SCIENCE_TECHNOLOGY,
                        Style.FUTURISTIC, Lighting.NEON_CYBERPUNK,
                        Composition.SYMMETRICAL, ColorPalette.VIBRANT_NEON),
        # 2. Zen Nature
        VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.NATURE_OUTDOORS,
                        Style.MINIMALIST, Lighting.NATURAL_SOFT,
                        Composition.MINIMALIST_NEGATIVE_SPACE, ColorPalette.EARTH_TONES),
        # 3. Action Sports
        VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE,
                        Style.REALISTIC_PHOTOGRAPHY, Lighting.DRAMATIC,
                        Composition.DYNAMIC_ANGLES, ColorPalette.BOLD_CONTRAST),
        # 4. Abstract 3D
        VisualAttributes(Trend.FANTASTIC_FRONTIERS, SubjectCategory.ABSTRACT_TEXTURES,
                        Style.DIGITAL_ART_3D, Lighting.STUDIO_LIGHTING,
                        Composition.ABSTRACT_GEOMETRIC, ColorPalette.PASTEL_DREAM),
        # 5. Home Office
        VisualAttributes(Trend.WORKPLACE_EVOLUTION, SubjectCategory.BUSINESS_WORK,
                        Style.SCANDINAVIAN, Lighting.WARM_GOLDEN_HOUR,
                        Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
        # 6. Playful Lifestyle
        VisualAttributes(Trend.LEVITY_AND_LAUGHTER, SubjectCategory.PEOPLE_LIFESTYLE,
                        Style.REALISTIC_PHOTOGRAPHY, Lighting.NATURAL_SOFT,
                        Composition.CENTERED, ColorPalette.VIBRANT),
        # 7. AI Tech Innovation
        VisualAttributes(Trend.IMMERSIVE_APPEAL, SubjectCategory.TECHNOLOGY,
                        Style.DIGITAL_ART_3D, Lighting.STUDIO_LIGHTING,
                        Composition.ABSTRACT_GEOMETRIC, ColorPalette.NEON_DARK),
        # 8. Peaceful Nature
        VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.NATURE,
                        Style.CINEMATIC, Lighting.GOLDEN_HOUR,
                        Composition.NEGATIVE_SPACE, ColorPalette.PASTEL),
        # 9. Urban Architecture
        VisualAttributes(Trend.TIME_WARP, SubjectCategory.ABSTRACT,
                        Style.FUTURISTIC, Lighting.DRAMATIC,
                        Composition.SYMMETRICAL, ColorPalette.MONOCHROMATIC),
        # 10. Food Scene
        VisualAttributes(Trend.GENERIC_BESTSELLER, SubjectCategory.FOOD,
                        Style.PHOTOREALISTIC, Lighting.NATURAL,
                        Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
    ]
    return samples[:count]

def generate_prompts(count=10):
    engine = PromptEngine()
    samples = get_sample_prompts(count)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "generations", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save prompts to file
    prompts_file = os.path.join(output_dir, "prompts.txt")
    
    print(f"=== GENERATION RUN: {timestamp} ===")
    print(f"Output: {output_dir}\n")
    
    # Print and save negative prompt
    negative = engine.get_negative_prompt()
    print("=== NEGATIVE PROMPT (apply to all) ===")
    print(f"{negative}\n")
    print("=" * 50 + "\n")
    
    with open(prompts_file, 'w', encoding='utf-8') as f:
        f.write(f"=== Generation Run: {timestamp} ===\n")
        f.write(f"Total: {count} prompts\n\n")
        f.write(f"=== NEGATIVE PROMPT ===\n{negative}\n\n")
        f.write("=" * 50 + "\n\n")
        
        for i, sample in enumerate(samples):
            full_prompt = engine.construct_full_prompt(sample)
            print(f"[{i+1}] {sample.trend.value}")
            print(f"    POSITIVE: {full_prompt['positive'][:100]}...")
            print()
            
            f.write(f"[{i+1}] {sample.trend.value}\n")
            f.write(f"POSITIVE: {full_prompt['positive']}\n\n")
    
    print(f"\nPrompts saved to: {prompts_file}")
    print(f"\n👉 Next: Generate images with these prompts and save them to:\n   {output_dir}")
    return timestamp

if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    generate_prompts(count)
