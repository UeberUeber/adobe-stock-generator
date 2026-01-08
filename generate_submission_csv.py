import os
import csv
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_csv(target_arg):
    # If target_arg is a timestamp, construct full path to 'upscaled'
    # If it's a full path, check if it ends with 'upscaled'
    
    if os.path.isabs(target_arg):
        target_dir = target_arg
        if not target_dir.endswith("upscaled") and os.path.exists(os.path.join(target_dir, "upscaled")):
            target_dir = os.path.join(target_dir, "upscaled")
    else:
        target_dir = os.path.join(BASE_DIR, "generations", target_arg, "upscaled")

    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return

    output_csv = os.path.join(target_dir, "submission.csv")
    
    # Get all images
    images = [f for f in os.listdir(target_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(images)} images in {target_dir}")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Filename', 'Title', 'Keywords', 'Category', 'Releases']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        success_count = 0
        for img_file in images:
            base_name = os.path.splitext(img_file)[0]
            # JSON might be in upscaled folder OR parent folder
            # Strategy: Look in upscaled first, then parent
            json_file = os.path.join(target_dir, f"{base_name}.json")
            parent_json = os.path.join(os.path.dirname(target_dir), f"{base_name}.json")
            
            meta = {}
            if os.path.exists(json_file):
                with open(json_file, 'r', encoding='utf-8') as jf: meta = json.load(jf)
            elif os.path.exists(parent_json):
                with open(parent_json, 'r', encoding='utf-8') as jf: meta = json.load(jf)
            
            if meta:
                try:
                    writer.writerow({
                        'Filename': img_file,
                        'Title': meta.get('title', ''),
                        'Keywords': ", ".join(meta.get('keywords', [])),
                        'Category': meta.get('category', 1),
                        'Releases': ''
                    })
                    success_count += 1
                except Exception as e:
                    print(f"Error writing row for {img_file}: {e}")
            else:
                print(f"Warning: No JSON found for {img_file}")
                writer.writerow({
                    'Filename': img_file,
                    'Title': 'Missing Metadata',
                    'Keywords': '',
                    'Category': 1,
                    'Releases': ''
                })

    print(f"Successfully created submission.csv with {success_count} entries.")
    print(f"Path: {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_csv(sys.argv[1])
    else:
        print("Usage: python generate_submission_csv.py <TIMESTAMP_OR_PATH>")
