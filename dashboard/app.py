from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import csv
import shutil
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
GENERATIONS_ROOT = os.path.join(PARENT_DIR, "generations")

KNOWN_METADATA = [
    {"MatchStr": "neon_cyberpunk", "Title": "Futuristic Neon Cyberpunk Cityscape", "Keywords": "cyberpunk, neon, city, night, futuristic", "Category": "19"},
    {"MatchStr": "minimalist_zen", "Title": "Minimalist Zen Nature Landscape", "Keywords": "minimalist, zen, nature, calm, serene", "Category": "1"},
    {"MatchStr": "dynamic_action", "Title": "Dynamic Action Sports Moment", "Keywords": "sports, action, dynamic, motion, energy", "Category": "16"},
    {"MatchStr": "abstract_3d", "Title": "Abstract 3D Geometric Shapes", "Keywords": "abstract, 3d, geometric, shapes, pastel", "Category": "19"},
    {"MatchStr": "cozy_home_office", "Title": "Cozy Scandinavian Home Office", "Keywords": "home office, scandinavian, cozy, warm", "Category": "3"},
]

def get_metadata_for_file(filename):
    for item in KNOWN_METADATA:
        if item["MatchStr"] in filename:
            return item
    return {"Title": "Adobe Stock Image", "Keywords": "stock, image", "Category": "1"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/images')
def list_images():
    if not os.path.exists(GENERATIONS_ROOT):
        return jsonify([])
    
    image_list = []
    for root, dirs, files in os.walk(GENERATIONS_ROOT):
        for f in files:
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, f)
                rel_id = os.path.relpath(full_path, PARENT_DIR).replace('\\', '/')
                folder_name = os.path.basename(root)
                meta = get_metadata_for_file(f)
                image_list.append({
                    "id": rel_id,
                    "filename": f,
                    "folder": folder_name,
                    "title": meta["Title"],
                    "url": f"/images_serve/{rel_id}"
                })
    
    image_list.sort(key=lambda x: (x['folder'], x['filename']), reverse=True)
    return jsonify(image_list)

@app.route('/images_serve/<path:filepath>')
def serve_image(filepath):
    return send_from_directory(PARENT_DIR, filepath)

@app.route('/api/create_submission_package', methods=['POST'])
def create_submission_package():
    selected_ids = request.json.get('files', [])
    if not selected_ids:
        return jsonify({"success": False, "message": "No files selected"})
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    submission_folder = os.path.join(PARENT_DIR, "submissions", f"submission_{timestamp}")
    os.makedirs(submission_folder, exist_ok=True)
    
    successful = []
    for rel_path in selected_ids:
        if '..' in rel_path: continue
        src = os.path.join(PARENT_DIR, rel_path)
        if os.path.exists(src):
            shutil.copy2(src, submission_folder)
            successful.append(os.path.basename(src))
    
    csv_path = os.path.join(submission_folder, "submission.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Filename', 'Title', 'Keywords', 'Category'])
        writer.writeheader()
        for fn in successful:
            meta = get_metadata_for_file(fn)
            writer.writerow({"Filename": fn, "Title": meta["Title"], 
                           "Keywords": meta["Keywords"], "Category": meta["Category"]})
    
    os.startfile(submission_folder)
    return jsonify({"success": True, "message": f"Package created: {len(successful)} images"})

@app.route('/api/delete_images', methods=['POST'])
def delete_images():
    selected_ids = request.json.get('files', [])
    deleted = 0
    for rel_path in selected_ids:
        if '..' in rel_path: continue
        path = os.path.join(PARENT_DIR, rel_path)
        if os.path.exists(path):
            os.remove(path)
            deleted += 1
    return jsonify({"success": True, "message": f"Deleted {deleted} files"})

@app.route('/api/open_folder', methods=['POST'])
def open_folder():
    os.startfile(GENERATIONS_ROOT if os.path.exists(GENERATIONS_ROOT) else PARENT_DIR)
    return jsonify({"success": True})

if __name__ == '__main__':
    print("Dashboard: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
