# Adobe Stock Generator

AI-powered image generation pipeline for Adobe Stock submissions with drag-and-drop dashboard management.

## 🎯 Overview

This project automates the Adobe Stock image submission workflow:
1. **Generate Prompts** → Create optimized prompts for AI image generation
2. **Process Images** → Crop to 16:9 and upscale to 4K with Real-ESRGAN
3. **Review & Select** → Drag-and-drop dashboard for image curation
4. **Submit** → Generate Adobe Stock compliant CSV metadata

---

## 📁 Project Structure

```
adobe-stock-generator/
├── dashboard/
│   ├── app.py                  # Flask web dashboard & API
│   └── templates/
│       └── index.html          # Drag-and-drop dashboard UI
├── config/
│   ├── prompt_config.md        # 📝 Editable prompt configuration
│   └── adobe_stock_guidelines.md # 📚 Metadata best practices & rules
├── visual_schema.py            # Visual attribute enums
├── prompt_engine.py            # Prompt construction logic
├── generate_prompts.py         # Prompt generation script
├── generation_pipeline.py      # Image processing (crop + upscale)
├── metadata_generator.py       # Adobe Stock metadata generator
├── models.py                   # Real-ESRGAN model definitions
├── weights/                    # Model weights (auto-downloaded)
├── generations/                # Output folder (timestamped)
│   └── {timestamp}/
│       ├── *.png               # Raw generated images
│       ├── processed/          # 16:9 cropped images
│       └── upscaled/           # 4K upscaled images
├── submissions/                # Adobe Stock packages
│   └── submission_{timestamp}/
│       ├── *.png               # Final images
│       ├── submission.csv      # Metadata CSV
│       └── UPLOAD_INSTRUCTIONS.txt
├── trash/                      # Deleted images
├── logs/                       # Processing logs
└── start_dashboard.bat         # Windows launcher
```

---

## 🚀 Quick Start

### 1. Generate Prompts
```bash
python generate_prompts.py
```
Creates `generations/{timestamp}/` folder with prompts.

### 2. Add Images
Copy AI-generated images to the `generations/{timestamp}/` folder.

### 3. Launch Dashboard
```bash
start_dashboard.bat
# or
cd dashboard && python app.py
```
Opens http://127.0.0.1:5001

### 4. Dashboard Workflow

| Action | Method |
|--------|--------|
| **Select for Upscale** | Drag image → Right panel (Selection) |
| **Delete Image** | Drag image → Left panel (Trash) |
| **Upscale Selected** | Click "⚡ Upscale Selected" |
| **Create Submission** | Click "📦 CSV Submission 생성" |

---

## 🎨 Prompt Configuration

Edit `config/prompt_config.md` to customize prompts. Changes are reflected automatically.

### Configurable Elements:
- **Trends**: Cyberpunk, Minimalist Zen, Fantastic Frontiers, etc.
- **Styles**: Photorealistic, 3D Render, Cinematic, etc.
- **Lighting**: Natural, Neon, Golden Hour, etc.
- **Composition**: Rule of Thirds, Symmetrical, etc.
- **Color Palettes**: Vibrant Neon, Pastel, Earth Tones, etc.
- **Negative Prompts**: IP avoidance, quality control, content policy

---

## 📊 Core Modules

| Module | Purpose |
|--------|---------|
| `visual_schema.py` | Defines visual attributes (Trend, Style, Lighting, etc.) |
| `prompt_engine.py` | Constructs detailed prompts from attributes |
| `generate_prompts.py` | Generates sample prompts with MECE coverage |
| `generation_pipeline.py` | Image processing (16:9 crop → 4x upscale) |
| `metadata_generator.py` | Adobe Stock compliant metadata & CSV |
| `dashboard/app.py` | Flask API for image management |

---

## 🖼️ Image Processing Pipeline

```
Raw Image (any size)
    ↓
[Crop to 16:9] → generations/{ts}/processed/
    ↓
[Real-ESRGAN 4x] → generations/{ts}/upscaled/ (4K output)
    ↓
[Select & Submit] → submissions/submission_{ts}/
```

### Upscaling Settings:
- **Model**: RealESRGAN_x4plus
- **Scale**: 4x
- **Tiling**: 512px (prevents OOM)
- **FP16**: Enabled for 2-3x speedup

---

## 📋 Adobe Stock Compliance

### Automatic Metadata Generation:
- Clean titles (no banned words)
- 5-50 optimized keywords
- Category classification
- Release status

### Required Upload Checkboxes:
- ✅ "Created using generative AI tools"
- ✅ "People and Property are fictional"

### Banned Content (Auto-filtered):
- Brand names & logos
- Celebrity names
- Copyrighted characters
- AI-related terms in metadata

---

## 🛠️ Requirements

```
Python 3.10+
Flask
Pillow
OpenCV (cv2)
PyTorch
realesrgan
```

### Install:
```bash
pip install flask pillow opencv-python torch realesrgan
```

---

## 📝 Changelog

- **v1.0**: Initial release with prompt generation
- **v1.1**: Added Real-ESRGAN upscaling pipeline
- **v1.2**: Dashboard with drag-and-drop image management
- **v1.3**: Configurable prompts via MD file
- **v1.4**: 
  - 🔧 Fixed torchvision 0.16+ compatibility (monkey patch)
  - 🔧 Fixed memory leak during upscaling (`del` + `torch.cuda.empty_cache()`)
  - ✨ Upscale progress display: `[m/n]` format
  - ✨ "모두 완료!" completion message
  - ✨ Auto-open upscaled folder on completion
  - ✨ Log Clear button in dashboard
  - 🚀 Auto-generate submission package after upscale

