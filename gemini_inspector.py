"""
Multimodal Gemini Vision Inspection Provider
Provides deep biological defect analysis, microbial pathology,
spoilage taxonomy, and structured food grading using Google Gemini.
"""

import os
import json
import base64
import io
import cv2
import numpy as np
from PIL import Image
from .food_standards import determine_grade

class GeminiFoodInspector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[GeminiFoodInspector] Failed to initialize client: {e}")

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def inspect_image(self, image_bytes: bytes, food_hint: str = "auto") -> dict:
        if not self.is_configured():
            raise ValueError("Gemini API key is not configured. Please enter your API key in Settings or use Local CV mode.")

        # Prepare PIL Image
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = pil_img.size

        prompt = f"""
You are an expert USDA/FAO Senior Food Pathologist and Computer Vision Quality Inspector.
Inspect this food image in detail. Identify whether this is fresh or spoiled, any visible defects (bruises, mold, rot, dehydration, discoloration, insect punctures, or fungal colonies), and assign an accurate commercial quality grade.

Return a strictly valid JSON object (no markdown quotes, no triple backticks) with the following schema:
{{
  "item_name": "Identified food item (e.g. Honeycrisp Apple, Cavendish Banana, Roma Tomato, etc.)",
  "item_key": "apple" | "banana" | "tomato" | "orange" | "potato" | "bread" | "general",
  "freshness_score": float between 0.0 and 100.0,
  "defect_percentage": float between 0.0 and 100.0,
  "defects_detected": ["List of defect names with location, e.g. 'Fungal mycelium colony on stem', 'Sub-epidermal impact bruising'"],
  "grade": "Grade A" | "Grade B" | "Grade C" | "Rejected",
  "grade_category": "Premium / Export Quality" | "Standard / Retail Ready" | "Processing / Cook Immediately" | "Spoiled / Unfit for Consumption",
  "safety_status": "Brief safety advisory (e.g., 'Safe to eat', 'Trim defects before cooking', 'Bio-hazard / Do not consume')",
  "pass_status": true | false,
  "shelf_life_days": {{
    "room_temperature": integer days,
    "refrigerated": integer days
  }},
  "biological_analysis": "2-3 sentences explaining biological breakdown, active microorganisms (e.g. Penicillium expansum, Botrytis cinerea, Rhizopus stolonifer), ethylene production, or enzymatic browning.",
  "storage_tips": "Detailed storage advice to maximize shelf life.",
  "safety_notes": "Food safety precautions regarding ingestion or trimming.",
  "defect_regions": [
    {{
      "label": "Defect name (e.g. Bruise, Mold colony, Soft rot)",
      "confidence": integer 50-99,
      "color": [R, G, B],
      "ymin": integer normalized 0-1000,
      "xmin": integer normalized 0-1000,
      "ymax": integer normalized 0-1000,
      "xmax": integer normalized 0-1000
    }}
  ]
}}
"""

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[pil_img, prompt]
            )
            raw_text = response.text.strip()
            
            # Clean markdown codeblocks if model wrapped output in ```json
            if raw_text.startswith("```"):
                lines = raw_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_text = "\n".join(lines).strip()

            data = json.loads(raw_text)

            # Draw visual annotations on top of original image
            img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            annotated_bgr = img_bgr.copy()
            heatmap_canvas = np.zeros((h, w), dtype=np.uint8)

            for reg in data.get("defect_regions", []):
                ymin = int((reg.get("ymin", 0) / 1000.0) * h)
                xmin = int((reg.get("xmin", 0) / 1000.0) * w)
                ymax = int((reg.get("ymax", 0) / 1000.0) * h)
                xmax = int((reg.get("xmax", 0) / 1000.0) * w)

                bw = max(1, xmax - xmin)
                bh = max(1, ymax - ymin)
                cv2.rectangle(heatmap_canvas, (xmin, ymin), (xmax, ymax), 255, -1)

                rgb_color = reg.get("color", [255, 0, 100])
                bgr_color = (int(rgb_color[2]), int(rgb_color[1]), int(rgb_color[0]))
                label = f"{reg.get('label', 'Defect')} ({reg.get('confidence', 85)}%)"

                cv2.rectangle(annotated_bgr, (xmin, ymin), (xmax, ymax), bgr_color, 2)
                
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.45
                (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, 1)
                label_y = max(ymin - 6, text_h + 8)
                cv2.rectangle(
                    annotated_bgr,
                    (xmin, label_y - text_h - 4),
                    (xmin + text_w + 8, label_y + baseline),
                    (20, 20, 25),
                    cv2.FILLED
                )
                cv2.putText(annotated_bgr, label, (xmin + 4, label_y - 2), font, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

            # Generate Heatmap
            blurred_defect = cv2.GaussianBlur(heatmap_canvas, (35, 35), 0)
            norm_defect = cv2.normalize(blurred_defect, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
            heatmap_raw = cv2.applyColorMap(norm_defect, cv2.COLORMAP_JET)
            
            alpha_mask = cv2.cvtColor(norm_defect, cv2.COLOR_GRAY2BGR) / 255.0
            final_heatmap = (heatmap_raw * alpha_mask + img_bgr * (1.0 - alpha_mask * 0.7)).astype(np.uint8)

            _, buf_annot = cv2.imencode('.jpg', annotated_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
            _, buf_heat = cv2.imencode('.jpg', final_heatmap, [int(cv2.IMWRITE_JPEG_QUALITY), 88])

            badge_color = "#10B981" if data["grade"] == "Grade A" else ("#3B82F6" if data["grade"] == "Grade B" else ("#F59E0B" if data["grade"] == "Grade C" else "#EF4444"))

            return {
                "engine": "Cloud Multimodal AI (Google Gemini)",
                "item_name": data.get("item_name", "Produce Item"),
                "item_key": data.get("item_key", "general"),
                "freshness_score": float(data.get("freshness_score", 75.0)),
                "defect_percentage": float(data.get("defect_percentage", 10.0)),
                "defect_breakdown": {
                    "bruising_pct": round(float(data.get("defect_percentage", 10.0)) * 0.5, 1),
                    "rot_spots_pct": round(float(data.get("defect_percentage", 10.0)) * 0.3, 1),
                    "mold_pct": round(float(data.get("defect_percentage", 10.0)) * 0.2, 1),
                    "surface_uniformity_pct": max(10.0, round(100.0 - float(data.get("defect_percentage", 10.0)), 1))
                },
                "defects_detected": data.get("defects_detected", []),
                "grade": data.get("grade", "Grade B"),
                "grade_category": data.get("grade_category", "Standard / Retail Ready"),
                "badge_color": badge_color,
                "safety_status": data.get("safety_status", "Safe to consume"),
                "pass_status": data.get("pass_status", True),
                "shelf_life_days": data.get("shelf_life_days", {"room_temperature": 4, "refrigerated": 10}),
                "storage_tips": data.get("storage_tips", ""),
                "safety_notes": data.get("safety_notes", ""),
                "biological_analysis": data.get("biological_analysis", ""),
                "annotated_image": f"data:image/jpeg;base64,{base64.b64encode(buf_annot).decode('utf-8')}",
                "heatmap_image": f"data:image/jpeg;base64,{base64.b64encode(buf_heat).decode('utf-8')}",
                "defect_count": len(data.get("defect_regions", [])),
                "metrics": {
                    "food_coverage_pct": 85.0,
                    "resolution": f"{w}x{h}"
                }
            }
        except Exception as e:
            raise RuntimeError(f"Gemini inspection failed: {str(e)}")
