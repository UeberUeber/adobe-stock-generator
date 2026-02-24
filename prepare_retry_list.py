
import json
import os
import re

def clean_filename(text):
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return clean.strip().replace(' ', '_').lower()

prompt_file = "seasonal_prompts.json"
timestamp = "2026-02-18_13-57-53"

with open(prompt_file, "r", encoding="utf-8") as f:
    prompts = json.load(f)

retry_list = []
for item in prompts:
    # Filter for IDs 78-89 if needed, but the file only has those.
    if 78 <= item['id'] <= 89:
        subject_desc = item.get('subject', '')
        short_desc = " ".join(subject_desc.split()[:5])
        filename_base = f"{clean_filename(short_desc)}_{timestamp}"
        retry_list.append({
            "name": filename_base,
            "prompt": item['prompt']
        })

print(json.dumps(retry_list, indent=2))
