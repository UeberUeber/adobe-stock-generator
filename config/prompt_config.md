# Adobe Stock Prompt Configuration
# 이 파일을 수정하면 프롬프트 생성에 자동 반영됩니다.

---

## 🎯 전략 프레임워크 (멱법칙 기반)

> 자세한 내용: `strategy_guide.md` 참조

### 포트폴리오 배분 (바벨 전략)
```yaml
portfolio_allocation:
  evergreen: 60%      # 에버그린 (안정적 기본 수요)
  seasonal: 30%       # 시즌성 (예측 가능한 피크)
  trending: 10%       # 트렌드 (고분산 베팅)
```

### 테마 분류
```yaml
evergreen_themes:
  - business_office      # 비즈니스, 사무실
  - lifestyle_wellness   # 라이프스타일, 건강
  - abstract_textures    # 배경, 텍스처, 패턴
  - education_learning   # 교육, 학습
  - medical_healthcare   # 의료, 웰빙
  - food_beverage       # 음식, 음료

seasonal_themes:
  - christmas_winter     # 크리스마스 (업로드: 9~10월)
  - valentines_love      # 발렌타인 (업로드: 12월)
  - easter_spring        # 부활절 (업로드: 1월)
  - summer_vacation      # 여름휴가 (업로드: 4월)
  - halloween_autumn     # 할로윈 (업로드: 8월)
  - thanksgiving         # 추수감사절 (업로드: 9월)
  - lunar_new_year       # 설날/춘절 (업로드: 11월)

trending_themes:
  # 현재 트렌드 (빠르게 변주, 고위험/고수익)
  - ai_technology        # AI/기술 비주얼
  - sustainable_eco      # 지속가능/친환경
  - remote_work          # 원격근무/재택
```

### 변주 생산 지침
```yaml
variation_rules:
  min_per_series: 10     # 시리즈당 최소 10장
  max_per_series: 50     # 시리즈당 최대 50장
  variation_axes:
    - color_palette      # 색상 변주
    - composition        # 구도 변주
    - copy_space         # 텍스트 공간 유무
    - aspect_ratio       # 비율 변주 (16:9, 1:1, 9:16)
```

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
