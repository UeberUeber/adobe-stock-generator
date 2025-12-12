import os
import cv2
import sys
import time
import torch
from PIL import Image
from realesrgan import RealESRGANer
from models import RRDBNet

import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATIONS_ROOT = os.path.join(BASE_DIR, "generations")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "upscale.log")
TARGET_ASPECT_RATIO = 16 / 9
TARGET_MIN_MP = 4

class ImagePipeline:
    def __init__(self, run_timestamp):
        self.timestamp = run_timestamp
        self.run_dir = os.path.join(GENERATIONS_ROOT, self.timestamp)
        self.processed_dir = os.path.join(self.run_dir, "processed")
        self.upscaled_dir = os.path.join(self.run_dir, "upscaled")
        
        os.makedirs(self.run_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.upscaled_dir, exist_ok=True)
        
        # Ensure log directory exists
        os.makedirs(LOG_DIR, exist_ok=True)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.log(f"Initialized Pipeline for {self.timestamp} on device: {self.device}")
        
    def log(self, message):
        """Write message to log file and stdout."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception as e:
            print(f"Error writing to log: {e}")
        
    def get_upsampler(self):
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = os.path.join(WEIGHTS_DIR, "RealESRGAN_x4plus.pth")
        
        if not os.path.exists(model_path):
            os.makedirs(WEIGHTS_DIR, exist_ok=True)
            self.log("Downloading Real-ESRGAN model...")
            import urllib.request
            url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
            urllib.request.urlretrieve(url, model_path)
        
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=512,      # Tiling to prevent OOM
            tile_pad=10,
            pre_pad=0,
            half=True,     # FP16 for 2-3x speedup
            gpu_id=0 if torch.cuda.is_available() else None
        )
        return upsampler

    def crop_to_16_9(self, img_path, out_path):
        with Image.open(img_path) as img:
            width, height = img.size
            if width / height != TARGET_ASPECT_RATIO:
                # Simple center crop logic if needed, but assuming mostly square to landscape
                # For this task, we assume we just need to ensure aspect ratio
                current_ratio = width / height
                if current_ratio > TARGET_ASPECT_RATIO:
                    new_width = int(height * TARGET_ASPECT_RATIO)
                    offset = (width - new_width) // 2
                    crop_box = (offset, 0, offset + new_width, height)
                else:
                    new_height = int(width / TARGET_ASPECT_RATIO)
                    offset = (height - new_height) // 2
                    crop_box = (0, offset, width, offset + new_height)
                img = img.crop(crop_box)
            img.save(out_path, quality=95)

    def process_all(self):
        self.log(f"Starting batch processing: {self.timestamp}")
        start_total = time.time()
        
        upsampler = self.get_upsampler()
        
        raw_files = [f for f in os.listdir(self.run_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total = len(raw_files)
        
        if total == 0:
            self.log("No images to process")
            return
        
        count = 0
        for idx, fname in enumerate(raw_files, 1):
            raw_path = os.path.join(self.run_dir, fname)
            processed_path = os.path.join(self.processed_dir, fname)
            upscaled_path = os.path.join(self.upscaled_dir, fname.replace('.jpg', '.png').replace('.jpeg', '.png'))
            
            # 1. Crop
            if not os.path.exists(processed_path):
                self.crop_to_16_9(raw_path, processed_path)
            
            # 2. Upscale (Benchmarked)
            if not os.path.exists(upscaled_path):
                self.log(f"  [{idx}/{total}] Upscaling {fname}...")
                t0 = time.time()
                
                img = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
                output, _ = upsampler.enhance(img, outscale=4)
                cv2.imwrite(upscaled_path, output)
                
                # Memory cleanup to prevent leaks
                del img, output
                torch.cuda.empty_cache()
                
                dt = time.time() - t0
                self.log(f"  [{idx}/{total}] Done: {fname} ({dt:.2f}s)")
                count += 1
        
        total_time = time.time() - start_total
        self.log(f"===== 모두 완료! ({count}/{total}) =====")
        self.log(f"Total time: {total_time:.2f}s. Avg: {total_time/max(1, count):.2f}s/img")
        
        # Open the upscaled folder automatically
        try:
            os.startfile(self.upscaled_dir)
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ImagePipeline(sys.argv[1]).process_all()
    else:
        print("Usage: python generation_pipeline.py <TIMESTAMP>")
