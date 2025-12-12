---
description: Adobe Stock 이미지 생성 및 메타데이터 자동 생성 워크플로우
---

# Adobe Stock 이미지 생성 워크플로우

사용자가 이미지 생성을 요청하면 아래 단계를 **순서대로** 수행합니다.

---

## 1️⃣ prompt_config.md 읽기
```
view_file: config/prompt_config.md
```
- base_style, quality_boosters, ip_safety, negative_prompts 확인
- 해당 내용을 프롬프트에 반영

---

## 2️⃣ 프롬프트 구성
프롬프트 구조:
```
{prompt_config.base_style}, {사용자 요청 내용}, {quality_boosters}, {ip_safety}, {negative_prompts}
```

예시:
```
Professional stock photo, commercial quality, 8k resolution, 
Cozy Christmas living room with decorated tree and fireplace,
16:9 aspect ratio, ultra sharp focus, no blur, no noise,
generic unbranded items, no visible logos or text,
no logos, no brand names, no watermarks, no deformed hands
```

---

## 3️⃣ 이미지 생성
```
generate_image 도구 호출
```

---

## 4️⃣ 이미지 분석 (필수!)
```
view_file: 생성된 이미지 경로
```

**이미지를 직접 보고 분석하여 다음을 파악:**
- 주요 오브젝트 (object)
- 배경/장소 (setting)
- 분위기/감정 (mood)
- 색상 (color)
- 조명 (lighting)
- 구도 (composition)

---

## 5️⃣ JSON 메타데이터 생성

`adobe_stock_guidelines.md` 참조하여 작성:

### Adobe Stock 20개 카테고리 (필수 참조!)
| ID | 카테고리 | 설명 |
|----|---------|------|
| 1 | Animals | 동물, 애완동물, 야생동물 |
| 2 | Buildings and Architecture | 건물, 건축, 랜드마크, 인테리어 |
| 3 | Business | 비즈니스, 사무실, 기업, 금융 |
| 4 | Drinks | 음료, 커피, 칵테일, 와인 |
| 5 | The Environment | 환경, 생태, 지속가능성 |
| 6 | States of Mind | 감정, 기분, 심리 |
| 7 | Food | 음식, 요리, 식재료 |
| 8 | Graphic Resources | 그래픽, 패턴, 텍스처, 배경 |
| 9 | Hobbies and Leisure | 취미, 여가, 오락 |
| 10 | Industry | 산업, 공장, 제조 |
| 11 | Landscapes | 풍경, 자연, 산, 해변 |
| 12 | Lifestyle | 라이프스타일, 일상, 웰빙 |
| 13 | People | 사람, 초상화, 그룹 |
| 14 | Plants and Flowers | 식물, 꽃, 정원, 나무 |
| 15 | Culture and Religion | 문화, 종교, **축제, 크리스마스, 명절** |
| 16 | Science | 과학, 연구, 실험 |
| 17 | Social Issues | 사회문제, 커뮤니티 |
| 18 | Sports | 스포츠, 피트니스, 운동 |
| 19 | Technology | 기술, 컴퓨터, 디지털 |
| 20 | Transport | 교통, 차량, 비행기 |
| 21 | Travel | 여행, 관광, 휴가 |

> ⚠️ **크리스마스, 설날, 추수감사절 등 명절 이미지는 반드시 Category 15 (Culture and Religion) 사용!**

```json
{
  "filename": "{오브젝트}_{장소}_{분위기}.png",
  "title": "{이미지 내용을 설명하는 자연스러운 문장, 70자 이내}",
  "keywords": [
    "{가장 중요한 키워드}",
    "{두 번째 중요한 키워드}",
    ... 
    // 총 15-35개, 중요도 순
  ],
  "category": "{위 표에서 가장 적합한 ID 선택}",
  "category_name": "{카테고리 이름}",
  "asset_type": "photo" 또는 "illustration",
  "prompt": "{사용한 프롬프트}",
  "is_ai_generated": true,
  "is_fictional": true
}
```

### 제목 작성 규칙:
- ❌ "Professional", "Commercial" 등으로 시작 금지
- ✅ 이미지에 보이는 것을 자연스러운 문장으로 설명
- 예: "Cozy living room with Christmas tree and glowing fireplace"

### 키워드 작성 규칙:
- 첫 10개가 가장 중요 (검색 가중치 높음)
- 단수 명사 사용 (cats → cat)
- 제목의 핵심 단어를 상위 10개에 포함

---

## 6️⃣ 파일 저장

1. 새 폴더 생성: `generations/{YYYY-MM-DD_HH-MM-SS}/`
2. 이미지 복사: `{filename}.png`
3. JSON 저장: `{filename}.json`

```powershell
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$destDir = "generations/$timestamp"
New-Item -ItemType Directory -Force -Path $destDir
Copy-Item "{원본 이미지}" -Destination "$destDir/{filename}.png"
# JSON 파일은 write_to_file로 생성
```

---

## 7️⃣ 완료 보고

사용자에게 다음 정보 제공:
- 생성된 이미지 개수
- 저장 위치
- 대시보드 링크: http://127.0.0.1:5001

---

## 참고 파일

| 파일 | 용도 |
|------|------|
| `config/prompt_config.md` | 프롬프트 구성 요소 |
| `config/adobe_stock_guidelines.md` | 메타데이터 작성 가이드라인 |
