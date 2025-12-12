"""
Prompt Metadata Extractor

Extracts structured metadata from image generation prompts and saves as JSON.
Follows Adobe Stock guidelines for titles, keywords, and categories.
"""

import os
import re
import json
from datetime import datetime
from typing import List, Dict, Optional

# Load guidelines for reference
GUIDELINES_PATH = os.path.join(os.path.dirname(__file__), "config", "adobe_stock_guidelines.md")

# Adobe Stock Category IDs
CATEGORY_MAP = {
    "animal": "1",
    "building": "2", "architecture": "2", "landmark": "2",
    "background": "3", "texture": "3", "pattern": "3", "abstract": "3",
    "business": "4", "office": "4", "corporate": "4",
    "drink": "5", "beverage": "5", "coffee": "5",
    "environment": "6",
    "emotion": "7", "mood": "7",
    "food": "8", "meal": "8", "cuisine": "8",
    "graphic": "9", "design": "9", "illustration": "9",
    "hobby": "10", "leisure": "10",
    "industry": "11",
    "landscape": "12", "nature": "12", "scenery": "12",
    "lifestyle": "13", "living": "13",
    "people": "14", "person": "14", "portrait": "14",
    "plant": "15", "flower": "15", "garden": "15",
    "culture": "16", "religion": "16",
    "science": "17", "research": "17",
    "social": "18",
    "sport": "19", "fitness": "19",
    "technology": "20", "tech": "20", "digital": "20", "cyber": "20",
    "transport": "21", "vehicle": "21", "car": "21",
    "travel": "22", "vacation": "22", "tourism": "22",
}

# Banned words in metadata (Adobe Stock policy)
BANNED_WORDS = [
    "ai", "artificial intelligence", "generated", "midjourney", "stable diffusion",
    "dall-e", "firefly", "neural", "machine learning", "deep learning",
    "picasso", "van gogh", "monet", "warhol", "banksy",
    "disney", "marvel", "dc comics", "pixar", "nintendo",
    "nike", "adidas", "apple", "google", "microsoft", "starbucks",
]


class PromptMetadataExtractor:
    """Extract Adobe Stock compliant metadata from prompts."""
    
    def __init__(self):
        pass
    
    def extract(self, prompt: str, custom_title: Optional[str] = None) -> Dict:
        """
        Extract metadata from a generation prompt.
        
        Args:
            prompt: The full image generation prompt
            custom_title: Optional custom title (if not provided, auto-generated)
            
        Returns:
            Dictionary with filename, title, keywords, category
        """
        # Clean and normalize prompt
        prompt_lower = prompt.lower()
        
        # Extract keywords from prompt
        keywords = self._extract_keywords(prompt)
        
        # Determine category
        category = self._determine_category(prompt_lower)
        
        # Generate title (max 70 chars, natural sentence)
        title = custom_title if custom_title else self._generate_title(prompt, keywords)
        
        # Generate filename
        filename = self._generate_filename(keywords)
        
        return {
            "filename": filename,
            "title": title,
            "keywords": keywords[:35],  # Max 35 keywords recommended
            "category": category,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
            "is_ai_generated": True,
            "is_fictional": True,
        }
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract relevant keywords from prompt."""
        # Remove common prompt patterns
        clean = prompt.lower()
        remove_patterns = [
            r"professional stock photo",
            r"8k resolution",
            r"4k resolution",
            r"high quality",
            r"no text",
            r"no logos",
            r"no watermarks",
            r"16:9 aspect ratio",
            r"\d+:\d+ aspect ratio",
        ]
        for pattern in remove_patterns:
            clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)
        
        # Split into words and phrases
        words = re.findall(r'[a-z]+(?:\s+[a-z]+)?', clean)
        
        # Filter and deduplicate
        seen = set()
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 2 and word not in seen:
                # Check if banned
                is_banned = any(banned in word for banned in BANNED_WORDS)
                if not is_banned:
                    seen.add(word)
                    keywords.append(word)
        
        # Sort by importance (longer phrases first, then by position)
        keywords.sort(key=lambda x: (-len(x.split()), keywords.index(x) if x in keywords else 999))
        
        return keywords[:50]  # Max 49 keywords allowed
    
    def _determine_category(self, prompt_lower: str) -> str:
        """Determine the best category based on prompt content."""
        category_scores = {}
        
        for keyword, cat_id in CATEGORY_MAP.items():
            if keyword in prompt_lower:
                category_scores[cat_id] = category_scores.get(cat_id, 0) + 1
        
        if category_scores:
            # Return category with highest score
            return max(category_scores, key=category_scores.get)
        
        # Default to Graphic Resources
        return "9"
    
    def _generate_title(self, prompt: str, keywords: List[str]) -> str:
        """Generate a natural, concise title (max 70 chars)."""
        # Take top 3-4 keywords and form a title
        top_keywords = keywords[:4]
        
        # Capitalize and join
        title_parts = [kw.title() for kw in top_keywords]
        title = " ".join(title_parts)
        
        # Add "Scene" or context if short
        if len(title) < 30:
            title += " Scene"
        
        # Truncate if too long
        if len(title) > 70:
            title = title[:67] + "..."
        
        return title
    
    def _generate_filename(self, keywords: List[str]) -> str:
        """Generate descriptive filename from keywords."""
        # Take top 3 keywords
        name_parts = [kw.replace(" ", "_") for kw in keywords[:3]]
        base_name = "_".join(name_parts)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{base_name}_{timestamp}.png"
    
    def save_metadata(self, metadata: Dict, output_dir: str) -> str:
        """
        Save metadata to JSON file alongside the image.
        
        Args:
            metadata: The metadata dictionary
            output_dir: Directory to save the JSON file
            
        Returns:
            Path to the saved JSON file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # JSON filename matches image filename
        json_filename = metadata["filename"].rsplit(".", 1)[0] + ".json"
        json_path = os.path.join(output_dir, json_filename)
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return json_path


def load_metadata_for_image(image_path: str) -> Optional[Dict]:
    """
    Load metadata JSON for an image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Metadata dictionary if JSON exists, None otherwise
    """
    json_path = image_path.rsplit(".", 1)[0] + ".json"
    
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return None


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        extractor = PromptMetadataExtractor()
        metadata = extractor.extract(prompt)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
    else:
        print("Usage: python prompt_metadata.py <prompt>")
