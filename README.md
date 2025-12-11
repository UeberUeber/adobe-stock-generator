# Adobe Stock Generator

AI-powered image generation pipeline for Adobe Stock submissions.

## Project Structure

```
adobe-stock-generator/
├── dashboard/
│   ├── app.py              # Flask web dashboard
│   └── templates/
│       └── index.html      # Dashboard UI
├── visual_schema.py        # Visual attribute enums (Trend, Style, etc.)
├── prompt_engine.py        # Prompt construction logic
├── generate_prompts.py     # Main generation script
├── generation_pipeline.py  # Image processing pipeline (crop, upscale)
├── start_dashboard.bat     # Windows launcher for dashboard
├── generations/            # Output folder (timestamped subfolders)
└── README.md
```

## Quick Start

### 1. Generate Prompts
```bash
python generate_prompts.py
```
Creates `generations/{timestamp}/` folder with metadata.

### 2. Process Images
```bash
python generation_pipeline.py {timestamp}
```
Crops to 16:9 and upscales 4x.

### 3. Review & Submit
```bash
start_dashboard.bat
```
Opens http://127.0.0.1:5000 for image review.

## Core Modules

| File | Purpose |
|------|---------|
| `visual_schema.py` | Defines visual attributes (Trend, Style, Lighting, etc.) |
| `prompt_engine.py` | Constructs detailed prompts from attributes |
| `generate_prompts.py` | Generates 5 MECE sample prompts |
| `generation_pipeline.py` | Processes raw images (crop → upscale) |
| `dashboard/app.py` | Flask API for image management |

## Requirements

- Python 3.10+
- Flask
- Pillow
