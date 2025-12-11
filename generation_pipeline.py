import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATIONS_ROOT = os.path.join(BASE_DIR, "generations")
TARGET_ASPECT_RATIO = 16 / 9
DEFAULT_UPSCALE_FACTOR = 4

class ImagePipeline:
    def __init__(self, run_timestamp):
        self.timestamp = run_timestamp
        self.run_dir = os.path.join(GENERATIONS_ROOT, self.timestamp)
        self.processed_dir = os.path.join(self.run_dir, "processed")
        self.upscaled_dir = os.path.join(self.run_dir, "upscaled")
        
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.upscaled_dir, exist_ok=True)

    def crop_to_16_9(self, img_path, out_path):
        with Image.open(img_path) as img:
            width, height = img.size
            current_ratio = width / height
            
            if current_ratio > TARGET_ASPECT_RATIO:
                new_width = int(height * TARGET_ASPECT_RATIO)
                offset = (width - new_width) // 2
                crop_box = (offset, 0, offset + new_width, height)
            else:
                new_height = int(width / TARGET_ASPECT_RATIO)
                offset = (height - new_height) // 2
                crop_box = (0, offset, width, offset + new_height)
            
            img.crop(crop_box).save(out_path)

    def upscale_image(self, img_path, out_path, factor=DEFAULT_UPSCALE_FACTOR):
        with Image.open(img_path) as img:
            width, height = img.size
            upscaled = img.resize((width * factor, height * factor), Image.Resampling.LANCZOS)
            upscaled.save(out_path, dpi=(300, 300))

    def process_all(self):
        print(f"Processing: {self.timestamp}")
        raw_files = [f for f in os.listdir(self.run_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for fname in raw_files:
            raw_path = os.path.join(self.run_dir, fname)
            processed_path = os.path.join(self.processed_dir, fname)
            upscaled_path = os.path.join(self.upscaled_dir, fname)
            
            if not os.path.exists(processed_path):
                print(f"  Cropping {fname}...")
                self.crop_to_16_9(raw_path, processed_path)
            
            if not os.path.exists(upscaled_path) and os.path.exists(processed_path):
                print(f"  Upscaling {fname}...")
                self.upscale_image(processed_path, upscaled_path)
        
        print("Done.")

def run_pipeline_for_timestamp(timestamp):
    ImagePipeline(timestamp).process_all()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_pipeline_for_timestamp(sys.argv[1])
    else:
        print("Usage: python generation_pipeline.py <TIMESTAMP>")
