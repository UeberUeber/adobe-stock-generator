"""
Adobe Stock Metadata Generator
Generates submission-compliant metadata following Adobe Stock Generative AI Guidelines.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
import re
import os
import json

# Adobe Stock Category IDs (most common ones)
class AdobeCategory(Enum):
    ANIMALS = "1"
    BUILDINGS_LANDMARKS = "2"
    BACKGROUNDS_TEXTURES = "3"
    BUSINESS = "4"
    DRINKS = "5"
    ENVIRONMENT = "6"
    STATES_OF_MIND = "7"
    FOOD = "8"
    GRAPHIC_RESOURCES = "9"
    HOBBIES_LEISURE = "10"
    INDUSTRY = "11"
    LANDSCAPES = "12"
    LIFESTYLE = "13"
    PEOPLE = "14"
    PLANTS_FLOWERS = "15"
    CULTURE_RELIGION = "16"
    SCIENCE = "17"
    SOCIAL_ISSUES = "18"
    SPORTS = "19"
    TECHNOLOGY = "20"
    TRANSPORT = "21"
    TRAVEL = "22"

class AssetType(Enum):
    PHOTO = "photo"
    ILLUSTRATION = "illustration"

# Banned words/phrases that violate Adobe Stock guidelines
BANNED_PATTERNS = [
    # AI-related terms (not allowed in title/keywords)
    r'\bai\b', r'\bartificial intelligence\b', r'\bgenerat(?:ed|ive)\b',
    r'\bmidjourney\b', r'\bstable diffusion\b', r'\bdall-?e\b', r'\bfirefly\b',
    r'\bneural\b', r'\bmachine learning\b', r'\bdeep learning\b',
    
    # Famous artists (copyright concerns)
    r'\bpicasso\b', r'\bvan gogh\b', r'\bmonet\b', r'\bdali\b', r'\bwarhol\b',
    r'\bbanksy\b', r'\brembrandt\b', r'\bmichelangelo\b', r'\bdavinci\b',
    r'\bgreg rutkowski\b', r'\bartgerm\b', r'\balkke\b', r'\bwlop\b',
    
    # Famous people
    r'\belon musk\b', r'\btrump\b', r'\bobama\b', r'\bbiden\b',
    r'\btaylor swift\b', r'\bbeyonce\b', r'\bkanye\b',
    
    # Fictional characters / IP
    r'\bmarvel\b', r'\bdc comics\b', r'\bdisney\b', r'\bpixar\b',
    r'\bspiderman\b', r'\bbatman\b', r'\bsuperman\b', r'\biron man\b',
    r'\bstar wars\b', r'\bharry potter\b', r'\bpokemon\b', r'\bmario\b',
    
    # Brands
    r'\bapple\b', r'\bgoogle\b', r'\bmicrosoft\b', r'\bnike\b', r'\badidas\b',
    r'\bcoca cola\b', r'\bmcdonalds\b', r'\bstarbucks\b',
    
    # Government agencies
    r'\bfbi\b', r'\bcia\b', r'\bnasa\b', r'\bpentagon\b',
]

@dataclass
class StockMetadata:
    """Adobe Stock compliant metadata structure."""
    filename: str
    title: str
    keywords: List[str]
    category: AdobeCategory
    asset_type: AssetType = AssetType.PHOTO
    is_generative_ai: bool = True  # Always True for AI-generated content
    is_fictional: bool = True      # True if people/property are AI-generated
    
    # Universal filler keywords for when we need to reach minimum
    FILLER_KEYWORDS = [
        "high quality", "professional", "detailed", "modern", "creative",
        "background", "concept", "design", "commercial", "stock image"
    ]
    
    def get_keywords_str(self, min_count: int = 5, max_count: int = 50) -> str:
        """Return comma-separated keywords (min 5, max 50 for Adobe Stock)."""
        filtered = self._filter_banned_words(self.keywords)
        
        # Ensure minimum 5 keywords
        if len(filtered) < min_count:
            for filler in self.FILLER_KEYWORDS:
                if filler.lower() not in [k.lower() for k in filtered]:
                    filtered.append(filler)
                if len(filtered) >= min_count:
                    break
        
        return ", ".join(filtered[:max_count])
    
    def get_clean_title(self) -> str:
        """Return title with banned words removed."""
        clean = self._filter_banned_text(self.title)
        # Ensure title is not empty
        if not clean or len(clean) < 5:
            clean = f"Professional {self.category.name.replace('_', ' ').title()} Image"
        return clean
    
    def _filter_banned_words(self, words: List[str]) -> List[str]:
        """Remove banned words from keyword list."""
        result = []
        for word in words:
            is_banned = any(re.search(pattern, word.lower()) for pattern in BANNED_PATTERNS)
            if not is_banned:
                result.append(word)
        return result
    
    def _filter_banned_text(self, text: str) -> str:
        """Remove banned patterns from text."""
        result = text
        for pattern in BANNED_PATTERNS:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        return re.sub(r'\s+', ' ', result).strip()
    
    def to_csv_row(self) -> dict:
        """Convert to CSV row format for Adobe Stock submission."""
        return {
            "Filename": self.filename,
            "Title": self.get_clean_title(),
            "Keywords": self.get_keywords_str(min_count=5, max_count=50),
            "Category": self.category.value,
            "Releases": "",  # No model/property release for fictional AI content
        }


# Mapping from visual schema to metadata with RICH SALES KEYWORDS
# Goal: 30+ keywords per image, optimized for discovery
TREND_METADATA = {
    "Fantastic Frontiers": {
        "title_prefix": "Surreal Dreamlike",
        "keywords": [
            "surreal", "fantasy", "dream", "dreamlike", "imagination", "ethereal", "mystical",
            "floating", "levitation", "magic", "magical", "otherworldly", "conceptual", "abstract",
            "creativity", "artistic", "inspiration", "mind", "subconscious", "psychedelic",
            "digital art", "3d render", "illustration", "background", "wallpaper", "futuristic",
            "space", "dimension", "reality", "vision"
        ],
        "category": AdobeCategory.GRAPHIC_RESOURCES,
        "asset_type": AssetType.ILLUSTRATION,
    },
    "Levity and Laughter": {
        "title_prefix": "Joyful Candid",
        "keywords": [
            "joy", "happiness", "laughter", "laughing", "smile", "smiling", "happy", "cheerful",
            "positive", "emotion", "candid", "authentic", "real", "genuine", "fun", "funny",
            "humor", "playful", "enjoyment", "delight", "carefree", "leisure", "lifestyle",
            "people", "person", "portrait", "good vibes", "optimistic", "bright", "sunny"
        ],
        "category": AdobeCategory.LIFESTYLE,
        "asset_type": AssetType.PHOTO,
    },
    "Time Warp": {
        "title_prefix": "Retro Futuristic Sci-Fi",
        "keywords": [
            "retro", "vintage", "futuristic", "retrofuturism", "sci-fi", "science fiction",
            "nostalgia", "nostalgic", "neon", "80s", "90s", "synthwave", "vaporwave", "cyber",
            "technology", "future", "past", "time travel", "conceptual", "artistic", "digital art",
            "illustration", "graphic", "design", "creative", "background", "poster", "cover"
        ],
        "category": AdobeCategory.GRAPHIC_RESOURCES,
        "asset_type": AssetType.ILLUSTRATION,
    },
    "Immersive Appeal": {
        "title_prefix": "Tactile Textured",
        "keywords": [
            "texture", "pattern", "background", "surface", "tactile", "detailed", "macro",
            "close-up", "material", "fabric", "organic", "abstract", "design", "wallpaper",
            "backdrop", "rough", "smooth", "soft", "hard", "quality", "high resolution",
            "full frame", "copy space", "blank", "template", "artistic", "creative"
        ],
        "category": AdobeCategory.BACKGROUNDS_TEXTURES,
        "asset_type": AssetType.PHOTO,
    },
    "Generic BestSeller": {
        "title_prefix": "Professional Commercial",
        "keywords": [
            "professional", "commercial", "business", "corporate", "success", "modern", "clean",
            "minimal", "background", "concept", "strategy", "innovation", "ideas", "planning",
            "office", "work", "job", "career", "development", "growth", "finance", "economy",
            "marketing", "advertising", "copy space", "presentation", "stock", "quality"
        ],
        "category": AdobeCategory.BUSINESS,
        "asset_type": AssetType.PHOTO,
    },
    "Neo-Noir Cyberpunk": {
        "title_prefix": "Futuristic Neon Cyberpunk",
        "keywords": [
            "cyberpunk", "neon", "futuristic", "city", "urban", "night", "technology", "sci-fi",
            "lights", "glowing", "cyber", "digital", "virtual", "reality", "metaverse", "future",
            "innovation", "tech", "smart city", "architecture", "building", "street", "dystopian",
            "utopian", "modern", "vibrant", "colorful", "dark", "moody", "atmospheric"
        ],
        "category": AdobeCategory.TECHNOLOGY,
        "asset_type": AssetType.ILLUSTRATION,
    },
    "Minimalist Zen": {
        "title_prefix": "Minimalist Zen",
        "keywords": [
            "minimalist", "minimalism", "simple", "simplicity", "zen", "calm", "peace", "peaceful",
            "serene", "tranquil", "quiet", "relax", "relaxation", "meditation", "mindfulness",
            "balance", "harmony", "nature", "natural", "clean", "fresh", "copy space", "background",
            "white space", "poster", "health", "wellness", "backgrounds", "soft"
        ],
        "category": AdobeCategory.LANDSCAPES,
        "asset_type": AssetType.PHOTO,
    },
    "Dynamic Action": {
        "title_prefix": "Dynamic High Energy",
        "keywords": [
            "action", "dynamic", "motion", "speed", "energy", "power", "strength", "fast",
            "movement", "active", "sport", "fitness", "exercise", "workout", "healthy", "lifestyle",
            "competitive", "challenge", "effort", "adrenaline", "intense", "blur", "impact",
            "strong", "determination", "focus", "success", "achievement", "goal"
        ],
        "category": AdobeCategory.SPORTS,
        "asset_type": AssetType.PHOTO,
    },
    "Cozy Home Office": {
        "title_prefix": "Modern Cozy Home Office",
        "keywords": [
            "home office", "workspace", "desk", "computer", "laptop", "work", "working", "remote work",
            "telecommute", "freelance", "business", "interior", "design", "room", "furniture",
            "cozy", "warm", "comfortable", "modern", "scandinavian", "lifestyle", "career",
            "productivity", "creative", "startup", "entrepreneur", "technology", "internet", "online"
        ],
        "category": AdobeCategory.BUSINESS,
        "asset_type": AssetType.PHOTO,
    },
}

SUBJECT_KEYWORDS = {
    "People": ["people", "person", "human", "adult", "model", "portrait", "lifestyle", "diversity", "authentic"],
    "Nature": ["nature", "outdoor", "environment", "landscape", "scenery", "natural", "beauty", "earth", "green"],
    "Technology": ["technology", "tech", "digital", "electronic", "device", "innovation", "future", "modern", "smart"],
    "Business": ["business", "corporate", "professional", "office", "work", "job", "career", "success", "finance"],
    "Abstract": ["abstract", "art", "artistic", "design", "pattern", "shape", "color", "concept", "creative"],
    "Food": ["food", "delicious", "tasty", "gourmet", "meal", "dish", "healthy", "fresh", "eating", "cuisine"],
    "Science & Tech": ["science", "technology", "research", "lab", "data", "analysis", "innovation", "futuristic"],
    "Nature & Outdoors": ["nature", "outdoors", "landscape", "sky", "view", "environment", "travel", "adventure"],
    "People & Lifestyle": ["lifestyle", "people", "living", "life", "everyday", "authentic", "candid", "real"],
    "Abstract & Textures": ["abstract", "texture", "surface", "background", "pattern", "design", "material"],
    "Business & Work": ["business", "work", "office", "professional", "corporate", "team", "success", "strategy"],
}

STYLE_KEYWORDS = {
    "Photorealistic": ["realistic", "photo", "photography", "high quality", "detailed", "sharp"],
    "3D Render": ["3d", "render", "digital art", "illustration", "cgi", "computer generated", "dimensional"],
    "Minimalist": ["minimalist", "minimal", "simple", "clean", "modern", "less is more", "uncluttered"],
    "Vector/Flat Art": ["vector", "flat", "illustration", "graphic", "design", "art", "drawing"],
    "Cinematic": ["cinematic", "film", "movie", "dramatic", "scene", "story", "composition"],
    "Futuristic": ["futuristic", "future", "sci-fi", "advanced", "modern", "tech", "innovation"],
    "Realistic Photography": ["photography", "photo", "image", "pic", "shot", "capture", "realistic"],
    "3D Digital Art": ["3d", "digital", "art", "render", "creative", "design", "virtua"],
    "Scandinavian Interior": ["scandinavian", "nordic", "interior", "design", "home", "decor", "style"],
}

LIGHTING_KEYWORDS = {
    "Natural Sunlight": ["natural light", "sunlight", "sun", "day", "daylight", "bright", "sunny"],
    "Studio Lighting": ["studio", "lighting", "professional", "controlled", "bright", "clear"],
    "Neon/Cyberpunk": ["neon", "glow", "light", "color", "colorful", "dark", "night"],
    "Golden Hour": ["golden hour", "sunset", "sunrise", "warm", "light", "beautiful", "glow"],
    "Neon Cyberpunk": ["neon", "cyberpunk", "glow", "vibrant", "electric", "night"],
    "Natural Soft": ["soft", "light", "gentle", "diffused", "calm", "pleasant"],
    "Dramatic High Contrast": ["dramatic", "contrast", "shadow", "light", "dark", "moody", "intense"],
    "Warm Golden Hour": ["warm", "golden", "glow", "sun", "light", "atmosphere"],
}

COLOR_KEYWORDS = {
    "Vibrant & Saturated": ["vibrant", "colorful", "color", "bright", "saturated", "vivid", "rich"],
    "Pastel & Soft": ["pastel", "soft", "color", "gentle", "pale", "light", "delicate"],
    "Earth Tones": ["earth", "tone", "natural", "brown", "green", "beige", "neutral"],
    "Monochromatic": ["monochromatic", "single color", "tone", "shade", "unified", "simple"],
    "Dark with Neon Accents": ["dark", "black", "neon", "contrast", "glow", "light"],
    "Vibrant Neon": ["neon", "vibrant", "bright", "glowing", "electric", "color"],
    "Bold Contrast": ["bold", "contrast", "strong", "striking", "impact"],
    "Pastel Dream": ["pastel", "dream", "soft", "color", "fantasy", "light"],
    "Warm Cozy": ["warm", "cozy", "inviting", "home", "comfort", "color"],
}


class MetadataGenerator:
    """Generates sales-optimized Adobe Stock compliant metadata."""
    
    def generate(self, filename: str, trend: str, subject: str, 
                 style: str, lighting: str, color: str, 
                 override_category: Optional[AdobeCategory] = None) -> StockMetadata:
        """Generate complete, rich metadata for an image."""
        
        # Get trend-based metadata
        trend_data = TREND_METADATA.get(trend, TREND_METADATA["Generic BestSeller"])
        
        # Determine Category: Use override if provided, else trend default
        category = override_category if override_category else trend_data["category"]
        
        # Build title from filename keywords (NOT templates)
        # Extract meaningful words from filename
        name_without_ext = filename.rsplit(".", 1)[0]
        # Remove timestamp patterns like _1765540915528 or _20251212
        import re
        name_clean = re.sub(r'_\d{10,}$', '', name_without_ext)  # Remove Unix timestamps
        name_clean = re.sub(r'_\d{8}_\d{6}$', '', name_clean)   # Remove YYYYMMDD_HHMMSS
        name_clean = re.sub(r'_\d+$', '', name_clean)           # Remove any trailing numbers
        
        # Convert underscores to spaces and capitalize
        title_words = name_clean.replace('_', ' ').replace('-', ' ').split()
        title_words = [w.capitalize() for w in title_words if len(w) > 1]
        
        # Create natural title (max 70 chars)
        if title_words:
            title = ' '.join(title_words)
            # DO NOT add subject suffix - keep title clean and descriptive
        else:
            # Fallback: use subject only if no words from filename
            title = f"{subject.replace('&', 'and')} Scene"
        
        # Truncate if too long
        if len(title) > 70:
            title = title[:67] + "..."
        
        # Collect keywords - START with filename keywords (most relevant)
        keywords = []
        
        # Add filename-derived keywords FIRST (highest priority)
        for w in title_words:
            keywords.append(w.lower())
        
        # Add subject-related keywords (NOT the generic trend keywords)
        keywords.extend(SUBJECT_KEYWORDS.get(subject, []))
        keywords.extend(STYLE_KEYWORDS.get(style, []))
        keywords.extend(LIGHTING_KEYWORDS.get(lighting, []))
        keywords.extend(COLOR_KEYWORDS.get(color, []))
        
        # NOTE: Removed generic "Sales Booster Keywords" like "professional, commercial, stock photo"
        # These are considered spam by Adobe Stock if not relevant to actual content
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            clean_kw = kw.lower().strip()
            if clean_kw and clean_kw not in seen:
                seen.add(clean_kw)
                unique_keywords.append(kw)
        
        # Determine if people are in the image
        has_people = any(p in subject.lower() for p in ["people", "person", "lifestyle", "portrait"])
        
        return StockMetadata(
            filename=filename,
            title=title,
            keywords=unique_keywords,
            category=category,
            asset_type=trend_data["asset_type"],
            is_generative_ai=True,
            is_fictional=has_people,  # Mark as fictional if contains people
        )
    
    def generate_from_filename(self, filename: str, image_dir: str = None) -> StockMetadata:
        """
        Generate metadata by loading JSON sidecar or parsing filename patterns.
        
        Args:
            filename: Image filename
            image_dir: Optional directory containing the image (for JSON lookup)
        """
        # === TRY JSON METADATA FIRST ===
        if image_dir:
            json_path = os.path.join(image_dir, filename.rsplit(".", 1)[0] + ".json")
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    
                    # Determine category from JSON or infer
                    category = AdobeCategory.GRAPHIC_RESOURCES  # Default
                    if "category" in meta:
                        for cat in AdobeCategory:
                            if cat.value == str(meta["category"]):
                                category = cat
                                break
                    
                    return StockMetadata(
                        filename=filename,
                        title=meta.get("title", "Professional Stock Image"),
                        keywords=meta.get("keywords", []),
                        category=category,
                        is_generative_ai=meta.get("is_ai_generated", True),
                        is_fictional=meta.get("is_fictional", True),
                    )
                except Exception as e:
                    print(f"Warning: Could not load JSON metadata: {e}")
        
        # === FALLBACK: Parse filename patterns ===
        fname_lower = filename.lower()
        
        # Default implicit values
        trend = "Generic BestSeller"
        subject = "Business & Work"
        style = "Photorealistic"
        lighting = "Studio Lighting"
        color = "Vibrant & Saturated"
        category_override = None
        
        # 1. Match known TREND patterns
        if "neon" in fname_lower or "cyberpunk" in fname_lower:
            trend = "Neo-Noir Cyberpunk"
            subject = "Science & Tech"
            style = "Futuristic"
            lighting = "Neon Cyberpunk"
            color = "Vibrant Neon"
        elif "zen" in fname_lower or "minimalist" in fname_lower:
            trend = "Minimalist Zen"
            subject = "Nature & Outdoors"
            style = "Minimalist"
            lighting = "Natural Soft"
            color = "Earth Tones"
        elif "action" in fname_lower or "dynamic" in fname_lower:
            trend = "Dynamic Action"
            subject = "People & Lifestyle"
            style = "Realistic Photography"
            lighting = "Dramatic High Contrast"
            color = "Bold Contrast"
        elif "abstract" in fname_lower or "3d" in fname_lower:
            trend = "Fantastic Frontiers"
            subject = "Abstract & Textures"
            style = "3D Digital Art"
            lighting = "Studio Lighting"
            color = "Pastel Dream"
        elif "office" in fname_lower or "cozy" in fname_lower:
            trend = "Cozy Home Office"
            subject = "Business & Work"
            style = "Scandinavian Interior"
            lighting = "Warm Golden Hour"
            color = "Warm Cozy"
        
        # 2. Smart Category Inference (Overrides Trend Default)
        # Check specific keywords to assign correct Adobe Category
        if any(w in fname_lower for w in ["cat", "dog", "animal", "pet", "wildlife", "bird"]):
            category_override = AdobeCategory.ANIMALS
            subject = "Nature"
        elif any(w in fname_lower for w in ["food", "drink", "coffee", "meal", "fruit", "dish"]):
            category_override = AdobeCategory.FOOD
            subject = "Food"
        elif any(w in fname_lower for w in ["building", "architecture", "city", "house", "skyscraper"]):
            category_override = AdobeCategory.BUILDINGS_LANDMARKS
        elif any(w in fname_lower for w in ["flower", "plant", "garden", "tree", "forest", "jungle"]):
            category_override = AdobeCategory.PLANTS_FLOWERS
            subject = "Nature & Outdoors"
        elif any(w in fname_lower for w in ["tech", "circuit", "computer", "robot", "ai", "data"]):
            category_override = AdobeCategory.TECHNOLOGY
            subject = "Science & Tech"
        elif any(w in fname_lower for w in ["travel", "vacation", "trip", "tourist", "landmark"]):
            category_override = AdobeCategory.TRAVEL
            subject = "Nature & Outdoors"
        elif any(w in fname_lower for w in ["business", "office", "meeting", "chart", "finance"]):
            category_override = AdobeCategory.BUSINESS
            subject = "Business & Work"
        elif any(w in fname_lower for w in ["sport", "fitness", "gym", "run", "yoga"]):
            category_override = AdobeCategory.SPORTS
            subject = "People & Lifestyle"
        
        # 3. Fallback logic for basic subjects if no trend was matched
        if trend == "Generic BestSeller" and not category_override:
             if "nature" in fname_lower: 
                subject = "Nature & Outdoors"
                style = "Realistic Photography"
                lighting = "Natural Sunlight"
                color = "Earth Tones"
                category_override = AdobeCategory.LANDSCAPES
             elif "texture" in fname_lower or "background" in fname_lower:
                 subject = "Abstract & Textures"
                 category_override = AdobeCategory.BACKGROUNDS_TEXTURES

        return self.generate(
            filename=filename,
            trend=trend,
            subject=subject,
            style=style,
            lighting=lighting,
            color=color,
            override_category=category_override
        )


# CSV Export helpers
def get_csv_headers() -> List[str]:
    """Return CSV headers for Adobe Stock submission."""
    return ["Filename", "Title", "Keywords", "Category", "Releases"]


def metadata_to_csv_rows(metadata_list: List[StockMetadata]) -> List[dict]:
    """Convert list of metadata to CSV rows."""
    return [m.to_csv_row() for m in metadata_list]
