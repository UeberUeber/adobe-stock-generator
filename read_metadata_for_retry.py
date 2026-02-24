
import os
import json
import glob

target_dir = r"e:\codeWantigravity\AdobeStock_Automation Service\adobe-stock-generator\generations\2026-02-18_13-57-53"
json_files = glob.glob(os.path.join(target_dir, "*.json"))

for jf in json_files:
    with open(jf, "r", encoding="utf-8") as f:
        data = json.load(f)
        # We need the base filename without extension to pass to generate_image as ImageName?
        # generate_image takes ImageName.
        # The filename in JSON is like "somename.png".
        # ImageName should be "somename".
        filename = data["filename"]
        image_name = os.path.splitext(filename)[0]
        prompt = data["prompt"]
        print(f"IMAGE_NAME: {image_name}")
        print(f"PROMPT: {prompt}")
        print("-" * 20)
