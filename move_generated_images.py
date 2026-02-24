import shutil
import os
import glob
import sys
import json

# Configuration
SOURCE_DIR_DEFAULT = r"C:\Users\ueber\.gemini\antigravity\brain\b18b6f25-31f5-4c04-9a23-76d8bb464786"
# Parent of "generations"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def move_files(source_dir=None, target_arg=None):
    if not source_dir: source_dir = SOURCE_DIR_DEFAULT
    
    # If target_arg is a timestamp (e.g. 2026-...) construct full path
    # If it's a full path, use it.
    if target_arg:
        if os.path.isabs(target_arg):
            target_dir = target_arg
        else:
            target_dir = os.path.join(BASE_DIR, "generations", target_arg)
    else:
        print("Error: Target timestamp or directory is required.")
        return
    
    if not os.path.exists(target_dir):
        print(f"Target directory does not exist: {target_dir}")
        return

    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")

    # Scan target dir for JSON files to identify what we need to move
    # JSONs are created by process_seasonal_metadata.py beforehand
    expected_bases = []
    json_files = glob.glob(os.path.join(target_dir, "*.json"))
    for jf in json_files:
        base = os.path.splitext(os.path.basename(jf))[0]
        expected_bases.append(base)
    
    print(f"Identified {len(expected_bases)} expected images from metadata in target.")
    
    moved_count = 0
    
    for base in expected_bases:
        # The generate_image tool replaces special characters with underscores
        # We need to normalize our expected base to match the actual artifact filename
        # e.g. "2026-01-08-12..." -> "2026_01_08_12..."
        normalized_base = base.replace("-", "_").replace(":", "_")
        
        # Find the file in artifacts
        # We search for normalized_base*.png
        pattern = os.path.join(source_dir, f"{normalized_base}*.png")
        matches = glob.glob(pattern)
        
        if matches:
            # Take the most recent one 
            src_file = max(matches, key=os.path.getmtime)
            
            # Target filename: ensure it matches exactly what the JSON expects (base.png)
            dst_file = os.path.join(target_dir, f"{base}.png")
            
            try:
                # If src and dst are same, skip
                if os.path.abspath(src_file) == os.path.abspath(dst_file):
                    continue
                    
                shutil.copy2(src_file, dst_file)
                print(f"Copied: {os.path.basename(src_file)} -> {os.path.basename(dst_file)}")
                moved_count += 1
            except Exception as e:
                print(f"Error copying {base}: {e}")
        else:
            # Only warn if the PNG doesn't already exist in target
            if not os.path.exists(os.path.join(target_dir, f"{base}.png")):
                print(f"Warning: Source file not found for base: {base} (Checked pattern: {os.path.basename(pattern)})")
            
    print(f"\nSuccessfully moved {moved_count} images.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # First arg is target (timestamp or path)
        target = sys.argv[1]
        source = sys.argv[2] if len(sys.argv) > 2 else None
        move_files(source_dir=source, target_arg=target)
    else:
        print("Usage: python move_generated_images.py <TIMESTAMP_OR_PATH> [SOURCE_DIR]")
