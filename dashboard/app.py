from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import sys
import csv
import json
import shutil
import threading
import subprocess
from datetime import datetime

# === MONKEY PATCH FOR TORCHVISION 0.16+ ===
# Fixes 'No module named torchvision.transforms.functional_tensor' error
try:
    from torchvision.transforms import functional_tensor
except ImportError:
    try:
        import torchvision.transforms.functional as F
        import types
        sys.modules["torchvision.transforms.functional_tensor"] = types.ModuleType("functional_tensor")
        sys.modules["torchvision.transforms.functional_tensor"].rgb_to_grayscale = F.rgb_to_grayscale
        print("Applied torchvision monkey patch")
    except:
        pass
# ==========================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
GENERATIONS_ROOT = os.path.join(PARENT_DIR, "generations")

# Add parent directory to path for imports
sys.path.insert(0, PARENT_DIR)

# Import MetadataGenerator
try:
    from metadata_generator import MetadataGenerator
    metadata_gen = MetadataGenerator()
    print("Successfully imported MetadataGenerator")
except ImportError as e:
    print(f"Error importing MetadataGenerator: {e}")
    metadata_gen = None

# Import ImagePipeline
try:
    from generation_pipeline import ImagePipeline
except (ImportError, OSError, Exception) as e:
    print(f"Warning: Could not import generation_pipeline: {e}")
    ImagePipeline = None

# Debug: Print paths on startup
print(f"=== PATH DEBUG ===")
print(f"BASE_DIR: {BASE_DIR}")
print(f"PARENT_DIR: {PARENT_DIR}")
print(f"GENERATIONS_ROOT: {GENERATIONS_ROOT}")
print(f"===================")

def get_metadata_for_file(filename, image_dir=None):
    """Generate Adobe Stock compliant metadata for a file.
    
    Args:
        filename: Image filename
        image_dir: Directory containing the image (for JSON lookup)
        
    Returns:
        dict with Title, Keywords, Category, is_generative_ai, is_fictional, has_json
    """
    # 1. Try to read JSON sidecar file first
    if image_dir:
        json_path = os.path.join(image_dir, filename.rsplit(".", 1)[0] + ".json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                return {
                    "Title": meta.get("title", "Stock Image"),
                    "Keywords": ", ".join(meta.get("keywords", [])),
                    "Category": str(meta.get("category", "1")),
                    "is_generative_ai": meta.get("is_ai_generated", True),
                    "is_fictional": meta.get("is_fictional", True),
                    "has_json": True,  # JSON found and loaded
                }
            except Exception as e:
                print(f"[WARNING] Failed to read JSON metadata: {e}")
    
    # 2. Fallback to metadata_generator (JSON not found!)
    print(f"[WARNING] No JSON metadata for {filename} - using filename inference")
    if metadata_gen:
        meta = metadata_gen.generate_from_filename(filename, image_dir)
        return {
            "Title": meta.get_clean_title(),
            "Keywords": meta.get_keywords_str(),
            "Category": meta.category.value,
            "is_generative_ai": meta.is_generative_ai,
            "is_fictional": meta.is_fictional,
            "has_json": False,  # No JSON - inferred from filename
        }
    else:
        # 3. Last fallback if import failed
        return {
            "Title": "Adobe Stock Image", 
            "Keywords": "stock, image, generic, professional, quality", 
            "Category": "1",
            "is_generative_ai": True,
            "is_fictional": True,
            "has_json": False,
        }

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
                
                # Pass image directory for JSON lookup (BUG FIX)
                image_dir = root
                meta = get_metadata_for_file(f, image_dir)
                image_list.append({
                    "id": rel_id,
                    "filename": f,
                    "folder": folder_name,
                    "title": meta["Title"],
                    "has_json": meta.get("has_json", False),
                    "url": f"/images_serve/{rel_id}"
                })
    
    image_list.sort(key=lambda x: (x['folder'], x['filename']), reverse=True)
    return jsonify(image_list)

@app.route('/images_serve/<path:filepath>')
def serve_image(filepath):
    return send_from_directory(PARENT_DIR, filepath)

# Job Queue for Upscale Tasks
# Format: {"timestamp": str, "status": "pending"|"running"|"completed"|"failed", "pid": int, ...}
UPSCALE_QUEUE = []
QUEUE_LOCK = threading.Lock()

# Dashboard log helper
LOG_DIR = os.path.join(PARENT_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "upscale.log")

def dashboard_log(message):
    """Write dashboard-level events to the upscale log."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [DASHBOARD] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"Error writing dashboard log: {e}")

def monitor_subprocess(timestamp, proc):
    """Monitor subprocess and update queue status when it completes."""
    try:
        # === IMPORTANT: Read stdout to prevent pipe buffer checking (Deadlock fix) ===
        # generation_pipeline.py already writes to upscale.log, so we don't need to write to file again.
        # But we must drain the pipe. We can optionally print to console for debugging.
        for line in iter(proc.stdout.readline, b''):
            line_str = line.decode('utf-8', errors='replace').strip()
            if line_str:
                # Optional: print to server console only, don't double-write to log file
                # print(f"[SUBPROCESS] {line_str}")
                pass
                
        proc.wait()  # Block until subprocess finishes
        exit_code = proc.returncode
        
        with QUEUE_LOCK:
            job = next((j for j in UPSCALE_QUEUE if j['timestamp'] == timestamp), None)
            if job:
                if exit_code == 0:
                    job['status'] = 'completed'
                    dashboard_log(f"✅ Upscale COMPLETED: {timestamp} (PID {proc.pid})")
                else:
                    job['status'] = 'failed'
                    job['error'] = f"Process exited with code {exit_code}"
                    dashboard_log(f"❌ Upscale FAILED: {timestamp} (exit code {exit_code})")
                job['completed_at'] = datetime.now().isoformat()
                
                # Auto-generate CSV in upscaled folder (simplified flow)
                if exit_code == 0:
                    try:
                        upscaled_dir = os.path.join(GENERATIONS_ROOT, timestamp, "upscaled")
                        if os.path.exists(upscaled_dir):
                            csv_path, count, missing_json = _create_csv_in_folder(upscaled_dir)
                            if missing_json:
                                print(f"[AUTO-CSV] ⚠️ WARNING: {len(missing_json)} images missing JSON metadata!")
                                for fn in missing_json:
                                    print(f"  - {fn}")
                            print(f"[AUTO-CSV] Created {csv_path} with {count} entries")
                            os.startfile(upscaled_dir)
                    except Exception as e:
                        print(f"[AUTO-CSV] Error: {e}")
                        
    except Exception as e:
        print(f"Error monitoring subprocess: {e}")
        with QUEUE_LOCK:
            job = next((j for j in UPSCALE_QUEUE if j['timestamp'] == timestamp), None)
            if job:
                job['status'] = 'failed'
                job['error'] = str(e)


@app.route('/api/upscale', methods=['POST'])
def upscale_images():
    data = request.json
    selected_ids = data.get('images', []) # list of rel paths
    
    timestamps = set()
    for rel_path in selected_ids:
        parts = rel_path.split('/')
        if 'generations' in parts:
            try:
                idx = parts.index('generations')
                ts = parts[idx+1]
                timestamps.add(ts)
            except:
                pass
    
    if not timestamps:
        return jsonify({'success': False, 'message': 'No valid timestamps found'})
    
    count = 0
    with QUEUE_LOCK:
        for ts in timestamps:
            # Check if already in queue
            if any(j['timestamp'] == ts for j in UPSCALE_QUEUE):
                continue
                
            print(f"[SUBPROCESS] Starting upscale for {ts}")
            dashboard_log(f"🚀 Starting upscale subprocess for batch: {ts}")
            
            # === SUBPROCESS ISOLATION ===
            # Run upscaling in a separate process so crashes don't kill the dashboard
            pipeline_script = os.path.join(PARENT_DIR, "generation_pipeline.py")
            proc = subprocess.Popen(
                [sys.executable, pipeline_script, ts],
                cwd=PARENT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            dashboard_log(f"📋 Subprocess started: PID {proc.pid}")
            
            UPSCALE_QUEUE.append({
                "timestamp": ts,
                "status": "running",
                "pid": proc.pid,
                "created_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat()
            })
            
            # Monitor subprocess in background thread
            monitor_thread = threading.Thread(target=monitor_subprocess, args=(ts, proc))
            monitor_thread.daemon = True
            monitor_thread.start()
            
            count += 1
        
    return jsonify({'success': True, 'message': f'Started {count} upscale processes (isolated)'})

@app.route('/api/queue', methods=['GET'])
def get_queue():
    with QUEUE_LOCK:
        return jsonify(UPSCALE_QUEUE)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    log_file = os.path.join(PARENT_DIR, "logs", "upscale.log")
    if not os.path.exists(log_file):
        return jsonify({"lines": []})
        
    try:
        # Read last 50 lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return jsonify({"lines": lines[-50:]})
    except Exception as e:
        return jsonify({"lines": [f"Error reading log: {str(e)}"]})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear the upscale log file."""
    log_file = os.path.join(PARENT_DIR, "logs", "upscale.log")
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Log cleared\n")
        return jsonify({"success": True, "message": "Logs cleared"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

def _create_csv_in_folder(folder_path):
    """Create submission.csv directly in the given folder.
    
    Args:
        folder_path: Directory containing images and JSON files
        
    Returns:
        (csv_path, count, missing_json_list)
    """
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    csv_path = os.path.join(folder_path, "submission.csv")
    missing_json = []
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Filename', 'Title', 'Keywords', 'Category', 'Releases']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for img in images:
            meta = get_metadata_for_file(img, folder_path)
            if not meta.get("has_json", False):
                missing_json.append(img)
            
            writer.writerow({
                "Filename": img,
                "Title": meta["Title"],
                "Keywords": meta["Keywords"],
                "Category": meta["Category"],
                "Releases": "",
            })
    
    return csv_path, len(images), missing_json

def _create_submission_package_internal(selected_ids):
    """Internal function to create submission package from relative file paths."""
    print(f"[DEBUG] Creating submission package for {len(selected_ids)} files")
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    submission_folder = os.path.join(PARENT_DIR, "submissions", f"submission_{timestamp}")
    os.makedirs(submission_folder, exist_ok=True)
    
    successful = []
    source_dirs = {}  # Map filename to source directory for JSON lookup
    for rel_path in selected_ids:
        if '..' in rel_path: continue
        # Normalize path separators
        rel_path = rel_path.replace('/', os.sep).replace('\\', os.sep)
        src = os.path.join(PARENT_DIR, rel_path)
        
        if os.path.exists(src):
            try:
                shutil.copy2(src, submission_folder)
                fn = os.path.basename(src)
                successful.append(fn)
                # Track source directory for JSON lookup
                source_dirs[fn] = os.path.dirname(src)
            except Exception as e:
                print(f"[ERROR] Failed to copy {src}: {e}")
    
    csv_path = os.path.join(submission_folder, "submission.csv")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        # Adobe Stock CSV format with all required fields
        fieldnames = ['Filename', 'Title', 'Keywords', 'Category', 'Releases']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fn in successful:
            # Pass source directory so JSON can be read
            image_dir = source_dirs.get(fn)
            meta = get_metadata_for_file(fn, image_dir)
            writer.writerow({
                "Filename": fn, 
                "Title": meta["Title"], 
                "Keywords": meta["Keywords"], 
                "Category": meta["Category"],
                "Releases": "",  # No release needed for fictional AI content
            })
    
    # Create a README with important upload instructions
    readme_path = os.path.join(submission_folder, "UPLOAD_INSTRUCTIONS.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("=== Adobe Stock Upload Instructions ===\n\n")
        f.write("IMPORTANT: When uploading these images, you MUST check the following boxes:\n\n")
        f.write("1. [x] 'Created using generative AI tools'\n")
        f.write("   - This is REQUIRED for all AI-generated images\n\n")
        f.write("2. [x] 'People and Property are fictional'\n")
        f.write("   - Check this if the image contains any people or properties\n\n")
        f.write("DO NOT include 'AI', 'Generative', or 'Artificial Intelligence' in titles/keywords.\n")
        f.write("The checkbox automatically labels your content as AI-generated.\n\n")
        f.write(f"Package contains {len(successful)} images.\n")
        
    return submission_folder, len(successful)

@app.route('/api/create_submission_package', methods=['POST'])
def create_submission_package():
    selected_ids = request.json.get('files', [])
    if not selected_ids:
        return jsonify({"success": False, "message": "No files selected"})
    
    folder, count = _create_submission_package_internal(selected_ids)
    os.startfile(folder)
    return jsonify({"success": True, "message": f"Package created: {count} images with Adobe Stock compliant metadata"})

@app.route('/api/delete_images', methods=['POST'])
def delete_images():
    selected_ids = request.json.get('files', [])
    deleted = 0
    errors = []
    
    print(f"[DELETE] Received request for {len(selected_ids)} files: {selected_ids}")
    
    # Ensure trash folder exists
    trash_folder = os.path.join(PARENT_DIR, "trash")
    os.makedirs(trash_folder, exist_ok=True)
    print(f"[DELETE] Trash folder: {trash_folder}")
    
    for rel_path in selected_ids:
        print(f"[DELETE] Processing: {rel_path}")
        if '..' in rel_path: 
            print(f"[DELETE] Skipping (contains ..): {rel_path}")
            continue
        
        # Normalize path separators for Windows
        rel_path_normalized = rel_path.replace('/', os.sep)
        safe_path = os.path.normpath(os.path.join(PARENT_DIR, rel_path_normalized))
        print(f"[DELETE] Safe path: {safe_path}")
        print(f"[DELETE] PARENT_DIR: {PARENT_DIR}")
        print(f"[DELETE] Path check: {os.path.normpath(PARENT_DIR)}")
        
        # Use normpath for both paths in comparison
        if not safe_path.startswith(os.path.normpath(PARENT_DIR)):
            print(f"[DELETE] Skipping (path check failed): {safe_path}")
            continue
        
        if os.path.exists(safe_path):
            try:
                # Move to trash instead of deleting
                filename = os.path.basename(safe_path)
                trash_path = os.path.join(trash_folder, filename)
                
                # Handle name collision by adding timestamp
                if os.path.exists(trash_path):
                    base, ext = os.path.splitext(filename)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    trash_path = os.path.join(trash_folder, f"{base}_{timestamp}{ext}")
                
                print(f"[DELETE] Moving {safe_path} -> {trash_path}")
                shutil.move(safe_path, trash_path)
                deleted += 1
                print(f"[DELETE] SUCCESS: Moved to trash")
            except Exception as e:
                print(f"[DELETE] ERROR: {e}")
                errors.append(str(e))
        else:
            print(f"[DELETE] File not found: {safe_path}")
    
    print(f"[DELETE] Complete: {deleted} files moved to trash")
    return jsonify({"success": True, "message": f"Moved {deleted} files to trash", "errors": errors})

@app.route('/api/open_folder', methods=['POST'])
def open_folder():
    path_to_open = GENERATIONS_ROOT if os.path.exists(GENERATIONS_ROOT) else PARENT_DIR
    print(f"[OPEN FOLDER] Opening: {path_to_open}")
    os.startfile(path_to_open)
    return jsonify({"success": True, "path": path_to_open})

if __name__ == '__main__':
    print("Dashboard: http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
