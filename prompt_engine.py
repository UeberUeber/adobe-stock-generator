from visual_schema import VisualAttributes, Trend, Style, Lighting, Composition, ColorPalette

class PromptEngine:
    """Constructs detailed prompts from visual attributes."""
    
    def __init__(self):
        # Clean, professional prefix without brand names
        self.base_style = "Professional stock photo, commercial quality, 8k resolution"
    
    def construct_prompt(self, attrs: VisualAttributes) -> str:
        parts = []
        
        # Subject & Trend handling
        if attrs.trend == Trend.FANTASTIC_FRONTIERS:
            parts.append(f"Surreal {attrs.subject_category.value}, dreamlike, floating elements")
        elif attrs.trend == Trend.LEVITY_AND_LAUGHTER:
            parts.append(f"Humorous {attrs.subject_category.value}, candid laughter, authentic")
        elif attrs.trend == Trend.TIME_WARP:
            parts.append(f"Retrofuturistic {attrs.subject_category.value}, vintage meets sci-fi")
        elif attrs.trend == Trend.IMMERSIVE_APPEAL:
            parts.append(f"Immersive {attrs.subject_category.value}, rich textures, tactile feel")
        elif attrs.trend == Trend.NEON_SURREALISM:
            parts.append(f"Cyberpunk {attrs.subject_category.value}, neon lights, futuristic city")
        elif attrs.trend == Trend.MINIMALIST_WELLNESS:
            parts.append(f"Zen {attrs.subject_category.value}, minimalist, calm, serene")
        elif attrs.trend == Trend.AUTHENTIC_MOMENTS:
            parts.append(f"Dynamic {attrs.subject_category.value}, action, motion blur, energy")
        elif attrs.trend == Trend.WORKPLACE_EVOLUTION:
            parts.append(f"Cozy {attrs.subject_category.value}, home office, warm interior")
        else:
            parts.append(f"Professional {attrs.subject_category.value}")
        
        # Standard attributes
        parts.append(f"Style: {attrs.style.value}")
        parts.append(f"Lighting: {attrs.lighting.value}")
        parts.append(f"Composition: {attrs.composition.value}")
        parts.append(f"Color: {attrs.color_palette.value}")
        
        # Quality boosters
        parts.insert(0, self.base_style)
        parts.append("16:9, highly detailed, sharp focus")
        
        return ", ".join(parts)
