"""
ChefGuard AI — Restaurant & Kitchen Food Sample Generator
Generates realistic high-resolution culinary dish samples for commercial kitchen inspection:
- Fresh Artisan Pizza & Burnt Overcooked Pizza
- Fresh Gourmet Garden Salad & Wilted Oxidized Salad
- Crispy Golden Fried Chicken & Burnt Scorched Chicken
- Fresh Salmon Sushi Nigiri & Stale Oxidized Sushi
- Grilled Ribeye Steak
- Produce items: Fresh Apple, Bruised Apple, Fresh Banana, Spoiled Banana, Moldy Bread
"""

import os
import sys
import cv2
import numpy as np

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "static", "samples")
os.makedirs(SAMPLES_DIR, exist_ok=True)

# 1. ARTISAN PIZZA (Fresh vs Burnt)
def generate_fresh_pizza():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Golden pizza crust
    cv2.circle(img, (250, 250), 195, (40, 110, 195), -1) # Golden dough
    cv2.circle(img, (250, 250), 165, (30, 80, 210), -1)  # Tomato sauce rim
    # Bubbly melted mozzarella
    cv2.circle(img, (250, 250), 155, (140, 215, 245), -1) # Mozzarella
    
    # Golden melted cheese patches
    for pt in [(210, 220), (280, 200), (220, 290), (300, 280), (250, 250)]:
        cv2.circle(img, pt, 28, (90, 175, 235), -1)

    # Pepperoni slices
    for pt in [(190, 190), (310, 190), (200, 310), (310, 300), (250, 230), (250, 320)]:
        cv2.circle(img, pt, 20, (25, 30, 175), -1)
        cv2.circle(img, pt, 18, (35, 45, 195), -1)

    # Basil leaves
    for pt in [(220, 240), (290, 230), (230, 280)]:
        cv2.ellipse(img, pt, (14, 8), 45, 0, 360, (30, 140, 50), -1)

    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_pizza.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

def generate_burnt_pizza():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Dark over-browned crust
    cv2.circle(img, (250, 250), 195, (25, 45, 90), -1)
    cv2.circle(img, (250, 250), 165, (20, 40, 130), -1)
    cv2.circle(img, (250, 250), 155, (90, 160, 210), -1)

    # Black scorched crust spots (heavy charring)
    for pt in [(110, 210), (140, 140), (250, 65), (370, 150), (415, 270), (360, 380), (210, 425)]:
        cv2.ellipse(img, pt, (35, 18), np.random.randint(0, 180), 0, 360, (15, 18, 25), -1)

    # Scorched cheese blister craters
    for pt in [(220, 210), (290, 260), (240, 300)]:
        cv2.circle(img, pt, 24, (20, 25, 35), -1)

    # Shriveled dried pepperoni
    for pt in [(190, 190), (310, 190), (200, 310), (310, 300)]:
        cv2.circle(img, pt, 18, (15, 20, 95), -1)

    blurred = cv2.GaussianBlur(img, (7, 7), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "burnt_pizza.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

# 2. CHEF'S GARDEN SALAD (Fresh vs Wilted)
def generate_fresh_salad():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Bowl rim
    cv2.circle(img, (250, 250), 190, (230, 230, 235), -1)
    cv2.circle(img, (250, 250), 185, (245, 245, 248), -1)

    # Crisp romaine & spinach leaves (vibrant green)
    leaf_pts = [
        [(190, 170), (240, 130), (310, 160), (280, 230), (210, 220)],
        [(150, 250), (180, 190), (260, 240), (230, 310), (160, 300)],
        [(250, 270), (330, 240), (370, 300), (320, 350), (240, 340)],
        [(210, 210), (290, 190), (330, 250), (280, 300), (220, 280)]
    ]
    for pts in leaf_pts:
        cv2.fillPoly(img, [np.array(pts, np.int32)], (35, 170, 60))

    # Fresh cherry tomato wedges (bright red)
    for pt in [(190, 230), (310, 230), (260, 300), (230, 170)]:
        cv2.circle(img, pt, 16, (25, 30, 225), -1)
        cv2.circle(img, (pt[0]-4, pt[1]-4), 4, (80, 90, 245), -1)

    # Cucumber slices
    for pt in [(250, 210), (180, 290), (320, 280)]:
        cv2.circle(img, pt, 18, (80, 190, 110), -1)
        cv2.circle(img, pt, 14, (160, 225, 180), -1)

    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_salad.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

def generate_wilted_salad():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    cv2.circle(img, (250, 250), 190, (230, 230, 235), -1)
    cv2.circle(img, (250, 250), 185, (245, 245, 248), -1)

    # Wilted brown/yellow decaying lettuce
    leaf_pts = [
        [(190, 170), (240, 130), (310, 160), (280, 230), (210, 220)],
        [(150, 250), (180, 190), (260, 240), (230, 310), (160, 300)],
        [(250, 270), (330, 240), (370, 300), (320, 350), (240, 340)]
    ]
    for pts in leaf_pts:
        # Dull yellow-brown slime
        cv2.fillPoly(img, [np.array(pts, np.int32)], (35, 105, 110))

    # Browning oxidized edges
    for pt in [(190, 160), (300, 150), (160, 220), (350, 260), (260, 330)]:
        cv2.ellipse(img, pt, (32, 14), 25, 0, 360, (25, 45, 75), -1)

    # Shriveled tomatoes
    for pt in [(190, 230), (310, 230), (260, 300)]:
        cv2.circle(img, pt, 14, (20, 25, 130), -1)

    blurred = cv2.GaussianBlur(img, (7, 7), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "wilted_salad.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

# 3. CRISPY FRIED CHICKEN (Golden vs Burnt)
def generate_crispy_chicken():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Drumstick/cutlet shape
    pts = np.array([
        [150, 340], [210, 390], [330, 380], [390, 310], [410, 220],
        [370, 150], [290, 140], [210, 180], [150, 260], [150, 340]
    ], np.int32)
    # Golden brown fried coating
    cv2.fillPoly(img, [pts], (30, 140, 215)) # Golden fried
    # Textured crispy crumb nuggets
    np.random.seed(44)
    for _ in range(120):
        cx = np.random.randint(180, 380)
        cy = np.random.randint(170, 360)
        if cv2.pointPolygonTest(pts, (cx, cy), False) >= 0:
            cv2.circle(img, (cx, cy), np.random.randint(2, 6), (20, 100, 175), -1)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "crispy_chicken.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

def generate_burnt_chicken():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    pts = np.array([
        [150, 340], [210, 390], [330, 380], [390, 310], [410, 220],
        [370, 150], [290, 140], [210, 180], [150, 260], [150, 340]
    ], np.int32)
    cv2.fillPoly(img, [pts], (25, 75, 120)) # Dark over-fried
    # Scorched carbonized black spots
    cv2.ellipse(img, (290, 230), (50, 35), 20, 0, 360, (15, 18, 25), -1)
    cv2.ellipse(img, (220, 300), (40, 25), -30, 0, 360, (18, 20, 30), -1)
    cv2.ellipse(img, (350, 310), (35, 22), 45, 0, 360, (15, 18, 25), -1)
    blurred = cv2.GaussianBlur(img, (7, 7), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "burnt_chicken.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

# 4. SALMON SUSHI NIGIRI (Fresh vs Stale)
def generate_fresh_sushi():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Seasoned rice ball base
    cv2.ellipse(img, (250, 290), (120, 55), 0, 0, 360, (230, 235, 240), -1)
    # Vibrant coral pink salmon drape
    salmon_pts = np.array([
        [140, 260], [190, 200], [290, 190], [370, 230],
        [350, 280], [270, 290], [170, 285], [140, 260]
    ], np.int32)
    cv2.fillPoly(img, [salmon_pts], (70, 115, 245)) # Coral orange-pink
    # White intramuscular fat striations
    for offset in range(-60, 80, 24):
        cv2.line(img, (220 + offset, 195), (180 + offset, 285), (170, 200, 255), 2)
    # Glossy highlight
    cv2.ellipse(img, (260, 230), (45, 12), -10, 0, 360, (130, 165, 255), -1)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_sushi.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

def generate_stale_sushi():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    cv2.ellipse(img, (250, 290), (120, 55), 0, 0, 360, (200, 205, 210), -1)
    salmon_pts = np.array([
        [140, 260], [190, 200], [290, 190], [370, 230],
        [350, 280], [270, 290], [170, 285], [140, 260]
    ], np.int32)
    # Dull gray-brown oxidized fish
    cv2.fillPoly(img, [salmon_pts], (70, 95, 185))
    # Discolored dried edges & oxidized spoilage spots
    cv2.polylines(img, [salmon_pts], True, (20, 30, 45), 8)
    # Bacterial dark necrotic patches
    cv2.ellipse(img, (240, 235), (45, 22), 15, 0, 360, (20, 28, 45), -1)
    cv2.ellipse(img, (310, 250), (30, 16), -20, 0, 360, (22, 30, 48), -1)
    cv2.ellipse(img, (180, 245), (25, 14), 10, 0, 360, (25, 35, 55), -1)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "stale_sushi.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

# 5. CHAR-GRILLED STEAK
def generate_fresh_steak():
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    # Steak cut
    cv2.ellipse(img, (250, 260), (140, 100), -15, 0, 360, (30, 55, 115), -1) # Seared brown
    cv2.ellipse(img, (245, 255), (120, 80), -15, 0, 360, (35, 65, 135), -1)
    # Crosshatch grill marks (diamond sear)
    for x in range(160, 350, 35):
        cv2.line(img, (x, 180), (x + 50, 330), (15, 20, 35), 4)
        cv2.line(img, (x + 50, 180), (x, 330), (15, 20, 35), 4)
    # Rosemary garnish
    cv2.line(img, (200, 220), (320, 260), (30, 120, 45), 3)
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_steak.jpg"), blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])

# 6. PRODUCE RE-GENERATION
def generate_produce():
    # Fresh Apple
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    cv2.circle(img, (250, 270), 170, (20, 25, 195), -1)
    cv2.circle(img, (230, 260), 160, (25, 45, 215), -1)
    cv2.circle(img, (270, 260), 160, (15, 20, 185), -1)
    cv2.ellipse(img, (200, 200), (45, 75), 25, 0, 360, (60, 90, 245), -1)
    cv2.ellipse(img, (250, 130), (35, 18), 0, 0, 360, (15, 15, 120), -1)
    pts = np.array([[250, 130], [255, 95], [268, 65], [262, 63], [250, 93], [246, 130]], np.int32)
    cv2.fillPoly(img, [pts], (30, 60, 90))
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_apple.jpg"), cv2.GaussianBlur(img, (5, 5), 0), [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Bruised Apple
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    cv2.circle(img, (250, 270), 170, (20, 25, 190), -1)
    cv2.circle(img, (230, 260), 160, (25, 40, 210), -1)
    cv2.ellipse(img, (290, 280), (45, 38), -15, 0, 360, (25, 45, 75), -1)
    cv2.circle(img, (300, 290), 22, (15, 25, 45), -1)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "bruised_apple.jpg"), cv2.GaussianBlur(img, (9, 9), 0), [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Fresh Banana
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    b_pts = np.array([[90, 340], [130, 380], [220, 400], [320, 360], [410, 270], [430, 190], [410, 195], [310, 290], [220, 330], [140, 310], [90, 340]], np.int32)
    cv2.fillPoly(img, [b_pts], (30, 215, 245))
    cv2.circle(img, (95, 345), 18, (45, 170, 90), -1)
    cv2.circle(img, (425, 192), 12, (20, 90, 50), -1)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "fresh_banana.jpg"), cv2.GaussianBlur(img, (7, 7), 0), [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Spoiled Banana
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    cv2.fillPoly(img, [b_pts], (35, 140, 165))
    cv2.ellipse(img, (200, 365), (35, 20), 10, 0, 360, (20, 30, 45), -1)
    cv2.ellipse(img, (270, 345), (42, 25), -20, 0, 360, (18, 25, 40), -1)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "spoiled_banana.jpg"), cv2.GaussianBlur(img, (7, 7), 0), [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Moldy Bread
    img = np.ones((500, 500, 3), dtype=np.uint8) * 245
    bread_pts = np.array([[120, 160], [150, 120], [250, 110], [350, 120], [380, 160], [370, 380], [350, 400], [150, 400], [130, 380], [120, 160]], np.int32)
    cv2.fillPoly(img, [bread_pts], (150, 205, 230))
    cv2.polylines(img, [bread_pts], True, (40, 95, 160), 12)
    cv2.circle(img, (220, 230), 38, (120, 160, 90), -1)
    cv2.circle(img, (300, 310), 35, (110, 150, 85), -1)
    cv2.imwrite(os.path.join(SAMPLES_DIR, "moldy_bread.jpg"), cv2.GaussianBlur(img, (7, 7), 0), [cv2.IMWRITE_JPEG_QUALITY, 95])

if __name__ == "__main__":
    generate_fresh_pizza()
    generate_burnt_pizza()
    generate_fresh_salad()
    generate_wilted_salad()
    generate_crispy_chicken()
    generate_burnt_chicken()
    generate_fresh_sushi()
    generate_stale_sushi()
    generate_fresh_steak()
    generate_produce()
    print("All commercial restaurant food samples generated successfully!")
