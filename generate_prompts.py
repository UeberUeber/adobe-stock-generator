import os
import datetime
from visual_schema import Trend, SubjectCategory, Style, Lighting, Composition, ColorPalette, VisualAttributes
from prompt_engine import PromptEngine

def get_sample_prompts():
    """Generate 5 diverse sample prompts."""
    samples = [
        VisualAttributes(Trend.NEON_SURREALISM, SubjectCategory.SCIENCE_TECHNOLOGY,
                        Style.FUTURISTIC, Lighting.NEON_CYBERPUNK,
                        Composition.SYMMETRICAL, ColorPalette.VIBRANT_NEON),
        VisualAttributes(Trend.MINIMALIST_WELLNESS, SubjectCategory.NATURE_OUTDOORS,
                        Style.MINIMALIST, Lighting.NATURAL_SOFT,
                        Composition.MINIMALIST_NEGATIVE_SPACE, ColorPalette.EARTH_TONES),
        VisualAttributes(Trend.AUTHENTIC_MOMENTS, SubjectCategory.PEOPLE_LIFESTYLE,
                        Style.REALISTIC_PHOTOGRAPHY, Lighting.DRAMATIC,
                        Composition.DYNAMIC_ANGLES, ColorPalette.BOLD_CONTRAST),
        VisualAttributes(Trend.FANTASTIC_FRONTIERS, SubjectCategory.ABSTRACT_TEXTURES,
                        Style.DIGITAL_ART_3D, Lighting.STUDIO_LIGHTING,
                        Composition.ABSTRACT_GEOMETRIC, ColorPalette.PASTEL_DREAM),
        VisualAttributes(Trend.WORKPLACE_EVOLUTION, SubjectCategory.BUSINESS_WORK,
                        Style.SCANDINAVIAN, Lighting.WARM_GOLDEN_HOUR,
                        Composition.RULE_OF_THIRDS, ColorPalette.WARM_COZY),
    ]
    return samples

def generate_prompts():
    engine = PromptEngine()
    samples = get_sample_prompts()
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "generations", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"=== GENERATION RUN: {timestamp} ===")
    print(f"Output: {output_dir}\n")
    
    for i, sample in enumerate(samples):
        prompt = engine.construct_prompt(sample)
        print(f"[{i+1}] {sample.trend.value}")
        print(f"    {prompt}\n")

if __name__ == "__main__":
    generate_prompts()
