"""
AI-Based Food Quality Inspection System
Flask API Server & Web Application
"""

import os
import sys
import io
import json
import base64
import time
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

from ai_engine.cv_inspector import CVFoodInspector
from ai_engine.gemini_inspector import GeminiFoodInspector
from ai_engine.food_standards import FOOD_STANDARDS

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max

# Initialize inspectors
cv_inspector = CVFoodInspector()

# Persistent history storage
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "inspection_history.json")
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history_record(record):
    history = load_history()
    # Don't save large base64 images in persistent json to keep it compact
    compact_record = {k: v for k, v in record.items() if k not in ["annotated_image", "heatmap_image", "laplacian_image", "luminance_image"]}
    history.insert(0, compact_record)
    # Keep last 100 entries
    history = history[:100]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# Mock user profiles for commercial kitchen roles
USER_PROFILES = {
    "auditor": {
        "id": "AUD-9042",
        "name": "Dr. Sarah Chen",
        "role": "auditor",
        "role_title": "Lead Food Safety Auditor (FDA / FSSAI Certified)",
        "kitchen": "Bistro Royale — Central Kitchen #3",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&auto=format&fit=crop&q=80"
    },
    "chef": {
        "id": "CHF-1085",
        "name": "Chef Marco Bellini",
        "role": "chef",
        "role_title": "Executive Head Chef & Plating Director",
        "kitchen": "Bistro Royale — Main Kitchen Line #1",
        "avatar": "https://images.unsplash.com/photo-1577219491135-ce391730fb2c?w=150&auto=format&fit=crop&q=80"
    },
    "manager": {
        "id": "MGR-3310",
        "name": "David Vance",
        "role": "manager",
        "role_title": "HACCP Hygiene & Operations Director",
        "kitchen": "Bistro Royale — Culinary Operations Floor",
        "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&auto=format&fit=crop&q=80"
    }
}

@app.route("/")
def index():
    return render_template("index.html", standards=FOOD_STANDARDS)

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    role = data.get("role", "chef")
    username = data.get("username", "")

    if role in USER_PROFILES:
        profile = USER_PROFILES[role]
    else:
        profile = {
            "id": f"USR-{int(time.time()%10000)}",
            "name": username if username else "Certified Food Inspector",
            "role": "inspector",
            "role_title": "Certified Culinary Quality Inspector",
            "kitchen": "Commercial Kitchen Line #1",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
        }
    return jsonify({"status": "success", "user": profile})

@app.route("/api/samples", methods=["GET"])
def get_samples():
    samples_dir = os.path.join(app.static_folder, "samples")
    if not os.path.exists(samples_dir):
        return jsonify([])

    sample_items = [
        # Prepared Restaurant Dishes
        {"id": "fresh_pizza", "name": "Artisan Pizza (Fresh)", "expected": "Ready to Serve", "file": "fresh_pizza.jpg", "category": "Prepared Dish", "hint": "pizza"},
        {"id": "burnt_pizza", "name": "Burnt Scorched Pizza", "expected": "Re-fire / Discard", "file": "burnt_pizza.jpg", "category": "Prepared Dish", "hint": "pizza"},
        {"id": "fresh_salad", "name": "Chef's Garden Salad (Crisp)", "expected": "Ready to Serve", "file": "fresh_salad.jpg", "category": "Cold Prep", "hint": "salad"},
        {"id": "wilted_salad", "name": "Wilted Oxidized Salad", "expected": "Discard Batch", "file": "wilted_salad.jpg", "category": "Cold Prep", "hint": "salad"},
        {"id": "crispy_chicken", "name": "Crispy Fried Chicken", "expected": "Ready to Serve", "file": "crispy_chicken.jpg", "category": "Hot Station", "hint": "fried_chicken"},
        {"id": "burnt_chicken", "name": "Over-Charred Chicken", "expected": "Re-fire Order", "file": "burnt_chicken.jpg", "category": "Hot Station", "hint": "fried_chicken"},
        {"id": "fresh_sushi", "name": "Salmon Nigiri (Fresh)", "expected": "Grade 1 Sashimi", "file": "fresh_sushi.jpg", "category": "Raw Seafood", "hint": "sushi_salmon"},
        {"id": "stale_sushi", "name": "Stale Oxidized Sushi", "expected": "Bio-Hazard Discard", "file": "stale_sushi.jpg", "category": "Raw Seafood", "hint": "sushi_salmon"},
        {"id": "fresh_steak", "name": "Char-Grilled Steak", "expected": "Prime Sear", "file": "fresh_steak.jpg", "category": "Grill Line", "hint": "steak"},
        # Kitchen Prep Commodities
        {"id": "fresh_apple", "name": "Fresh Apple (Prep)", "expected": "Garnish Ready", "file": "fresh_apple.jpg", "category": "Raw Produce", "hint": "apple"},
        {"id": "bruised_apple", "name": "Bruised Apple", "expected": "Trim for Sauce", "file": "bruised_apple.jpg", "category": "Raw Produce", "hint": "apple"},
        {"id": "fresh_banana", "name": "Fresh Banana (Bakery)", "expected": "Plating Ready", "file": "fresh_banana.jpg", "category": "Bakery Prep", "hint": "banana"},
        {"id": "spoiled_banana", "name": "Rotten Banana", "expected": "Discard Flesh", "file": "spoiled_banana.jpg", "category": "Bakery Prep", "hint": "banana"},
        {"id": "moldy_bread", "name": "Moldy Bread", "expected": "Discard Spores", "file": "moldy_bread.jpg", "category": "Bakery", "hint": "bread"}
    ]
    
    available = []
    for s in sample_items:
        path = os.path.join(samples_dir, s["file"])
        if os.path.exists(path):
            s["url"] = f"/static/samples/{s['file']}"
            available.append(s)
            
    return jsonify(available)

@app.route("/api/inspect", methods=["POST"])
def inspect_food():
    try:
        image_bytes = None
        filename = "inspection_image.jpg"
        food_hint = "auto"
        engine_type = "cv"
        api_key = ""

        # Handle JSON (Base64 webcam or payload)
        if request.is_json:
            data = request.get_json()
            food_hint = data.get("food_hint", "auto")
            engine_type = data.get("engine", "cv")
            api_key = data.get("api_key", "").strip()
            
            b64_str = data.get("image", "")
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            image_bytes = base64.b64decode(b64_str)
            filename = data.get("filename", "camera_snapshot.jpg")

        # Handle Multipart Form Upload
        elif "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            filename = secure_filename(file.filename)
            image_bytes = file.read()
            food_hint = request.form.get("food_hint", "auto")
            engine_type = request.form.get("engine", "cv")
            api_key = request.form.get("api_key", "").strip()

        if not image_bytes:
            return jsonify({"error": "No image data received"}), 400

        # Execute selected engine
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if engine_type == "gemini":
            try:
                gemini_inspector = GeminiFoodInspector(api_key=api_key if api_key else None)
                result = gemini_inspector.inspect_image(image_bytes, food_hint)
            except Exception as e:
                # Graceful fallback to CV if Gemini key invalid or fails
                result = cv_inspector.inspect_image(image_bytes, food_hint)
                result["fallback_notice"] = f"Gemini API note: {str(e)}. Fallback to CV Engine applied."
        else:
            result = cv_inspector.inspect_image(image_bytes, food_hint)

        result["id"] = f"INS-{int(time.time()*1000)}"
        result["filename"] = filename
        result["timestamp"] = timestamp

        # Save to persistent history
        save_history_record(result)

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/batch", methods=["POST"])
def batch_inspect():
    try:
        files = request.files.getlist("files")
        if not files:
            return jsonify({"error": "No files uploaded for batch inspection"}), 400

        food_hint = request.form.get("food_hint", "auto")
        results = []
        pass_count = 0
        total_freshness = 0.0

        for file in files:
            if file.filename:
                fname = secure_filename(file.filename)
                raw_bytes = file.read()
                try:
                    res = cv_inspector.inspect_image(raw_bytes, food_hint)
                    res["filename"] = fname
                    res["id"] = f"BATCH-{int(time.time()*1000)}"
                    res["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if res["pass_status"]:
                        pass_count += 1
                    total_freshness += res["freshness_score"]
                    results.append(res)
                    save_history_record(res)
                except Exception as ex:
                    results.append({
                        "filename": fname,
                        "error": str(ex),
                        "pass_status": False,
                        "grade": "Error"
                    })

        total = len(results)
        summary = {
            "total_inspected": total,
            "passed_count": pass_count,
            "failed_count": total - pass_count,
            "pass_rate_pct": round((pass_count / total) * 100, 1) if total > 0 else 0,
            "average_freshness": round(total_freshness / total, 1) if total > 0 else 0
        }

        return jsonify({"summary": summary, "items": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    records = load_history()
    total = len(records)
    passed = sum(1 for r in records if r.get("pass_status", False))
    
    # Grade breakdown
    grade_counts = {"Grade A": 0, "Grade B": 0, "Grade C": 0, "Rejected": 0}
    for r in records:
        g = r.get("grade", "Rejected")
        if g in grade_counts:
            grade_counts[g] += 1

    return jsonify({
        "records": records,
        "analytics": {
            "total_inspections": total,
            "passed_count": passed,
            "failed_count": total - passed,
            "pass_rate_pct": round((passed / total) * 100, 1) if total > 0 else 100.0,
            "grade_distribution": grade_counts
        }
    })

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    if os.path.exists(HISTORY_FILE):
        try:
            os.remove(HISTORY_FILE)
        except Exception:
            pass
    return jsonify({"status": "cleared"})

@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    import csv
    from io import StringIO
    from flask import Response
    
    records = load_history()
    si = StringIO()
    cw = csv.writer(si)
    
    # Headers
    cw.writerow([
        "Inspection ID", "Timestamp", "Culinary Dish / Commodity", "Commercial Grade", "Freshness/Doneness (%)",
        "Defect Coverage (%)", "Service Clearance", "Plating Appeal Score", "Caliber (mm)", "Volume (cm3)", "HACCP Safety Verdict"
    ])
    
    for r in records:
        metro = r.get("metrology", {})
        cw.writerow([
            r.get("id", ""),
            r.get("timestamp", ""),
            r.get("item_name", ""),
            r.get("grade", ""),
            r.get("freshness_score", ""),
            r.get("defect_percentage", ""),
            r.get("service_badge", "READY TO SERVE" if r.get("pass_status") else "RE-FIRE / DISCARD"),
            r.get("plating_appeal_score", 90.0),
            metro.get("estimated_diameter_mm", "N/A"),
            metro.get("estimated_volume_cm3", "N/A"),
            r.get("haccp_verdict", "N/A")
        ])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=nutriscan_quality_log.csv"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*60)
    print("   CHEFGUARD AI — RESTAURANT FOOD QUALITY INSPECTION SYSTEM")
    print(f"   Running at: http://127.0.0.1:{port}")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
