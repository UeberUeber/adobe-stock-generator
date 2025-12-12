from visual_schema import VisualAttributes, Trend, Style, Lighting, Composition, ColorPalette

class PromptEngine:
    """Constructs detailed prompts from visual attributes."""
    
    def __init__(self):
        # Clean, professional prefix without brand names
        self.base_style = "Professional stock photo, commercial quality, 8k resolution"
        
        # === NEGATIVE PROMPTS FOR IP AVOIDANCE & QUALITY ===
        # These MUST be included to avoid Adobe Stock rejection
        self.negative_prompts = [
            # Brand/Logo Avoidance (Critical for IP compliance)
            "no logos", "no brand names", "no trademarks", "no company logos",
            "no text", "no letters", "no words", "no writing", "no signage",
            "no watermarks", "no stamps", "no emblems", "no symbols",
            
            # Specific Brand Avoidance (Common in office/tech scenes)
            "no apple logo", "no macbook", "no iphone", "no ipad",
            "no microsoft logo", "no windows logo", "no google logo",
            "no samsung", "no dell", "no hp logo", "no lenovo",
            "no nike swoosh", "no adidas", "no coca cola", "no starbucks",
            
            # Anatomy/Quality Issues (Common AI rejection reasons)
            "no deformed hands", "no extra fingers", "no missing fingers",
            "no malformed limbs", "no distorted faces", "no asymmetric eyes",
            "no blurry", "no pixelated", "no grainy", "no noise",
            "no artifacts", "no glitches", "no compression artifacts",
            
            # Legal/Editorial Issues
            "no celebrities", "no famous people", "no politicians",
            "no copyrighted characters", "no fictional characters",
            "no flags", "no currency", "no government symbols",
            
            # Content Policy Issues
            "no violence", "no weapons", "no drugs", "no alcohol visible",
            "no nudity", "no suggestive content",
        ]
    
    def get_negative_prompt(self) -> str:
        """Return the complete negative prompt string."""
        return ", ".join(self.negative_prompts)
    
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
            parts.append(f"Cozy {attrs.subject_category.value}, home office, warm interior, generic laptop, plain monitor")
        else:
            parts.append(f"Professional {attrs.subject_category.value}")
        
        # Standard attributes
        parts.append(f"Style: {attrs.style.value}")
        parts.append(f"Lighting: {attrs.lighting.value}")
        parts.append(f"Composition: {attrs.composition.value}")
        parts.append(f"Color: {attrs.color_palette.value}")
        
        # Quality boosters - enhanced for Adobe Stock approval
        parts.insert(0, self.base_style)
        parts.append("16:9 aspect ratio, ultra sharp focus, no blur, no noise, no artifacts")
        parts.append("professional DSLR quality, crisp details, clean edges, studio lighting")
        
        # IP Safety additions
        parts.append("generic unbranded items, no visible logos or text, plain surfaces")
        
        return ", ".join(parts)
    
    def construct_full_prompt(self, attrs: VisualAttributes) -> dict:
        """Return both positive and negative prompts for image generation."""
        return {
            "positive": self.construct_prompt(attrs),
            "negative": self.get_negative_prompt(),
        }
