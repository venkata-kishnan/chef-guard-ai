"""
ChefGuard AI — Omniverse Restaurant Food Quality & Kitchen Standards
Defines commercial culinary standards for prepared restaurant dishes (Pizzas,
Salads, Fried Chicken, Sushi, Steaks, Burgers) and fresh kitchen produce.
Aligned with USDA, FDA Food Code, and HACCP Kitchen Hygiene Regulations.
"""

RESTAURANT_FOOD_STANDARDS = {
    # --- PREPARED RESTAURANT DISHES ---
    "pizza": {
        "name": "Artisan Pizza",
        "category": "Prepared Culinary Dish",
        "optimal_service_temp_c": "65-72°C (150-160°F)",
        "optimal_shelf_life_hours": 3,
        "color_profile": "golden_melt_red",
        "nominal_diameter_mm": 280.0,
        "target_circularity": 0.95,
        "target_plating_score": 92.0,
        "defect_tolerances": {
            "grade_a_max_defect_pct": 4.0,   # slight leopard spotting acceptable
            "grade_b_max_defect_pct": 12.0,  # moderate edge char
            "grade_c_max_defect_pct": 25.0   # overcooked crust
        },
        "service_verdict": {
            "pass": "APPROVED FOR GUEST SERVICE — Golden Melt & Crust Uniformity Verified",
            "conditional": "SUB-STANDARD BAKE — Crust Over-charred; Reheat or Trim",
            "fail": "CULL & RE-FIRE — Excessive Acrylamide Scorching or Stale Base"
        },
        "kitchen_action": "Oven stone calibrated at 450°C. Maintain 90-second bake window. Check cheese moisture separation.",
        "haccp_ccp": "CCP-1: Cooked core temperature must reach min 74°C (165°F) for foodborne pathogen inactivation."
    },
    "salad": {
        "name": "Chef's Gourmet Garden Salad",
        "category": "Cold Kitchen Prep",
        "optimal_service_temp_c": "2-4°C (35-40°F)",
        "optimal_shelf_life_hours": 2,
        "color_profile": "vibrant_green_red",
        "nominal_diameter_mm": 180.0,
        "target_circularity": 0.82,
        "target_plating_score": 95.0,
        "defect_tolerances": {
            "grade_a_max_defect_pct": 3.0,
            "grade_b_max_defect_pct": 10.0,
            "grade_c_max_defect_pct": 20.0
        },
        "service_verdict": {
            "pass": "APPROVED FOR SERVICE — Crisp Cellular Turgidity & Zero Wilting",
            "conditional": "REFRESH GREENS — Minor Edge Oxidation; Dressing Breakdown",
            "fail": "DISCARD BATCH — Slime Accumulation or Microbial Decomposition"
        },
        "kitchen_action": "Hold greens in ice bath before dressing. Toss immediately prior to table service.",
        "haccp_ccp": "CCP-2: Cold-holding limit max 5°C. Zero tolerance for unwashed leafy green enteric pathogens."
    },
    "fried_chicken": {
        "name": "Crispy Fried Chicken / Cutlet",
        "category": "Deep Fried Poultry",
        "optimal_service_temp_c": "70-75°C (158-167°F)",
        "optimal_shelf_life_hours": 2,
        "color_profile": "golden_brown_crunch",
        "nominal_diameter_mm": 140.0,
        "target_circularity": 0.72,
        "target_plating_score": 90.0,
        "defect_tolerances": {
            "grade_a_max_defect_pct": 5.0,
            "grade_b_max_defect_pct": 14.0,
            "grade_c_max_defect_pct": 28.0
        },
        "service_verdict": {
            "pass": "APPROVED FOR GUEST SERVICE — Golden Crisp Maillard Crust",
            "conditional": "SECONDARY HOLDING — Crust Softening or Minor Over-Fry",
            "fail": "RE-FIRE ORDER — Surface Scorching or Undercooked Inner Flesh"
        },
        "kitchen_action": "Verify fryer oil polar compound < 24%. Core internal temp must register 74°C.",
        "haccp_ccp": "CCP-1: Salmonella and Campylobacter thermal death time verification."
    },
    "sushi_salmon": {
        "name": "Atlantic Salmon Sashimi / Nigiri",
        "category": "Raw Seafood Prep",
        "optimal_service_temp_c": "3-6°C (37-43°F)",
        "optimal_shelf_life_hours": 1,
        "color_profile": "vibrant_coral_orange",
        "nominal_diameter_mm": 110.0,
        "target_circularity": 0.65,
        "target_plating_score": 98.0,
        "defect_tolerances": {
            "grade_a_max_defect_pct": 2.0,
            "grade_b_max_defect_pct": 6.0,
            "grade_c_max_defect_pct": 15.0
        },
        "service_verdict": {
            "pass": "APPROVED FOR GUEST SERVICE — Grade 1 Sashimi Flesh Translucency",
            "conditional": "USE FOR COOKED ROLLS — Mild Metmyoglobin Oxidation",
            "fail": "BIO-HAZARD / DISCARD — High Histamine / Bacterial Spoilage"
        },
        "kitchen_action": "Slice with clean Yanagiba blade. Disinfect bamboo rolling mats between tickets.",
        "haccp_ccp": "CCP-3: Parasite destruction freezing log (-20°C for 7 days or -35°C for 15 hours)."
    },
    "steak": {
        "name": "Char-Grilled Steak / Beef",
        "category": "Grilled Protein",
        "optimal_service_temp_c": "55-65°C (130-150°F)",
        "optimal_shelf_life_hours": 1,
        "color_profile": "sear_maillard_brown",
        "nominal_diameter_mm": 160.0,
        "target_circularity": 0.78,
        "target_plating_score": 94.0,
        "defect_tolerances": {
            "grade_a_max_defect_pct": 6.0,
            "grade_b_max_defect_pct": 16.0,
            "grade_c_max_defect_pct": 30.0
        },
        "service_verdict": {
            "pass": "APPROVED FOR SERVICE — Optimal Maillard Sear & Resting Moisture",
            "conditional": "OVER-SEARED — Minor Bitter Crust Formation",
            "fail": "RE-FIRE ORDER — Surface Carbonization or Cold Center"
        },
        "kitchen_action": "Rest steak 5 minutes on warm cutting board before slicing to retain intramuscular juices.",
        "haccp_ccp": "CCP-1: E. coli surface pasteurization (min 63°C surface sear)."
    },
    # --- RAW PRODUCE & COMMODITIES ---
    "apple": {
        "name": "Apple (Kitchen Prep)",
        "category": "Fruit Produce",
        "optimal_service_temp_c": "4-8°C",
        "optimal_shelf_life_hours": 120,
        "color_profile": "red_green_yellow",
        "nominal_diameter_mm": 75.0,
        "target_circularity": 0.88,
        "target_plating_score": 90.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 5.0, "grade_b_max_defect_pct": 15.0, "grade_c_max_defect_pct": 30.0},
        "service_verdict": {"pass": "APPROVED — Fresh Salad/Garnish Grade", "conditional": "TRIM DEFECTS — Use in Sauce/Pastry", "fail": "DISCARD — Core Rot / Patulin"},
        "kitchen_action": "Store in walk-in crisper away from culinary greens.",
        "haccp_ccp": "CCP-1: Wash in 50ppm sanitizing fruit rinse."
    },
    "banana": {
        "name": "Banana (Bakery Prep)",
        "category": "Tropical Fruit",
        "optimal_service_temp_c": "15-18°C",
        "optimal_shelf_life_hours": 72,
        "color_profile": "yellow_green_brown",
        "nominal_diameter_mm": 35.0,
        "target_circularity": 0.42,
        "target_plating_score": 85.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 8.0, "grade_b_max_defect_pct": 22.0, "grade_c_max_defect_pct": 45.0},
        "service_verdict": {"pass": "APPROVED — Dessert Plating Ready", "conditional": "USE FOR BANANA BREAD — High Sugar Browning", "fail": "DISCARD — Fermented Flesh"},
        "kitchen_action": "Do not refrigerate unripe fruit to avoid chilling injury.",
        "haccp_ccp": "CCP-2: Crown rot exclusion."
    },
    "tomato": {
        "name": "Tomato (Kitchen Prep)",
        "category": "Salad / Sauce Prep",
        "optimal_service_temp_c": "12-15°C",
        "optimal_shelf_life_hours": 96,
        "color_profile": "red_orange",
        "nominal_diameter_mm": 65.0,
        "target_circularity": 0.92,
        "target_plating_score": 92.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 4.0, "grade_b_max_defect_pct": 14.0, "grade_c_max_defect_pct": 28.0},
        "service_verdict": {"pass": "APPROVED — Slicing / Table Ready", "conditional": "USE IN SAUCE / STEW — Wrinkled Skin", "fail": "DISCARD — Fungal Mycelium"},
        "kitchen_action": "Store stem-down at room temperature to preserve aroma volatiles.",
        "haccp_ccp": "CCP-1: Skin integrity check."
    },
    "orange": {
        "name": "Orange (Beverage Prep)",
        "category": "Citrus",
        "optimal_service_temp_c": "4-6°C",
        "optimal_shelf_life_hours": 168,
        "color_profile": "orange_yellow",
        "nominal_diameter_mm": 72.0,
        "target_circularity": 0.94,
        "target_plating_score": 90.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 6.0, "grade_b_max_defect_pct": 18.0, "grade_c_max_defect_pct": 32.0},
        "service_verdict": {"pass": "APPROVED — Bar & Garnish Grade", "conditional": "JUICING ONLY — Surface Blemishes", "fail": "DISCARD — Penicillium Mold"},
        "kitchen_action": "Isolate moldy fruits immediately to prevent airborne spore contamination.",
        "haccp_ccp": "CCP-3: Fungal cross-contamination control."
    },
    "bread": {
        "name": "Artisan Bread / Buns",
        "category": "Bakery",
        "optimal_service_temp_c": "Room Temp (18-22°C)",
        "optimal_shelf_life_hours": 48,
        "color_profile": "golden_brown",
        "nominal_diameter_mm": 110.0,
        "target_circularity": 0.85,
        "target_plating_score": 90.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 1.0, "grade_b_max_defect_pct": 5.0, "grade_c_max_defect_pct": 10.0},
        "service_verdict": {"pass": "APPROVED — Table Bread Ready", "conditional": "TOAST OR CROUTONS — Stale Crumb", "fail": "DISCARD IMMEDIATELY — Fungal Spores"},
        "kitchen_action": "Store in breathable bread bins; never refrigerate (accelerates retrogradation).",
        "haccp_ccp": "CCP-1: Zero tolerance for Penicillium or Rhizopus mold."
    },
    "general": {
        "name": "General Commercial Food / Prep",
        "category": "Kitchen Commodity",
        "optimal_service_temp_c": "Per Recipe",
        "optimal_shelf_life_hours": 24,
        "color_profile": "multi",
        "nominal_diameter_mm": 80.0,
        "target_circularity": 0.80,
        "target_plating_score": 88.0,
        "defect_tolerances": {"grade_a_max_defect_pct": 5.0, "grade_b_max_defect_pct": 15.0, "grade_c_max_defect_pct": 30.0},
        "service_verdict": {"pass": "APPROVED FOR SERVICE", "conditional": "CONDITIONAL RE-FIRE", "fail": "DISCARD / CULL"},
        "kitchen_action": "Follow standard restaurant sanitation SOPs.",
        "haccp_ccp": "CCP-1: Organoleptic food safety verification."
    }
}

FOOD_STANDARDS = RESTAURANT_FOOD_STANDARDS

def determine_restaurant_culinary_grade(freshness_score: float, defect_percentage: float, item_key: str = "general", diameter_mm: float = 0.0) -> dict:
    """
    Computes culinary grade, table service clearance, plating aesthetic score,
    and commercial kitchen action directives.
    """
    standards = RESTAURANT_FOOD_STANDARDS.get(item_key, RESTAURANT_FOOD_STANDARDS["general"])
    tol = standards["defect_tolerances"]
    verdicts = standards.get("service_verdict", RESTAURANT_FOOD_STANDARDS["general"]["service_verdict"])

    # 1. Commercial Culinary Grade & Service Verdict
    if freshness_score >= 85 and defect_percentage <= tol["grade_a_max_defect_pct"]:
        grade = "Grade A"
        category = "Michelin / Premium Quality"
        color = "#10B981"  # emerald-500
        service_status = verdicts["pass"]
        pass_status = True
        service_badge = "READY TO SERVE"
        haccp_verdict = "CCP PASSED — Safe for Immediate Consumption"
    elif freshness_score >= 70 and defect_percentage <= tol["grade_b_max_defect_pct"]:
        grade = "Grade B"
        category = "Standard Commercial Plating"
        color = "#3B82F6"  # blue-500
        service_status = verdicts.get("conditional", verdicts["pass"])
        pass_status = True
        service_badge = "CONDITIONAL PASS"
        haccp_verdict = "CCP PASSED — Minor Cosmetic Anomaly"
    elif freshness_score >= 48 and defect_percentage <= tol["grade_c_max_defect_pct"]:
        grade = "Grade C"
        category = "Sub-Standard / Re-fire Needed"
        color = "#F59E0B"  # amber-500
        service_status = verdicts.get("conditional", "RE-FIRE / REHEAT REQUIRED")
        pass_status = False
        service_badge = "RE-FIRE IN KITCHEN"
        haccp_verdict = "CCP CONDITIONAL — Corrective Thermal Action Required"
    else:
        grade = "Rejected"
        category = "Spoiled / Bio-Hazard"
        color = "#EF4444"  # red-500
        service_status = verdicts["fail"]
        pass_status = False
        service_badge = "DISCARD & QUARANTINE"
        haccp_verdict = "CCP FAILED — Critical Hygiene Non-Conformance"

    # 2. Plating & Visual Appeal Score (0-100)
    base_appeal = standards.get("target_plating_score", 90.0)
    plating_score = max(10.0, min(99.0, round(base_appeal * (freshness_score / 100.0) - (defect_percentage * 1.5), 1)))

    # 3. Estimated Remaining Service Life
    factor = max(0.0, min(1.0, (freshness_score / 100.0) * (1.0 - (defect_percentage / 100.0))))
    base_hours = standards.get("optimal_shelf_life_hours", 24)
    remaining_hours = max(0.1, round(base_hours * factor, 1))

    # 4. Nutritional / Biochemical Degradation
    vit_c_retention = max(10.0, min(99.0, round(freshness_score * 0.9, 1)))
    moisture_loss = round(max(0.5, min(40.0, (100.0 - freshness_score) * 0.3 + defect_percentage * 0.2), 1))

    return {
        "grade": grade,
        "grade_category": category,
        "badge_color": color,
        "service_badge": service_badge,
        "service_status": service_status,
        "safety_status": service_status,
        "pass_status": pass_status,
        "haccp_verdict": haccp_verdict,
        "haccp_standard": standards.get("haccp_ccp", "Standard restaurant sanitation."),
        "plating_appeal_score": plating_score,
        "remaining_service_hours": remaining_hours,
        "optimal_service_temp": standards.get("optimal_service_temp_c", "Per Chef Specs"),
        "kitchen_action": standards.get("kitchen_action", "Proceed with table service."),
        "nutritional_status": {
            "vitamin_c_retention_pct": vit_c_retention,
            "moisture_loss_pct": moisture_loss,
            "ripeness_stage": "Culinary Prep Validated",
            "ethylene_status": "N/A (Prepared Food)"
        },
        "storage_tips": standards.get("kitchen_action", ""),
        "safety_notes": standards.get("haccp_ccp", "")
    }

# Aliases
determine_grade = determine_restaurant_culinary_grade
determine_grade_and_nutritional_status = determine_restaurant_culinary_grade
