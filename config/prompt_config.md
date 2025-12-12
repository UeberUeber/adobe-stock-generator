# Adobe Stock Prompt Configuration
# 이 파일을 수정하면 프롬프트 생성에 자동 반영됩니다.

---

## Base Style
```yaml
base_style: "Professional stock photo, commercial quality, 8k resolution"
quality_boosters:
  - "16:9 aspect ratio"
  - "ultra sharp focus"
  - "no blur"
  - "no noise"
  - "no artifacts"
  - "professional DSLR quality"
  - "crisp details"
  - "clean edges"
  - "studio lighting"
ip_safety:
  - "generic unbranded items"
  - "no visible logos or text"
  - "plain surfaces"
```

---

## Trends
```yaml
trends:
  FANTASTIC_FRONTIERS:
    name: "Fantastic Frontiers"
    prefix: "Surreal {subject}, dreamlike, floating elements"
  
  LEVITY_AND_LAUGHTER:
    name: "Levity and Laughter"
    prefix: "Humorous {subject}, candid laughter, authentic"
  
  TIME_WARP:
    name: "Time Warp"
    prefix: "Retrofuturistic {subject}, vintage meets sci-fi"
  
  IMMERSIVE_APPEAL:
    name: "Immersive Appeal"
    prefix: "Immersive {subject}, rich textures, tactile feel"
  
  NEON_SURREALISM:
    name: "Neo-Noir Cyberpunk"
    prefix: "Cyberpunk {subject}, neon lights, futuristic city"
  
  MINIMALIST_WELLNESS:
    name: "Minimalist Zen"
    prefix: "Zen {subject}, minimalist, calm, serene"
  
  AUTHENTIC_MOMENTS:
    name: "Dynamic Action"
    prefix: "Dynamic {subject}, action, motion blur, energy"
  
  WORKPLACE_EVOLUTION:
    name: "Cozy Home Office"
    prefix: "Cozy {subject}, home office, warm interior, generic laptop, plain monitor"
  
  GENERIC_BESTSELLER:
    name: "Generic BestSeller"
    prefix: "Professional {subject}"
```

---

## Subject Categories
```yaml
subjects:
  PEOPLE: "People"
  NATURE: "Nature"
  TECHNOLOGY: "Technology"
  BUSINESS: "Business"
  ABSTRACT: "Abstract"
  FOOD: "Food"
  SCIENCE_TECHNOLOGY: "Science & Tech"
  NATURE_OUTDOORS: "Nature & Outdoors"
  PEOPLE_LIFESTYLE: "People & Lifestyle"
  ABSTRACT_TEXTURES: "Abstract & Textures"
  BUSINESS_WORK: "Business & Work"
```

---

## Styles
```yaml
styles:
  PHOTOREALISTIC: "Photorealistic"
  RENDER_3D: "3D Render"
  MINIMALIST: "Minimalist"
  VECTOR_FLAT: "Vector/Flat Art"
  CINEMATIC: "Cinematic"
  FUTURISTIC: "Futuristic"
  REALISTIC_PHOTOGRAPHY: "Realistic Photography"
  DIGITAL_ART_3D: "3D Digital Art"
  SCANDINAVIAN: "Scandinavian Interior"
```

---

## Lighting
```yaml
lighting:
  NATURAL: "Natural Sunlight"
  STUDIO: "Studio Lighting"
  NEON: "Neon/Cyberpunk"
  GOLDEN_HOUR: "Golden Hour"
  NEON_CYBERPUNK: "Neon Cyberpunk"
  NATURAL_SOFT: "Natural Soft"
  DRAMATIC: "Dramatic High Contrast"
  STUDIO_LIGHTING: "Studio Lighting"
  WARM_GOLDEN_HOUR: "Warm Golden Hour"
```

---

## Composition
```yaml
composition:
  CENTERED: "Centered"
  RULE_OF_THIRDS: "Rule of Thirds"
  NEGATIVE_SPACE: "Negative Space"
  KNOLLING: "Knolling/Flat Lay"
  MACRO: "Macro/Close-up"
  SYMMETRICAL: "Symmetrical"
  MINIMALIST_NEGATIVE_SPACE: "Minimalist Negative Space"
  DYNAMIC_ANGLES: "Dynamic Angles"
  ABSTRACT_GEOMETRIC: "Abstract Geometric"
```

---

## Color Palette
```yaml
colors:
  VIBRANT: "Vibrant & Saturated"
  PASTEL: "Pastel & Soft"
  EARTH_TONES: "Earth Tones"
  MONOCHROMATIC: "Monochromatic"
  NEON_DARK: "Dark with Neon Accents"
  VIBRANT_NEON: "Vibrant Neon"
  BOLD_CONTRAST: "Bold Contrast"
  PASTEL_DREAM: "Pastel Dream"
  WARM_COZY: "Warm Cozy"
```

---

## Negative Prompts
```yaml
negative_prompts:
  # Brand/Logo Avoidance (Critical for IP compliance)
  brand_avoidance:
    - "no logos"
    - "no brand names"
    - "no trademarks"
    - "no company logos"
    - "no text"
    - "no letters"
    - "no words"
    - "no writing"
    - "no signage"
    - "no watermarks"
    - "no stamps"
    - "no emblems"
    - "no symbols"
  
  # Specific Brand Avoidance
  specific_brands:
    - "no apple logo"
    - "no macbook"
    - "no iphone"
    - "no ipad"
    - "no microsoft logo"
    - "no windows logo"
    - "no google logo"
    - "no samsung"
    - "no dell"
    - "no hp logo"
    - "no lenovo"
    - "no nike swoosh"
    - "no adidas"
    - "no coca cola"
    - "no starbucks"
  
  # Quality Issues
  quality:
    - "no deformed hands"
    - "no extra fingers"
    - "no missing fingers"
    - "no malformed limbs"
    - "no distorted faces"
    - "no asymmetric eyes"
    - "no blurry"
    - "no pixelated"
    - "no grainy"
    - "no noise"
    - "no artifacts"
    - "no glitches"
    - "no compression artifacts"
  
  # Legal/Editorial Issues
  legal:
    - "no celebrities"
    - "no famous people"
    - "no politicians"
    - "no copyrighted characters"
    - "no fictional characters"
    - "no flags"
    - "no currency"
    - "no government symbols"
  
  # Content Policy
  content_policy:
    - "no violence"
    - "no weapons"
    - "no drugs"
    - "no alcohol visible"
    - "no nudity"
    - "no suggestive content"
```
