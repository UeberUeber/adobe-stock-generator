import os
import sys

# === MONKEY PATCH FOR TORCHVISION 0.16+ ===
# Fixes 'No module named torchvision.transforms.functional_tensor' error in basicsr
# MUST BE APPLIED BEFORE IMPORTING REALESRGAN
try:
    from torchvision.transforms import functional_tensor
except ImportError:
    try:
        import torchvision.transforms.functional as F
        import types
        sys.modules["torchvision.transforms.functional_tensor"] = types.ModuleType("functional_tensor")
        sys.modules["torchvision.transforms.functional_tensor"].rgb_to_grayscale = F.rgb_to_grayscale
    except:
        pass
# ==========================================

import cv2
import time
import gc
import torch
from PIL import Image
from realesrgan import RealESRGANer
from models import RRDBNet

import datetime
import traceback
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATIONS_ROOT = os.path.join(BASE_DIR, "generations")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "upscale.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "error.log")
TARGET_ASPECT_RATIO = 16 / 9
TARGET_MIN_MP = 4

# === TILE SIZE CONFIGURATION ===
# 512: 빠름, VRAM 많이 사용 (8GB+ 필요)
# 384: 균형, VRAM 중간 (~6GB) - 권장
# 256: 느림 (~50% 증가), VRAM 적게 사용 (~4GB)
TILE_SIZE = 384

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
        
        # Force UTF-8 for stdout/stderr to prevent encoding errors in subprocess
        sys.stdout.reconfigure(encoding='utf-8')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.log(f"Initialized Pipeline for {self.timestamp} on device: {self.device}")
        self.log(f"Tile size: {TILE_SIZE} (lower = more stable, slower)")
        
    def log(self, message):
        """Write message to log file and stdout."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted, flush=True)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception as e:
            print(f"Error writing to log: {e}", flush=True)
        
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
            tile=TILE_SIZE,  # Configurable tile size for VRAM management
            tile_pad=10,
            pre_pad=0,
            half=False,    # FP32 for better quality (slower but reduces artifacts)
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
            # PNG for lossless quality (no JPEG compression artifacts)
            img.save(out_path, format='PNG')

    def log_error(self, message, exception=None):
        """Write error to error log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] ERROR: {message}"
        if exception:
            formatted += f"\n{traceback.format_exc()}"
        print(formatted)
        try:
            with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(formatted + "\n")
        except Exception as e:
            print(f"Error writing to error log: {e}")

    def process_all(self):
        self.log(f"Starting batch processing: {self.timestamp}")
        self.log(f"=== Memory Optimized Mode: 1 image at a time ===")
        start_total = time.time()
        
        raw_files = [f for f in os.listdir(self.run_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total = len(raw_files)
        
        if total == 0:
            self.log("No images to process")
            return
        
        count = 0
        failed = 0
        
        for idx, fname in enumerate(raw_files, 1):
            raw_path = os.path.join(self.run_dir, fname)
            # Processed files are now PNG
            processed_fname = fname.rsplit('.', 1)[0] + '.png'
            processed_path = os.path.join(self.processed_dir, processed_fname)
            upscaled_path = os.path.join(self.upscaled_dir, processed_fname)
            
            try:
                # 1. Crop (saves as PNG now)
                if not os.path.exists(processed_path):
                    self.crop_to_16_9(raw_path, processed_path)
                
                # 2. Upscale - Load model fresh for each image to prevent memory accumulation
                if not os.path.exists(upscaled_path):
                    self.log(f"  [{idx}/{total}] Upscaling {fname}...")
                    t0 = time.time()
                    
                    # Create upsampler for this image only
                    upsampler = self.get_upsampler()
                    
                    img = cv2.imread(processed_path, cv2.IMREAD_UNCHANGED)
                    if img is None:
                        raise ValueError(f"Failed to read image: {processed_path}")
                    
                    output, _ = upsampler.enhance(img, outscale=4)
                    cv2.imwrite(upscaled_path, output)
                    
                    # === AGGRESSIVE MEMORY CLEANUP ===
                    del img, output, upsampler
                    torch.cuda.empty_cache()
                    gc.collect()
                    # =================================
                    
                    dt = time.time() - t0
                    self.log(f"  [{idx}/{total}] Done: {fname} ({dt:.2f}s)")
                    count += 1
                    
                    # Copy JSON metadata file to upscaled folder if exists
                    json_fname = fname.rsplit('.', 1)[0] + '.json'
                    json_src = os.path.join(self.run_dir, json_fname)
                    json_dst = os.path.join(self.upscaled_dir, json_fname)
                    if os.path.exists(json_src) and not os.path.exists(json_dst):
                        shutil.copy2(json_src, json_dst)
                        self.log(f"  [{idx}/{total}] Copied JSON metadata: {json_fname}")
                else:
                    self.log(f"  [{idx}/{total}] Skipped (already exists): {fname}")
                    
            except Exception as e:
                failed += 1
                self.log_error(f"Failed to process {fname}", e)
                self.log(f"  [{idx}/{total}] FAILED: {fname} - {str(e)}")
                # Continue with next image
                torch.cuda.empty_cache()
                gc.collect()
        
        total_time = time.time() - start_total
        self.log(f"===== 완료! 성공: {count}/{total}, 실패: {failed} =====")
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
