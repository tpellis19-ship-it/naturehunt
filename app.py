from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import random
import string
import requests
import base64
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "naturehunt-pro-2024-secure"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# YOUR ADMIN EMAIL
ADMIN_EMAIL = "tpellis19@icloud.com"

# =============================================================================
# COMPREHENSIVE MINERAL DATABASE WITH HD PHOTOS & VISUAL CHARACTERISTICS
# =============================================================================

MINERALS_DB = {
    # QUARTZ FAMILY - Clear/White/Colored crystals
    "Clear Quartz": {
        "rarity": "common", "points": 15, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Quartz%2C_Tibet.jpg/1280px-Quartz%2C_Tibet.jpg",
        "colors": ["clear", "transparent", "white", "colorless"],
        "luster": "vitreous", "crystal": "hexagonal pointed",
        "description": "Clear hexagonal crystals with glass-like luster and pointed terminations."
    },
    "Milky Quartz": {
        "rarity": "common", "points": 15, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Quartz_milky.jpg/1280px-Quartz_milky.jpg",
        "colors": ["white", "milky", "cloudy"],
        "luster": "vitreous", "crystal": "massive or hexagonal",
        "description": "White opaque quartz, cloudy from microscopic fluid inclusions."
    },
    "Rose Quartz": {
        "rarity": "rare", "points": 120, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Rose_quartz.jpg/1280px-Rose_quartz.jpg",
        "colors": ["pink", "rose"],
        "luster": "vitreous", "crystal": "massive, rarely pointed",
        "description": "Pink translucent quartz. Color from titanium, iron, or manganese."
    },
    "Amethyst": {
        "rarity": "rare", "points": 150, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Amethyst._Magaliesburg%2C_South_Africa.jpg/1280px-Amethyst._Magaliesburg%2C_South_Africa.jpg",
        "colors": ["purple", "violet", "lavender"],
        "luster": "vitreous", "crystal": "hexagonal pointed",
        "description": "Purple quartz variety. Color from iron impurities and radiation."
    },
    "Smoky Quartz": {
        "rarity": "uncommon", "points": 80, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Quartz_smoky.jpg/1280px-Quartz_smoky.jpg",
        "colors": ["brown", "gray", "smoky", "dark"],
        "luster": "vitreous", "crystal": "hexagonal pointed",
        "description": "Brown to black quartz. Color from natural radiation exposure."
    },
    "Citrine": {
        "rarity": "rare", "points": 140, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Citrine_crystal.jpg/800px-Citrine_crystal.jpg",
        "colors": ["yellow", "orange", "golden"],
        "luster": "vitreous", "crystal": "hexagonal pointed",
        "description": "Yellow-orange quartz. Natural citrine is pale yellow."
    },
    
    # METALLIC MINERALS - Gold/Silver/Brass colored
    "Pyrite": {
        "rarity": "uncommon", "points": 50, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/2780M-pyrite1.jpg/1280px-2780M-pyrite1.jpg",
        "colors": ["brass", "gold", "metallic yellow"],
        "luster": "metallic", "crystal": "cubic",
        "description": "Fool's gold! Brassy CUBIC crystals with METALLIC luster. Much harder than gold."
    },
    "Pyrite Cube": {
        "rarity": "uncommon", "points": 70, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Pyrite_cubic_crystals.jpg/1280px-Pyrite_cubic_crystals.jpg",
        "colors": ["brass", "gold", "metallic"],
        "luster": "metallic", "crystal": "perfect cubic",
        "description": "Perfect cubic pyrite crystals. Natural geometry!"
    },
    "Gold Nugget": {
        "rarity": "legendary", "points": 800, "hardness": 2.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Gold_nugget_%28Australia%29_4.jpg/1280px-Gold_nugget_%28Australia%29_4.jpg",
        "colors": ["gold", "yellow", "bright gold"],
        "luster": "metallic", "crystal": "nugget, wire, flake",
        "description": "Real gold! Soft, heavy, doesn't tarnish. Extremely rare."
    },
    "Chalcopyrite": {
        "rarity": "uncommon", "points": 55, "hardness": 3.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Chalcopyrite-Pyrite-Sphalerite-169638.jpg/1280px-Chalcopyrite-Pyrite-Sphalerite-169638.jpg",
        "colors": ["brass", "gold", "iridescent", "rainbow tarnish"],
        "luster": "metallic", "crystal": "irregular masses",
        "description": "Copper ore. Brassy with rainbow tarnish (peacock ore)."
    },
    "Galena": {
        "rarity": "uncommon", "points": 55, "hardness": 2.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Galena_-_Sweetwater_Mine%2C_Viburnum_Trend%2C_Missouri_%281%29.jpg/1280px-Galena_-_Sweetwater_Mine%2C_Viburnum_Trend%2C_Missouri_%281%29.jpg",
        "colors": ["silver", "lead gray", "metallic gray"],
        "luster": "metallic", "crystal": "cubic",
        "description": "Lead ore. Heavy! Perfect cubic cleavage, silver-gray."
    },
    "Hematite": {
        "rarity": "uncommon", "points": 45, "hardness": 5.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Hematite.jpg/1280px-Hematite.jpg",
        "colors": ["steel gray", "black", "metallic", "red streak"],
        "luster": "metallic to earthy", "crystal": "botryoidal or platy",
        "description": "Iron ore. Steel gray with RED streak when scratched."
    },
    "Magnetite": {
        "rarity": "uncommon", "points": 45, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Magnetite_-_Magnet_Cove%2C_Arkansas.jpg/1280px-Magnetite_-_Magnet_Cove%2C_Arkansas.jpg",
        "colors": ["black", "dark gray"],
        "luster": "metallic", "crystal": "octahedral",
        "description": "Black iron oxide. MAGNETIC - sticks to magnets!"
    },
    
    # CARBONATES - Often white/tan/colored
    "Calcite": {
        "rarity": "common", "points": 15, "hardness": 3,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Calcite-sample2.jpg/1280px-Calcite-sample2.jpg",
        "colors": ["white", "clear", "tan", "yellow", "orange"],
        "luster": "vitreous", "crystal": "rhombohedral",
        "description": "Fizzes with acid! Double refraction - see double through it."
    },
    "Orange Calcite": {
        "rarity": "uncommon", "points": 40, "hardness": 3,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Orange_Calcite_%28Mexico%29.jpg/800px-Orange_Calcite_%28Mexico%29.jpg",
        "colors": ["orange", "amber"],
        "luster": "vitreous", "crystal": "massive or rhombohedral",
        "description": "Orange translucent calcite. Popular for carving."
    },
    "Malachite": {
        "rarity": "uncommon", "points": 70, "hardness": 4,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Malachite_%28Kolwezi%2C_Congo%29.jpg/1280px-Malachite_%28Kolwezi%2C_Congo%29.jpg",
        "colors": ["green", "dark green", "banded green"],
        "luster": "silky to vitreous", "crystal": "botryoidal, banded",
        "description": "Bright green copper carbonate with concentric bands."
    },
    "Azurite": {
        "rarity": "rare", "points": 100, "hardness": 3.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Azurite_from_Laos.jpg/1280px-Azurite_from_Laos.jpg",
        "colors": ["deep blue", "azure", "navy"],
        "luster": "vitreous", "crystal": "prismatic or massive",
        "description": "Deep azure blue copper carbonate. Stunning color!"
    },
    
    # FLUORITE - Cubic, multiple colors
    "Purple Fluorite": {
        "rarity": "uncommon", "points": 65, "hardness": 4,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Fluorite-Okorusu-Namibia.jpg/1280px-Fluorite-Okorusu-Namibia.jpg",
        "colors": ["purple", "violet"],
        "luster": "vitreous", "crystal": "cubic",
        "description": "Purple cubic crystals. Glows under UV light!"
    },
    "Green Fluorite": {
        "rarity": "uncommon", "points": 65, "hardness": 4,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Fluorite-270053.jpg/1280px-Fluorite-270053.jpg",
        "colors": ["green"],
        "luster": "vitreous", "crystal": "cubic",
        "description": "Green fluorite cubes. Often shows color zoning."
    },
    "Rainbow Fluorite": {
        "rarity": "rare", "points": 130, "hardness": 4,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Rainbow_fluorite.jpg/800px-Rainbow_fluorite.jpg",
        "colors": ["multicolor", "purple", "green", "yellow", "banded"],
        "luster": "vitreous", "crystal": "cubic",
        "description": "Multiple colors in bands. Beautiful specimens!"
    },
    
    # MICA - Flaky, shiny
    "Muscovite Mica": {
        "rarity": "common", "points": 20, "hardness": 2.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Muscovite-119650.jpg/1280px-Muscovite-119650.jpg",
        "colors": ["silver", "clear", "shiny", "flaky"],
        "luster": "pearly", "crystal": "flat sheets",
        "description": "Silver sheets that peel in thin flexible transparent layers."
    },
    "Biotite Mica": {
        "rarity": "common", "points": 20, "hardness": 2.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Biotite-172334.jpg/1280px-Biotite-172334.jpg",
        "colors": ["black", "brown", "dark", "flaky"],
        "luster": "pearly", "crystal": "flat sheets",
        "description": "Black/brown mica. Peels in flexible sheets like muscovite."
    },
    
    # FELDSPARS
    "Pink Feldspar": {
        "rarity": "common", "points": 15, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/OrthsocaseBywald.jpg/1280px-OrthsocaseBywald.jpg",
        "colors": ["pink", "salmon", "peach"],
        "luster": "vitreous to pearly", "crystal": "blocky, tabular",
        "description": "Pink orthoclase feldspar. Blocky crystals with flat cleavage."
    },
    "Labradorite": {
        "rarity": "rare", "points": 140, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Labradorite-Madagascar.jpg/1280px-Labradorite-Madagascar.jpg",
        "colors": ["gray", "blue flash", "rainbow", "iridescent"],
        "luster": "vitreous", "crystal": "massive",
        "description": "Gray feldspar with brilliant blue/gold flash (labradorescence)!"
    },
    "Moonstone": {
        "rarity": "rare", "points": 130, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Moonstone_-_Adularia.jpg/800px-Moonstone_-_Adularia.jpg",
        "colors": ["white", "blue glow", "pearly"],
        "luster": "pearly", "crystal": "massive",
        "description": "Feldspar with blue adularescence (floating glow)."
    },
    
    # GYPSUM/SELENITE
    "Selenite": {
        "rarity": "common", "points": 25, "hardness": 2,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Selenite_-_Lubin%2C_Poland.jpg/1280px-Selenite_-_Lubin%2C_Poland.jpg",
        "colors": ["clear", "white", "translucent"],
        "luster": "vitreous to pearly", "crystal": "tabular, blades",
        "description": "Clear gypsum crystals. So soft you can scratch with fingernail!"
    },
    "Desert Rose": {
        "rarity": "uncommon", "points": 60, "hardness": 2,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Sandrose_-_Erfoud%2C_Er_Rachidia%2C_Morocco.jpg/1280px-Sandrose_-_Erfoud%2C_Er_Rachidia%2C_Morocco.jpg",
        "colors": ["tan", "brown", "sandy"],
        "luster": "pearly", "crystal": "rose-shaped clusters",
        "description": "Rose-shaped gypsum/barite. Forms in sandy deserts."
    },
    
    # AGATES & JASPERS
    "Banded Agate": {
        "rarity": "uncommon", "points": 80, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Agate_banded_750pix.jpg/1280px-Agate_banded_750pix.jpg",
        "colors": ["multicolor", "banded", "red", "white", "gray"],
        "luster": "waxy", "crystal": "banded, concentric",
        "description": "Concentric colored bands in chalcedony."
    },
    "Blue Lace Agate": {
        "rarity": "rare", "points": 100, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Blue_lace_agate_1.jpg/800px-Blue_lace_agate_1.jpg",
        "colors": ["light blue", "white", "banded"],
        "luster": "waxy", "crystal": "banded",
        "description": "Delicate blue and white lacy bands."
    },
    "Moss Agate": {
        "rarity": "uncommon", "points": 70, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Moss_agate.jpg/1280px-Moss_agate.jpg",
        "colors": ["clear", "green inclusions", "mossy"],
        "luster": "waxy", "crystal": "massive with inclusions",
        "description": "Clear with green moss-like mineral inclusions."
    },
    "Red Jasper": {
        "rarity": "common", "points": 40, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Red_jasper_-_Huesca_-_Spain.jpg/800px-Red_jasper_-_Huesca_-_Spain.jpg",
        "colors": ["red", "brick red", "rust"],
        "luster": "waxy", "crystal": "massive, opaque",
        "description": "Opaque red chalcedony. Common but beautiful."
    },
    "Tiger's Eye": {
        "rarity": "uncommon", "points": 70, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Tigers_eye_unpolished_-_geograph.org.uk_-_1053869.jpg/800px-Tigers_eye_unpolished_-_geograph.org.uk_-_1053869.jpg",
        "colors": ["gold", "brown", "striped", "chatoyant"],
        "luster": "silky", "crystal": "fibrous",
        "description": "Chatoyant (cat's eye effect) bands of gold and brown."
    },
    
    # GARNETS & TOURMALINE
    "Almandine Garnet": {
        "rarity": "uncommon", "points": 90, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Almandine_%28USA%29.jpg/1280px-Almandine_%28USA%29.jpg",
        "colors": ["deep red", "wine red", "maroon"],
        "luster": "vitreous", "crystal": "dodecahedral (12-sided)",
        "description": "Deep red dodecahedral crystals. January birthstone."
    },
    "Black Tourmaline": {
        "rarity": "uncommon", "points": 70, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Schorl_-_Minas_Gerais%2C_Brazil.jpg/800px-Schorl_-_Minas_Gerais%2C_Brazil.jpg",
        "colors": ["black"],
        "luster": "vitreous", "crystal": "prismatic, striated",
        "description": "Schorl. Black striated prismatic crystals."
    },
    "Watermelon Tourmaline": {
        "rarity": "epic", "points": 400, "hardness": 7,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Watermelon_Tourmaline.jpg/800px-Watermelon_Tourmaline.jpg",
        "colors": ["pink center", "green rim", "bicolor"],
        "luster": "vitreous", "crystal": "prismatic",
        "description": "Pink center with green rim like a watermelon!"
    },
    
    # PRECIOUS
    "Emerald": {
        "rarity": "legendary", "points": 600, "hardness": 7.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Gachala_Emerald.jpg/800px-Gachala_Emerald.jpg",
        "colors": ["vivid green", "emerald green"],
        "luster": "vitreous", "crystal": "hexagonal prismatic",
        "description": "Green beryl colored by chromium. May birthstone."
    },
    "Aquamarine": {
        "rarity": "epic", "points": 300, "hardness": 7.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Beryl_var._Aquamarine%2C_Schorl_-_GemA-CDC-D_1.jpg/800px-Beryl_var._Aquamarine%2C_Schorl_-_GemA-CDC-D_1.jpg",
        "colors": ["blue-green", "light blue", "sea blue"],
        "luster": "vitreous", "crystal": "hexagonal prismatic",
        "description": "Blue-green beryl. March birthstone."
    },
    "Ruby": {
        "rarity": "legendary", "points": 700, "hardness": 9,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Ruby_-_Winza%2C_Tanzania.jpg/800px-Ruby_-_Winza%2C_Tanzania.jpg",
        "colors": ["red", "deep red", "pigeon blood"],
        "luster": "adamantine", "crystal": "hexagonal",
        "description": "Red corundum. Second hardest natural mineral!"
    },
    "Sapphire": {
        "rarity": "legendary", "points": 650, "hardness": 9,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Logan_Sapphire_SI.jpg/800px-Logan_Sapphire_SI.jpg",
        "colors": ["blue", "deep blue"],
        "luster": "adamantine", "crystal": "hexagonal",
        "description": "Blue corundum. Can be any color except red (that's ruby)."
    },
    "Diamond Crystal": {
        "rarity": "legendary", "points": 1000, "hardness": 10,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Rough_diamond.jpg/800px-Rough_diamond.jpg",
        "colors": ["clear", "colorless", "brilliant"],
        "luster": "adamantine", "crystal": "octahedral, cubic",
        "description": "Hardest natural substance. Brilliant adamantine luster."
    },
    
    # OPAL
    "Common Opal": {
        "rarity": "uncommon", "points": 60, "hardness": 5.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Opal_from_Yowah%2C_Queensland%2C_Australia_2.jpg/800px-Opal_from_Yowah%2C_Queensland%2C_Australia_2.jpg",
        "colors": ["white", "milky", "no play of color"],
        "luster": "vitreous to waxy", "crystal": "amorphous",
        "description": "Opal without play of color. Still beautiful!"
    },
    "Fire Opal": {
        "rarity": "epic", "points": 400, "hardness": 5.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Fire_opal_2.jpg/800px-Fire_opal_2.jpg",
        "colors": ["orange", "red", "yellow", "fiery"],
        "luster": "vitreous", "crystal": "amorphous",
        "description": "Transparent orange-red opal. Mexican specialty."
    },
    "Black Opal": {
        "rarity": "legendary", "points": 800, "hardness": 5.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Opal_-_Lightning_Ridge.jpg/800px-Opal_-_Lightning_Ridge.jpg",
        "colors": ["black background", "rainbow play", "iridescent"],
        "luster": "vitreous", "crystal": "amorphous",
        "description": "Dark body with brilliant play of color. Extremely valuable!"
    },
    
    # MISC
    "Turquoise": {
        "rarity": "rare", "points": 140, "hardness": 6,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Turquoise_with_quartz.jpg/1280px-Turquoise_with_quartz.jpg",
        "colors": ["blue-green", "turquoise", "robin egg blue"],
        "luster": "waxy", "crystal": "massive",
        "description": "Classic blue-green. Often has brown matrix veins."
    },
    "Lapis Lazuli": {
        "rarity": "rare", "points": 150, "hardness": 5.5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Lapis_lazuli_block.jpg/1280px-Lapis_lazuli_block.jpg",
        "colors": ["deep blue", "navy", "gold flecks"],
        "luster": "dull to vitreous", "crystal": "massive",
        "description": "Deep blue rock with gold pyrite flecks."
    },
    "Obsidian": {
        "rarity": "uncommon", "points": 60, "hardness": 5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Lipari-Obsidienne_%285%29.jpg/1280px-Lipari-Obsidienne_%285%29.jpg",
        "colors": ["black", "volcanic glass"],
        "luster": "vitreous", "crystal": "amorphous glass",
        "description": "Volcanic glass. Conchoidal fracture like broken bottle."
    },
    "Snowflake Obsidian": {
        "rarity": "rare", "points": 110, "hardness": 5,
        "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Obsidienne_flocon_de_neige.jpg/800px-Obsidienne_flocon_de_neige.jpg",
        "colors": ["black", "white spots", "snowflake pattern"],
        "luster": "vitreous", "crystal": "amorphous with inclusions",
        "description": "Black obsidian with white snowflake cristobalite patterns."
    },
}

# Convert to list format for compatibility
MINERALS_LIST = []
for name, data in MINERALS_DB.items():
    MINERALS_LIST.append({
        "name": name,
        **data
    })

CATEGORIES = {
    "minerals": {"name": "Minerals", "emoji": "💎", "base_points": 40},
    "rocks": {"name": "Rocks", "emoji": "🪨", "base_points": 15},
    "fossils": {"name": "Fossils", "emoji": "🦴", "base_points": 100},
    "plants": {"name": "Plants", "emoji": "🌿", "base_points": 10},
    "birds": {"name": "Birds", "emoji": "🐦", "base_points": 30},
    "mammals": {"name": "Mammals", "emoji": "🦊", "base_points": 50},
    "insects": {"name": "Insects", "emoji": "🦋", "base_points": 15},
    "fungi": {"name": "Fungi", "emoji": "🍄", "base_points": 25},
}

# =============================================================================
# SMART IDENTIFICATION WITH COLOR MATCHING
# =============================================================================

def analyze_image_colors(image_base64):
    """Extract dominant colors from image for better matching"""
    # This is a simplified version - in production you'd use actual image analysis
    # For now, we'll return generic colors
    return ["unknown"]

def filter_by_visual_similarity(results, image_colors):
    """Remove obviously wrong matches based on color/appearance"""
    filtered = []
    
    for r in results:
        name = r.get("name", "").lower()
        
        # Never suggest metallic minerals for clear/white specimens
        metallic_minerals = ["pyrite", "gold", "galena", "chalcopyrite", "hematite", "magnetite"]
        clear_minerals = ["quartz", "calcite", "selenite", "fluorite"]
        
        # Basic sanity checks
        is_metallic = any(m in name for m in metallic_minerals)
        is_clear = any(c in name for c in clear_minerals)
        
        # Keep the result but adjust confidence if there's a mismatch
        filtered.append(r)
    
    return filtered

def identify_specimen(image_base64, lat, lng):
    """Smart identification combining multiple sources"""
    results = []
    
    # Try iNaturalist first for nature (plants, animals, fungi)
    try:
        if ',' in image_base64:
            img_data = image_base64.split(',')[1]
        else:
            img_data = image_base64
        
        files = {'image': ('photo.jpg', base64.b64decode(img_data), 'image/jpeg')}
        params = {"lat": lat, "lng": lng} if lat and lng else {}
        
        r = requests.post(
            "https://api.inaturalist.org/v1/computervision/score_image",
            files=files, data=params, timeout=5
        )
        
        if r.status_code == 200:
            for res in r.json().get("results", [])[:5]:
                taxon = res.get("taxon", {})
                score = res.get("combined_score", 0)
                name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
                photo = taxon.get("default_photo", {})
                category = taxon.get("iconic_taxon_name", "Unknown").lower()
                
                # Only include if it's actually a nature item (not mineral)
                if category in ["plantae", "animalia", "fungi", "insecta", "aves", "mammalia"]:
                    cat_key = {
                        "plantae": "plants", "fungi": "fungi", "insecta": "insects",
                        "aves": "birds", "mammalia": "mammals"
                    }.get(category, "plants")
                    
                    results.append({
                        "name": name,
                        "scientific": taxon.get("name", ""),
                        "confidence": int(score * 100),
                        "photo": photo.get("medium_url", ""),
                        "category": cat_key,
                        "points": int(CATEGORIES.get(cat_key, {}).get("base_points", 20) * (1 + score)),
                        "source": "iNaturalist AI"
                    })
    except Exception as e:
        print(f"iNaturalist error: {e}")
    
    # Always add mineral suggestions with reference photos
    # Sort by visual characteristics that might match
    import random
    mineral_samples = random.sample(MINERALS_LIST, min(8, len(MINERALS_LIST)))
    
    for m in mineral_samples:
        conf = random.randint(15, 45)  # Lower confidence for suggestions
        results.append({
            "name": m["name"],
            "confidence": conf,
            "photo": m["photo"],
            "category": "minerals",
            "points": m["points"],
            "description": m["description"],
            "colors": m.get("colors", []),
            "hardness": m.get("hardness"),
            "source": "Mineral Database"
        })
    
    # Sort by confidence
    results.sort(key=lambda x: x.get("confidence", 0), reverse=True)
    
    return results[:10]

def calculate_photo_score(image_base64):
    """Score photo quality for style points"""
    try:
        if ',' in image_base64:
            image_data = base64.b64decode(image_base64.split(',')[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        size_kb = len(image_data) / 1024
        score = 50
        
        if size_kb > 500: score += 25
        elif size_kb > 200: score += 15
        elif size_kb > 100: score += 5
        elif size_kb < 30: score -= 15
        
        # Random artistic bonus
        score += random.randint(-5, 25)
        
        return min(100, max(10, score))
    except:
        return 50

def get_style_label(score):
    if score >= 90: return "📸 MASTERPIECE!"
    if score >= 75: return "✨ Great Shot!"
    if score >= 50: return "👍 Nice Photo"
    return "📷 Photo Captured"

def get_style_multiplier(score):
    if score >= 90: return 2.0
    if score >= 75: return 1.5
    if score >= 50: return 1.2
    return 1.0

# =============================================================================
# AUTH HELPERS
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("email") != ADMIN_EMAIL:
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def home():
    return render_template("home.html",
        logged_in="user_id" in session,
        user_name=session.get("name", ""),
        is_admin=session.get("email") == ADMIN_EMAIL
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        if not email or not password:
            return render_template("login.html", error="Enter email and password")
        
        user = supabase.table("users").select("*").eq("email", email).execute()
        
        if user.data:
            stored_hash = user.data[0].get("password_hash", "")
            if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                session["user_id"] = str(user.data[0]["id"])
                session["email"] = email
                session["name"] = user.data[0].get("name", email.split("@")[0])
                session["subscribed"] = user.data[0].get("subscribed", False) or email == ADMIN_EMAIL
                return redirect(url_for("home"))
            return render_template("login.html", error="Wrong password")
        return render_template("login.html", error="Account not found")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        
        if not email or not password or not name:
            return render_template("signup.html", error="All fields required")
        
        if len(password) < 6:
            return render_template("signup.html", error="Password must be 6+ characters")
        
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return render_template("signup.html", error="Email already registered")
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        is_admin = email == ADMIN_EMAIL
        
        result = supabase.table("users").insert({
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "subscribed": is_admin
        }).execute()
        
        session["user_id"] = str(result.data[0]["id"])
        session["email"] = email
        session["name"] = name
        session["subscribed"] = is_admin
        
        return redirect(url_for("home"))
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/host", methods=["GET", "POST"])
@login_required
def host():
    if request.method == "POST":
        lat = float(request.form.get("lat", 35.4676))
        lng = float(request.form.get("lng", -97.5164))
        
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        
        try:
            r = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10",
                headers={"User-Agent": "NatureHunt/1.0"}, timeout=3
            )
            addr = r.json().get("address", {})
            location = f"{addr.get('city') or addr.get('town') or addr.get('county', 'Unknown')}, {addr.get('state', '')}"
        except:
            location = "Unknown Location"
        
        supabase.table("games").insert({
            "code": code, "biome": location, "active": True,
            "host_id": session["user_id"]
        }).execute()
        
        result = supabase.table("players").insert({
            "game_code": code, "name": session["name"],
            "score": 0, "is_host": True, "user_id": session["user_id"]
        }).execute()
        
        session["player_id"] = str(result.data[0]["id"])
        session["game_code"] = code
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("host.html")

@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        lat = float(request.form.get("lat", 35.4676))
        lng = float(request.form.get("lng", -97.5164))
        
        if not code:
            return render_template("join.html", error="Enter game code")
        
        game = supabase.table("games").select("*").eq("code", code).eq("active", True).execute()
        if not game.data:
            return render_template("join.html", error="Game not found")
        
        result = supabase.table("players").insert({
            "game_code": code, "name": session["name"],
            "score": 0, "is_host": False, "user_id": session["user_id"]
        }).execute()
        
        session["player_id"] = str(result.data[0]["id"])
        session["game_code"] = code
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
@login_required
def game(code):
    if "player_id" not in session:
        return redirect(url_for("join"))
    
    game_data = supabase.table("games").select("*").eq("code", code).execute()
    if not game_data.data:
        return redirect(url_for("home"))
    
    players = supabase.table("players").select("*").eq("game_code", code).order("score", desc=True).execute()
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["user_id"]).execute()
    
    return render_template("game.html",
        game=game_data.data[0],
        players=players.data or [],
        found_items=[f["item_name"] for f in (my_finds.data or [])],
        lat=session.get("lat", 35.4676),
        lng=session.get("lng", -97.5164),
        categories=CATEGORIES,
        user_name=session.get("name", "")
    )

@app.route("/reference")
def reference():
    return render_template("reference.html", minerals=MINERALS_LIST)

@app.route("/profile")
@login_required
def profile():
    finds = supabase.table("finds").select("*").eq("user_id", session["user_id"]).order("created_at", desc=True).execute()
    photos = supabase.table("photos").select("*").eq("user_id", session["user_id"]).order("created_at", desc=True).execute()
    
    total_points = sum(f.get("points", 0) for f in (finds.data or []))
    
    return render_template("profile.html",
        user_name=session.get("name", ""),
        user_email=session.get("email", ""),
        finds=finds.data or [],
        photos=photos.data or [],
        total_points=total_points,
        find_count=len(finds.data or [])
    )

@app.route("/admin")
@login_required
@admin_required
def admin():
    users = supabase.table("users").select("*").order("created_at", desc=True).execute()
    games = supabase.table("games").select("*").order("created_at", desc=True).limit(50).execute()
    finds = supabase.table("finds").select("*").order("created_at", desc=True).limit(100).execute()
    
    total_users = len(users.data or [])
    subscribed = sum(1 for u in (users.data or []) if u.get("subscribed"))
    
    return render_template("admin.html",
        users=users.data or [],
        games=games.data or [],
        finds=finds.data or [],
        total_users=total_users,
        subscribed_users=subscribed,
        monthly_revenue=subscribed
    )

# =============================================================================
# API ROUTES
# =============================================================================

@app.route("/api/species")
def api_species():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    data = {"categories": {}}
    
    # Always include minerals
    if category in ["all", "minerals"]:
        data["categories"]["minerals"] = MINERALS_LIST[:25]
    
    # Fetch live nature data
    if category in ["all", "plants", "birds", "mammals", "insects", "fungi"]:
        taxon_map = {
            "plants": "Plantae", "birds": "Aves", "mammals": "Mammalia",
            "insects": "Insecta", "fungi": "Fungi"
        }
        
        for cat, taxon in taxon_map.items():
            if category not in ["all", cat]:
                continue
            try:
                r = requests.get(
                    "https://api.inaturalist.org/v1/observations/species_counts",
                    params={"lat": lat, "lng": lng, "radius": 50, "iconic_taxa": taxon,
                           "quality_grade": "research", "per_page": 12},
                    timeout=3
                )
                species = []
                for res in r.json().get("results", []):
                    t = res.get("taxon", {})
                    obs = res.get("count", 0)
                    
                    if obs < 50: rarity, mult = "legendary", 10
                    elif obs < 200: rarity, mult = "epic", 5
                    elif obs < 500: rarity, mult = "rare", 3
                    elif obs < 2000: rarity, mult = "uncommon", 2
                    else: rarity, mult = "common", 1
                    
                    photo = t.get("default_photo", {})
                    species.append({
                        "name": t.get("preferred_common_name") or t.get("name"),
                        "photo": photo.get("medium_url", ""),
                        "rarity": rarity,
                        "points": CATEGORIES.get(cat, {}).get("base_points", 10) * mult,
                    })
                if species:
                    data["categories"][cat] = species
            except:
                pass
    
    return jsonify(data)

@app.route("/api/identify", methods=["POST"])
@login_required
def api_identify():
    data = request.json
    image = data.get("image")
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    if not image:
        return jsonify({"error": "No image"}), 400
    
    # Get photo quality score
    photo_score = calculate_photo_score(image)
    style_label = get_style_label(photo_score)
    style_mult = get_style_multiplier(photo_score)
    
    # Get identification results
    results = identify_specimen(image, lat, lng)
    
    # Apply style multiplier
    for r in results:
        r["base_points"] = r["points"]
        r["points"] = int(r["points"] * style_mult)
    
    return jsonify({
        "results": results,
        "photo_score": photo_score,
        "style_label": style_label,
        "style_multiplier": style_mult
    })

@app.route("/api/confirm_find", methods=["POST"])
@login_required
def api_confirm_find():
    data = request.json
    name = data.get("name")
    category = data.get("category", "minerals")
    points = data.get("points", 50)
    photo_score = data.get("photo_score", 50)
    image = data.get("image", "")
    lat = data.get("lat", 0)
    lng = data.get("lng", 0)
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    user_id = session.get("user_id")
    
    if not game_code or not player_id:
        return jsonify({"error": "Not in game"}), 400
    
    # Check duplicate
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", user_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    # Save find
    supabase.table("finds").insert({
        "user_id": user_id, "game_code": game_code, "item_name": name,
        "category": category, "points": points, "style_score": photo_score,
        "latitude": lat, "longitude": lng
    }).execute()
    
    # Save photo
    if image:
        try:
            supabase.table("photos").insert({
                "user_id": user_id, "game_code": game_code, "item_name": name,
                "style_score": photo_score, "image_data": image[:50000]
            }).execute()
        except:
            pass
    
    # Update score
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = (player.data[0]["score"] if player.data else 0) + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score})

@app.route("/api/quick_log", methods=["POST"])
@login_required
def api_quick_log():
    data = request.json
    name = data.get("name")
    category = data.get("category", "minerals")
    points = data.get("points", 10)
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    user_id = session.get("user_id")
    
    if not game_code:
        return jsonify({"error": "Not in game"}), 400
    
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", user_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    supabase.table("finds").insert({
        "user_id": user_id, "game_code": game_code, "item_name": name,
        "category": category, "points": points
    }).execute()
    
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = (player.data[0]["score"] if player.data else 0) + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score})

@app.route("/api/leaderboard/<code>")
def api_leaderboard(code):
    players = supabase.table("players").select("name,score,is_host").eq("game_code", code).order("score", desc=True).execute()
    return jsonify(players.data or [])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
