from enum import Enum
import itertools
import random
from dataclasses import dataclass

class Trend(Enum):
    FANTASTIC_FRONTIERS = "Fantastic Frontiers"
    LEVITY_AND_LAUGHTER = "Levity and Laughter"
    TIME_WARP = "Time Warp"
    IMMERSIVE_APPEAL = "Immersive Appeal"
    GENERIC_BESTSELLER = "Generic BestSeller"
    NEON_SURREALISM = "Neo-Noir Cyberpunk"
    MINIMALIST_WELLNESS = "Minimalist Zen"
    AUTHENTIC_MOMENTS = "Dynamic Action"
    WORKPLACE_EVOLUTION = "Cozy Home Office"

class SubjectCategory(Enum):
    PEOPLE = "People"
    NATURE = "Nature"
    TECHNOLOGY = "Technology"
    BUSINESS = "Business"
    ABSTRACT = "Abstract"
    FOOD = "Food"
    SCIENCE_TECHNOLOGY = "Science & Tech"
    NATURE_OUTDOORS = "Nature & Outdoors"
    PEOPLE_LIFESTYLE = "People & Lifestyle"
    ABSTRACT_TEXTURES = "Abstract & Textures"
    BUSINESS_WORK = "Business & Work"

class Style(Enum):
    PHOTOREALISTIC = "Photorealistic"
    RENDER_3D = "3D Render"
    MINIMALIST = "Minimalist"
    VECTOR_FLAT = "Vector/Flat Art"
    CINEMATIC = "Cinematic"
    FUTURISTIC = "Futuristic"
    REALISTIC_PHOTOGRAPHY = "Realistic Photography"
    DIGITAL_ART_3D = "3D Digital Art"
    SCANDINAVIAN = "Scandinavian Interior"

class Lighting(Enum):
    NATURAL = "Natural Sunlight"
    STUDIO = "Studio Lighting"
    NEON = "Neon/Cyberpunk"
    GOLDEN_HOUR = "Golden Hour"
    NEON_CYBERPUNK = "Neon Cyberpunk"
    NATURAL_SOFT = "Natural Soft"
    DRAMATIC = "Dramatic High Contrast"
    STUDIO_LIGHTING = "Studio Lighting"
    WARM_GOLDEN_HOUR = "Warm Golden Hour"

class Composition(Enum):
    CENTERED = "Centered"
    RULE_OF_THIRDS = "Rule of Thirds"
    NEGATIVE_SPACE = "Negative Space"
    KNOLLING = "Knolling/Flat Lay"
    MACRO = "Macro/Close-up"
    SYMMETRICAL = "Symmetrical"
    MINIMALIST_NEGATIVE_SPACE = "Minimalist Negative Space"
    DYNAMIC_ANGLES = "Dynamic Angles"
    ABSTRACT_GEOMETRIC = "Abstract Geometric"

class ColorPalette(Enum):
    VIBRANT = "Vibrant & Saturated"
    PASTEL = "Pastel & Soft"
    EARTH_TONES = "Earth Tones"
    MONOCHROMATIC = "Monochromatic"
    NEON_DARK = "Dark with Neon Accents"
    VIBRANT_NEON = "Vibrant Neon"
    BOLD_CONTRAST = "Bold Contrast"
    PASTEL_DREAM = "Pastel Dream"
    WARM_COZY = "Warm Cozy"

@dataclass
class VisualAttributes:
    trend: Trend
    subject_category: SubjectCategory
    style: Style
    lighting: Lighting
    composition: Composition
    color_palette: ColorPalette

    def __str__(self):
        return (f"Trend: {self.trend.value} | Subject: {self.subject_category.value} | "
                f"Style: {self.style.value} | Light: {self.lighting.value} | "
                f"Comp: {self.composition.value} | Color: {self.color_palette.value}")

class SchemaGenerator:
    @staticmethod
    def generate_random() -> VisualAttributes:
        return VisualAttributes(
            trend=random.choice(list(Trend)),
            subject_category=random.choice(list(SubjectCategory)),
            style=random.choice(list(Style)),
            lighting=random.choice(list(Lighting)),
            composition=random.choice(list(Composition)),
            color_palette=random.choice(list(ColorPalette))
        )

    @staticmethod
    def generate_all_combinations():
        keys = [list(Trend), list(SubjectCategory), list(Style), 
                list(Lighting), list(Composition), list(ColorPalette)]
        for item in itertools.product(*keys):
            yield VisualAttributes(*item)
