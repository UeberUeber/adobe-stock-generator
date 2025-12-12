"""
AI-based Metadata Generator using Gemini API
Analyzes images and generates accurate Adobe Stock metadata including category inference.
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Optional, List

# Adobe Stock Categories - 20 official categories
ADOBE_STOCK_CATEGORIES = {
    "1": "Animals",
    "2": "Buildings and Architecture",
    "3": "Business",
    "4": "Drinks",
    "5": "The Environment",
    "6": "States of Mind",
    "7": "Food",
    "8": "Graphic Resources",
    "9": "Hobbies and Leisure",
    "10": "Industry",
    "11": "Landscapes",
    "12": "Lifestyle",
    "13": "People",
    "14": "Plants and Flowers",
    "15": "Culture and Religion",
    "16": "Science",
    "17": "Social Issues",
    "18": "Sports",
    "19": "Technology",
    "20": "Transport",
    "21": "Travel",
}

# Category descriptions for better AI inference
CATEGORY_DESCRIPTIONS = {
    "1": "Animals: pets, wildlife, birds, fish, insects, zoo animals",
    "2": "Buildings and Architecture: houses, skyscrapers, landmarks, interior design, construction",
    "3": "Business: office, corporate, meetings, finance, professional work",
    "4": "Drinks: coffee, tea, cocktails, beverages, wine, beer",
    "5": "The Environment: ecology, sustainability, climate, pollution, nature conservation",
    "6": "States of Mind: emotions, feelings, moods, psychology, mental health",
    "7": "Food: meals, dishes, cuisine, cooking, ingredients, restaurants",
    "8": "Graphic Resources: abstract, patterns, textures, backgrounds, design elements",
    "9": "Hobbies and Leisure: games, crafts, entertainment, recreation, relaxation",
    "10": "Industry: factories, manufacturing, machinery, production, logistics",
    "11": "Landscapes: mountains, beaches, forests, nature scenery, countryside",
    "12": "Lifestyle: everyday life, home, family, wellness, fashion",
    "13": "People: portraits, groups, diversity, ages, professions",
    "14": "Plants and Flowers: gardens, trees, floral, botanical, agriculture",
    "15": "Culture and Religion: traditions, holidays, celebrations, Christmas, festivals, religious symbols",
    "16": "Science: research, laboratory, experiments, medicine, biology",
    "17": "Social Issues: community, society, politics, activism, humanitarian",
    "18": "Sports: fitness, athletics, exercise, games, outdoor activities",
    "19": "Technology: computers, gadgets, innovation, digital, AI, robots",
    "20": "Transport: vehicles, cars, planes, trains, roads, traffic",
    "21": "Travel: tourism, vacation, destinations, landmarks, adventure",
}

# Banned words in Adobe Stock metadata
BANNED_WORDS = [
    "ai", "artificial intelligence", "generated", "midjourney", "stable diffusion",
    "dall-e", "firefly", "neural", "machine learning", "deep learning",
    "picasso", "van gogh", "monet", "warhol", "banksy", "greg rutkowski",
    "disney", "marvel", "dc comics", "pixar", "nintendo",
    "nike", "adidas", "apple", "google", "microsoft", "starbucks",
    "coca cola", "mcdonalds", "canon", "nikon", "4k", "8k", "hd",
]


class AIMetadataGenerator:
    """Generate Adobe Stock metadata using Gemini API for image analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI Metadata Generator.
        
        Args:
            api_key: Google AI API key. If not provided, reads from GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
                print("[AIMetadataGenerator] Gemini API initialized successfully")
            except ImportError:
                print("[AIMetadataGenerator] google-generativeai not installed. Run: pip install google-generativeai")
            except Exception as e:
                print(f"[AIMetadataGenerator] Failed to initialize Gemini: {e}")
        else:
            print("[AIMetadataGenerator] No API key found. Set GOOGLE_API_KEY environment variable.")
    
    def _build_category_prompt(self) -> str:
        """Build the category list for the prompt."""
        lines = ["Choose the SINGLE most appropriate category from this list:"]
        for cat_id, desc in CATEGORY_DESCRIPTIONS.items():
            lines.append(f"  {cat_id}: {desc}")
        return "\n".join(lines)
    
    def _clean_keywords(self, keywords: List[str]) -> List[str]:
        """Remove banned words from keywords."""
        cleaned = []
        for kw in keywords:
            kw_lower = kw.lower().strip()
            is_banned = any(banned in kw_lower for banned in BANNED_WORDS)
            if not is_banned and len(kw_lower) > 1:
                cleaned.append(kw)
        return cleaned
    
    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """
        Analyze an image using Gemini and generate metadata.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with title, keywords, category, category_name
        """
        if not self.model:
            print("[AIMetadataGenerator] Model not initialized, using fallback")
            return None
        
        if not os.path.exists(image_path):
            print(f"[AIMetadataGenerator] Image not found: {image_path}")
            return None
        
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Determine mime type
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
            }.get(ext, "image/png")
            
            # Build prompt
            prompt = f"""Analyze this image for Adobe Stock submission and provide metadata.

{self._build_category_prompt()}

IMPORTANT RULES:
- Title: Natural sentence, max 70 characters, describe the main subject
- Keywords: 20-35 relevant keywords, single words or short phrases
- DO NOT include: AI, generated, brand names, celebrity names, camera info
- Focus on: subject, mood, style, colors, composition, use case

Respond in this EXACT JSON format:
{{
    "title": "Descriptive natural title for stock photo",
    "keywords": ["keyword1", "keyword2", "keyword3", ...],
    "category_id": "15",
    "category_name": "Culture and Religion"
}}

Analyze the image and respond with ONLY the JSON, no other text."""

            # Call Gemini API
            import google.generativeai as genai
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": mime_type, "data": image_data}
            ])
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            result = json.loads(response_text)
            
            # Validate and clean
            result["keywords"] = self._clean_keywords(result.get("keywords", []))
            result["category_id"] = str(result.get("category_id", "8"))
            
            # Ensure category_name matches category_id
            result["category_name"] = ADOBE_STOCK_CATEGORIES.get(
                result["category_id"], 
                "Graphic Resources"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"[AIMetadataGenerator] Failed to parse JSON response: {e}")
            print(f"Response was: {response_text[:500] if 'response_text' in dir() else 'N/A'}")
            return None
        except Exception as e:
            print(f"[AIMetadataGenerator] Error analyzing image: {e}")
            return None
    
    def generate_metadata_json(self, image_path: str, output_dir: Optional[str] = None) -> Optional[str]:
        """
        Generate and save metadata JSON file for an image.
        
        Args:
            image_path: Path to the image file
            output_dir: Directory to save JSON (default: same as image)
            
        Returns:
            Path to saved JSON file, or None if failed
        """
        result = self.analyze_image(image_path)
        
        if not result:
            return None
        
        # Build full metadata
        filename = os.path.basename(image_path)
        metadata = {
            "filename": filename,
            "title": result.get("title", "Stock Image"),
            "keywords": result.get("keywords", []),
            "category": result.get("category_id", "8"),
            "category_name": result.get("category_name", "Graphic Resources"),
            "asset_type": "photo",
            "is_ai_generated": True,
            "is_fictional": True,
            "created_at": datetime.now().isoformat(),
        }
        
        # Determine output path
        if output_dir is None:
            output_dir = os.path.dirname(image_path)
        
        json_filename = filename.rsplit(".", 1)[0] + ".json"
        json_path = os.path.join(output_dir, json_filename)
        
        # Save JSON
        os.makedirs(output_dir, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4, ensure_ascii=False)
        
        print(f"[AIMetadataGenerator] Saved: {json_path}")
        return json_path
    
    def batch_generate(self, image_dir: str, skip_existing: bool = True) -> List[str]:
        """
        Generate metadata for all images in a directory.
        
        Args:
            image_dir: Directory containing images
            skip_existing: Skip images that already have JSON files
            
        Returns:
            List of generated JSON file paths
        """
        generated = []
        image_extensions = [".png", ".jpg", ".jpeg", ".webp"]
        
        for filename in os.listdir(image_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in image_extensions:
                continue
            
            image_path = os.path.join(image_dir, filename)
            json_path = image_path.rsplit(".", 1)[0] + ".json"
            
            if skip_existing and os.path.exists(json_path):
                print(f"[AIMetadataGenerator] Skipping (JSON exists): {filename}")
                continue
            
            result = self.generate_metadata_json(image_path)
            if result:
                generated.append(result)
        
        return generated


# CLI usage
if __name__ == "__main__":
    import sys
    
    generator = AIMetadataGenerator()
    
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            print(f"Processing directory: {path}")
            results = generator.batch_generate(path)
            print(f"\nGenerated {len(results)} JSON files")
        elif os.path.isfile(path):
            print(f"Processing image: {path}")
            result = generator.generate_metadata_json(path)
            if result:
                print(f"Generated: {result}")
        else:
            print(f"Path not found: {path}")
    else:
        print("Usage: python ai_metadata_generator.py <image_path_or_directory>")
        print("\nSet GOOGLE_API_KEY environment variable before running.")
