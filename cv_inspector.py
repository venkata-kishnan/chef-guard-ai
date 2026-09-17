"""
Advanced Multi-Spectral Computer Vision & Metrology Engine for Food Quality Inspection
Computes morphometric sizing (mm, cm2, cm3, circularity), multi-spectral overlays
(Thermal Jet, Laplacian Texture Gradient, CIELAB Luminance), and biochemical degradation.
"""

import cv2
import numpy as np
import base64
import time
from .food_standards import FOOD_STANDARDS, determine_grade_and_nutritional_status

class CVFoodInspector:
    def __init__(self, mm_per_pixel: float = 0.25):
        # Default working distance scale: 0.25 mm per pixel
        self.mm_per_pixel = mm_per_pixel

    def inspect_image(self, image_bytes: bytes, food_hint: str = "auto") -> dict:
        """
        Main multi-spectral inspection pipeline.
        Returns comprehensive metrology, defect segmentation, multi-spectral images,
        and nutritional degradation profiles.
        """
        start_time = time.perf_counter()

        # 1. Decode image into OpenCV BGR format
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Failed to decode image. Please provide a valid JPG/PNG file.")

        # Resize for consistent inspection resolution if overly large
        h, w = img_bgr.shape[:2]
        max_dim = 900
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
            h, w = img_bgr.shape[:2]

        # 2. Segment Food Object from Background
        food_mask, food_contour = self._segment_food_object(img_bgr)
        food_area = cv2.countNonZero(food_mask)
        total_pixels = h * w
        
        # Fallback if food_area is too small
        if food_area < (total_pixels * 0.04):
            food_mask = np.ones((h, w), dtype=np.uint8) * 255
            food_area = total_pixels
            food_contour = None

        # 3. Detect / Confirm Food Category
        detected_food = self._classify_food_item(img_bgr, food_mask, food_hint)

        # 4. Computer Vision Metrology & Sizing
        metrology = self._compute_metrology(food_contour, food_area, h, w)

        # 5. Extract Multi-Spectral Defects (Rot, Mold, Bruises)
        defects_info = self._detect_defects(img_bgr, food_mask, detected_food)

        # 6. Defect Metrics & Freshness Scoring
        defect_mask = defects_info["combined_defect_mask"]
        defect_pixels = cv2.countNonZero(defect_mask)
        defect_pct = min(100.0, round((defect_pixels / float(food_area)) * 100.0, 2))

        freshness_score = self._calculate_freshness_score(
            defect_pct=defect_pct,
            color_uniformity=float(defects_info["color_uniformity"]),
            texture_roughness=float(defects_info["texture_roughness"]),
            mold_pct=float(defects_info["mold_pct"]),
            rot_pct=float(defects_info["rot_pct"]),
            food_type=detected_food
        )

        # 7. Generate Multi-Spectral Visualizations (HUD, Heatmap, Laplacian, Luminance)
        visuals = self._generate_multispectral_visuals(
            img_bgr, food_mask, defect_mask, defects_info, metrology, freshness_score, detected_food
        )

        # 8. Grade, Nutritional Degradation, and HACCP Clearance
        grade_info = determine_grade_and_nutritional_status(
            freshness_score, defect_pct, detected_food, metrology["estimated_diameter_mm"]
        )

        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 1)

        return {
            "engine": "Local Multi-Spectral Computer Vision (OpenCV)",
            "item_name": FOOD_STANDARDS.get(detected_food, FOOD_STANDARDS["general"])["name"],
            "item_key": detected_food,
            "freshness_score": float(freshness_score),
            "defect_percentage": float(defect_pct),
            "defect_breakdown": {
                "bruising_pct": float(defects_info["bruise_pct"]),
                "rot_spots_pct": float(defects_info["rot_pct"]),
                "mold_pct": float(defects_info["mold_pct"]),
                "surface_uniformity_pct": float(round(float(defects_info["color_uniformity"]) * 100.0, 1))
            },
            "defects_detected": defects_info["detected_defect_labels"],
            "defect_count": int(len(defects_info["defect_regions"])),
            "grade": grade_info["grade"],
            "grade_category": grade_info["grade_category"],
            "badge_color": grade_info["badge_color"],
            "service_badge": grade_info.get("service_badge", "READY TO SERVE"),
            "service_status": grade_info.get("service_status", grade_info["safety_status"]),
            "safety_status": grade_info["safety_status"],
            "pass_status": grade_info["pass_status"],
            "haccp_verdict": grade_info["haccp_verdict"],
            "haccp_standard": grade_info.get("haccp_standard", "Standard kitchen hygiene."),
            "plating_appeal_score": grade_info.get("plating_appeal_score", 90.0),
            "remaining_service_hours": grade_info.get("remaining_service_hours", 2.0),
            "optimal_service_temp": grade_info.get("optimal_service_temp", "65°C"),
            "kitchen_action": grade_info.get("kitchen_action", "Proceed with table service."),
            "size_class": grade_info.get("size_class", "Commercial Portion"),
            "shelf_life_days": grade_info.get("shelf_life_days", {"room_temperature": 1, "refrigerated": 3}),
            "nutritional_status": grade_info.get("nutritional_status", {}),
            "metrology": metrology,
            "storage_tips": grade_info.get("kitchen_action", "Store in clean warm holding."),
            "safety_notes": grade_info.get("safety_notes", "Maintain HACCP temp."),
            # Multi-spectral visual outputs
            "annotated_image": f"data:image/jpeg;base64,{visuals['annotated_b64']}",
            "heatmap_image": f"data:image/jpeg;base64,{visuals['heatmap_b64']}",
            "laplacian_image": f"data:image/jpeg;base64,{visuals['laplacian_b64']}",
            "luminance_image": f"data:image/jpeg;base64,{visuals['luminance_b64']}",
            "metrics": {
                "food_coverage_pct": float(round((food_area / float(total_pixels)) * 100.0, 1)),
                "resolution": f"{w}x{h}",
                "inference_time_ms": latency_ms
            }
        }

    def _compute_metrology(self, contour, area_px, h, w):
        """
        Computer Vision Metrology & Geometric Caliber Analysis:
        Computes physical diameter, surface area, volume, circularity, and solidity.
        """
        scale = self.mm_per_pixel

        if contour is not None and len(contour) >= 5:
            # Perimeter
            perimeter = cv2.arcLength(contour, True)
            
            # Circularity Index: 4*pi*Area / P^2 (1.0 = circle)
            circularity = (4 * np.pi * area_px) / float(perimeter ** 2) if perimeter > 0 else 0.0
            circularity = max(0.1, min(1.0, circularity))

            # Convex Hull and Solidity
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            solidity = float(area_px / hull_area) if hull_area > 0 else 1.0

            # Minimum enclosing circle
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            diameter_mm = radius * 2 * scale

            # Ellipse fit for 3D volume estimation
            try:
                ellipse = cv2.fitEllipse(contour)
                (e_x, e_y), (e_w, e_h), angle = ellipse
                major_axis_cm = (max(e_w, e_h) * scale) / 10.0
                minor_axis_cm = (min(e_w, e_h) * scale) / 10.0
                # Prolate spheroid volume: 4/3 * pi * a * b^2
                volume_cm3 = (4.0 / 3.0) * np.pi * (major_axis_cm / 2.0) * ((minor_axis_cm / 2.0) ** 2)
            except Exception:
                major_axis_cm = diameter_mm / 10.0
                minor_axis_cm = diameter_mm / 10.0
                volume_cm3 = (4.0 / 3.0) * np.pi * ((major_axis_cm / 2.0) ** 3)

        else:
            # Approximation from equivalent area circle
            equiv_radius = np.sqrt(area_px / np.pi)
            diameter_mm = equiv_radius * 2 * scale
            circularity = 0.85
            solidity = 0.95
            radius_cm = (diameter_mm / 2.0) / 10.0
            volume_cm3 = (4.0 / 3.0) * np.pi * (radius_cm ** 3)

        # Projected Surface Area in cm2
        surface_area_cm2 = (area_px * (scale ** 2)) / 100.0

        # Form / Deformity classification
        if solidity < 0.85:
            form_status = "Deformed / Indented Contour"
        elif circularity > 0.80:
            form_status = "Uniform Symmetrical"
        else:
            form_status = "Elongated Natural"

        return {
            "estimated_diameter_mm": round(float(diameter_mm), 1),
            "projected_area_cm2": round(float(surface_area_cm2), 1),
            "estimated_volume_cm3": round(float(volume_cm3), 1),
            "circularity_index": round(float(circularity), 2),
            "solidity_index": round(float(solidity), 2),
            "form_status": form_status
        }

    def _segment_food_object(self, img_bgr):
        h, w = img_bgr.shape[:2]
        
        # Sample the 4 corners to establish background reference
        c_size = max(8, min(24, int(min(h, w) * 0.05)))
        corners = [
            img_bgr[:c_size, :c_size],
            img_bgr[:c_size, -c_size:],
            img_bgr[-c_size:, :c_size],
            img_bgr[-c_size:, -c_size:]
        ]
        bg_color = np.median(np.concatenate([c.reshape(-1, 3) for c in corners], axis=0), axis=0)

        # Euclidean distance in BGR
        diff = np.sqrt(np.sum((img_bgr.astype(np.float32) - bg_color.astype(np.float32)) ** 2, axis=2))
        _, fg_mask = cv2.threshold(diff.astype(np.uint8), 22, 255, cv2.THRESH_BINARY)

        # Chromatic saturation threshold
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        sat = hsv[:, :, 1]
        _, sat_mask = cv2.threshold(sat, 25, 255, cv2.THRESH_BINARY)
        
        combined = cv2.bitwise_or(fg_mask, sat_mask)

        # Morphological closing
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        cleaned = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=3)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return np.ones((h, w), dtype=np.uint8) * 255, None

        largest_c = max(contours, key=cv2.contourArea)
        food_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(food_mask, [largest_c], -1, 255, thickness=cv2.FILLED)

        if cv2.countNonZero(food_mask) < (h * w * 0.03):
            food_mask = np.ones((h, w), dtype=np.uint8) * 255
            largest_c = None

        return food_mask, largest_c

    def _classify_food_item(self, img_bgr, food_mask, food_hint):
        if food_hint in FOOD_STANDARDS and food_hint != "auto":
            return food_hint

        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        h_channel = hsv[:, :, 0]
        s_channel = hsv[:, :, 1]
        v_channel = hsv[:, :, 2]

        food_pixels_h = h_channel[food_mask > 0]
        food_pixels_s = s_channel[food_mask > 0]
        food_pixels_v = v_channel[food_mask > 0]

        if len(food_pixels_h) == 0:
            return "general"

        median_h = float(np.median(food_pixels_h))
        median_s = float(np.median(food_pixels_s))
        median_v = float(np.median(food_pixels_v))

        if (median_h < 12 or median_h > 165) and median_s > 60:
            return "apple" if median_v > 80 else "tomato"
        elif 12 <= median_h < 25 and median_s > 70:
            return "orange"
        elif 25 <= median_h < 38 and median_s > 60:
            return "banana"
        elif 10 <= median_h < 30 and median_s <= 90 and median_v > 100:
            return "potato"
        elif median_s < 70 and median_v > 110:
            return "bread"
        
        return "general"

    def _detect_defects(self, img_bgr, food_mask, detected_food):
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        h, w = img_bgr.shape[:2]

        l_chan = lab[:, :, 0]
        h_chan = hsv[:, :, 0]
        s_chan = hsv[:, :, 1]
        v_chan = hsv[:, :, 2]

        # Inner food mask: erode perimeter to avoid anti-aliased edge artifacts
        kernel_edge = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        inner_food_mask = cv2.erode(food_mask, kernel_edge, iterations=1)
        if cv2.countNonZero(inner_food_mask) < 100:
            inner_food_mask = food_mask

        food_pixels_l = l_chan[inner_food_mask > 0]
        mean_l = np.mean(food_pixels_l) if len(food_pixels_l) > 0 else 128
        std_l = np.std(food_pixels_l) if len(food_pixels_l) > 0 else 20

        # --- A. Dark Rot / Necrotic Spots ---
        # True necrotic rot is dark AND desaturated/brownish, unlike vibrant fruit blush
        rot_thresh = max(15, int(mean_l - 1.75 * std_l))
        is_dark_l = l_chan < rot_thresh
        is_not_vibrant_blush = (s_chan < 130) | (l_chan < 55)
        dark_mask = is_dark_l & is_not_vibrant_blush & (inner_food_mask > 0)
        
        if detected_food == "banana":
            green_tips = (h_chan >= 35) & (h_chan <= 85) & (inner_food_mask > 0)
            dark_mask = dark_mask & (~green_tips)

        dark_mask = np.uint8(dark_mask * 255)
        kernel_rot = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_rot)

        # --- B. Fungal Mold / Spore Colonies ---
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_abs = np.uint8(np.clip(np.absolute(laplacian), 0, 255))
        
        # Pale/grayish mold (Botrytis, Rhizopus)
        pale_mold = ((lap_abs > 18) | (s_chan < 55)) & (s_chan < 85) & (v_chan > 105) & (inner_food_mask > 0)
        if detected_food == "sushi_salmon":
            # Natural intramuscular fat striations in salmon sashimi are not mold
            is_fat_stripe = (v_chan > 165) & (s_chan < 75)
            pale_mold = pale_mold & (~is_fat_stripe)

        # Blue-green mold (Penicillium)
        green_mold = (h_chan >= 50) & (h_chan <= 115) & (s_chan > 25) & (s_chan < 170) & (inner_food_mask > 0)
        if detected_food == "strawberry":
            # Exclude healthy green calyx sepals from being classified as mold
            is_calyx = (h_chan >= 35) & (h_chan <= 85) & (s_chan > 50)
            green_mold = green_mold & (~is_calyx)

        if detected_food in ["bread", "tomato", "apple", "orange", "strawberry"]:
            mold_candidate = (pale_mold | green_mold)
        else:
            mold_candidate = pale_mold

        mold_mask = np.uint8(mold_candidate * 255)
        kernel_mold = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mold_mask = cv2.morphologyEx(mold_mask, cv2.MORPH_OPEN, kernel_mold)
        mold_mask = cv2.morphologyEx(mold_mask, cv2.MORPH_CLOSE, kernel_mold)

        # --- C. Bruise / Softening ---
        bruise_thresh = int(mean_l - 0.9 * std_l)
        bruise_candidate = (l_chan < bruise_thresh) & (l_chan >= rot_thresh) & is_not_vibrant_blush & (inner_food_mask > 0)
        bruise_mask = np.uint8(bruise_candidate * 255)
        kernel_bruise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        bruise_mask = cv2.morphologyEx(bruise_mask, cv2.MORPH_OPEN, kernel_bruise)
        bruise_mask = cv2.bitwise_and(bruise_mask, cv2.bitwise_not(mold_mask))

        dark_mask = cv2.bitwise_and(dark_mask, food_mask)
        mold_mask = cv2.bitwise_and(mold_mask, food_mask)
        bruise_mask = cv2.bitwise_and(bruise_mask, food_mask)

        combined_defect = cv2.bitwise_or(dark_mask, cv2.bitwise_or(mold_mask, bruise_mask))

        food_area = float(max(1, cv2.countNonZero(food_mask)))
        rot_pct = round((cv2.countNonZero(dark_mask) / food_area) * 100.0, 2)
        mold_pct = round((cv2.countNonZero(mold_mask) / food_area) * 100.0, 2)
        bruise_pct = round((cv2.countNonZero(bruise_mask) / food_area) * 100.0, 2)

        contours, _ = cv2.findContours(combined_defect, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        defect_regions = []
        labels_found = set()

        min_region_area = max(25, int(food_area * 0.0015))
        for c in contours:
            area = cv2.contourArea(c)
            if area >= min_region_area:
                x, y, bw, bh = cv2.boundingRect(c)
                region_roi_dark = dark_mask[y:y+bh, x:x+bw]
                region_roi_mold = mold_mask[y:y+bh, x:x+bw]

                dark_score = cv2.countNonZero(region_roi_dark)
                mold_score = cv2.countNonZero(region_roi_mold)

                if mold_score > dark_score and mold_score > (area * 0.3):
                    label = "Fungal Mold / Spores"
                    color = (255, 0, 200) # pinkish
                elif dark_score > (area * 0.35):
                    label = "Necrosis / Rot Lesion"
                    color = (0, 0, 255) # red
                else:
                    label = "Impact Bruise / Blemish"
                    color = (0, 165, 255) # orange

                labels_found.add(label)
                confidence = min(99, int(72 + (area / food_area) * 200))
                defect_regions.append({
                    "bbox": [int(x), int(y), int(bw), int(bh)],
                    "label": label,
                    "color": color,
                    "area": int(area),
                    "confidence": confidence
                })

        texture_roughness = float(np.mean(lap_abs[food_mask > 0])) if food_area > 0 else 0.0
        color_uniformity = max(0.1, min(1.0, 1.0 - (std_l / 128.0)))

        return {
            "combined_defect_mask": combined_defect,
            "dark_mask": dark_mask,
            "mold_mask": mold_mask,
            "bruise_mask": bruise_mask,
            "rot_pct": rot_pct,
            "mold_pct": mold_pct,
            "bruise_pct": bruise_pct,
            "color_uniformity": round(float(color_uniformity), 2),
            "texture_roughness": round(float(texture_roughness), 2),
            "defect_regions": defect_regions,
            "detected_defect_labels": list(labels_found) if labels_found else ["No major surface defects"],
            "lap_abs": lap_abs,
            "l_chan": l_chan
        }

    def _calculate_freshness_score(self, defect_pct, color_uniformity, texture_roughness, mold_pct=0.0, rot_pct=0.0, food_type="general"):
        base_score = 100.0
        defect_penalty = defect_pct * 2.2
        mold_penalty = min(35.0, mold_pct * 8.0) if mold_pct > 0.3 else 0.0
        rot_penalty = min(25.0, rot_pct * 4.0) if rot_pct > 1.0 else 0.0
        
        # Seeded fruits (like strawberries) naturally have higher surface texture roughness
        base_roughness = 30.0 if food_type == "strawberry" else 18.0
        roughness_penalty = max(0.0, (texture_roughness - base_roughness) * 0.7)
        uniformity_penalty = max(0.0, (1.0 - color_uniformity) * 20.0)

        raw_score = base_score - defect_penalty - mold_penalty - rot_penalty - roughness_penalty - uniformity_penalty
        score = max(5.0, min(99.0, raw_score))
        return round(float(score), 1)

    def _generate_multispectral_visuals(self, img_bgr, food_mask, defect_mask, defects_info, metrology, freshness_score, food_type):
        h, w = img_bgr.shape[:2]

        # 1. Annotated HUD Image
        annotated = img_bgr.copy()
        food_contours, _ = cv2.findContours(food_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(annotated, food_contours, -1, (255, 230, 0), 2)

        # HUD corner brackets and labels
        for reg in defects_info["defect_regions"]:
            x, y, bw, bh = reg["bbox"]
            color = reg["color"]
            label = f"{reg['label']} ({reg['confidence']}%)"

            cv2.rectangle(annotated, (x, y), (x + bw, y + bh), color, 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            (text_w, text_h), baseline = cv2.getTextSize(label, font, 0.42, 1)
            label_y = max(y - 6, text_h + 8)
            cv2.rectangle(annotated, (x, label_y - text_h - 4), (x + text_w + 8, label_y + baseline), (20, 20, 25), cv2.FILLED)
            cv2.rectangle(annotated, (x, label_y - text_h - 4), (x + text_w + 8, label_y + baseline), color, 1)
            cv2.putText(annotated, label, (x + 4, label_y - 2), font, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # Caliber sizing watermark on top left
        caliber_text = f"CALIBER: {metrology['estimated_diameter_mm']}mm | {metrology['form_status']}"
        cv2.putText(annotated, caliber_text, (16, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 220), 1, cv2.LINE_AA)

        # 2. Thermal Jet Heatmap
        blurred_defect = cv2.GaussianBlur(defect_mask, (25, 25), 0)
        norm_defect = cv2.normalize(blurred_defect, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        heatmap_raw = cv2.applyColorMap(norm_defect, cv2.COLORMAP_JET)
        dimmed_original = (img_bgr * 0.35).astype(np.uint8)
        alpha_mask = cv2.cvtColor(norm_defect, cv2.COLOR_GRAY2BGR) / 255.0
        blended = (heatmap_raw * alpha_mask + img_bgr * (1.0 - alpha_mask * 0.8)).astype(np.uint8)
        food_mask_3ch = cv2.cvtColor(food_mask, cv2.COLOR_GRAY2BGR) / 255.0
        final_heatmap = (blended * food_mask_3ch + dimmed_original * (1.0 - food_mask_3ch)).astype(np.uint8)

        # 3. Spatial Laplacian Texture Gradient Image
        lap_norm = cv2.normalize(defects_info["lap_abs"], None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        lap_colored = cv2.applyColorMap(lap_norm, cv2.COLORMAP_VIRIDIS)
        final_laplacian = (lap_colored * food_mask_3ch + dimmed_original * (1.0 - food_mask_3ch)).astype(np.uint8)

        # 4. CIELAB Luminance Degradation Map
        l_norm = cv2.normalize(defects_info["l_chan"], None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        l_colored = cv2.applyColorMap(255 - l_norm, cv2.COLORMAP_INFERNO)
        final_luminance = (l_colored * food_mask_3ch + dimmed_original * (1.0 - food_mask_3ch)).astype(np.uint8)

        return {
            "annotated_b64": self._cv2_to_base64(annotated),
            "heatmap_b64": self._cv2_to_base64(final_heatmap),
            "laplacian_b64": self._cv2_to_base64(final_laplacian),
            "luminance_b64": self._cv2_to_base64(final_luminance)
        }

    def _cv2_to_base64(self, img_bgr):
        _, buffer = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 88])
        return base64.b64encode(buffer).decode('utf-8')
