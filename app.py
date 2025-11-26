from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import os
import random
import string
import requests
from datetime import datetime
import base64

app = Flask(__name__)
app.secret_key = "naturehunt-ultimate-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

INATURALIST_API = "https://api.inaturalist.org/v1"
GBIF_API = "https://api.gbif.org/v1"
PBDB_API = "https://paleobiodb.org/data1.2"
MACROSTRAT_API = "https://macrostrat.org/api"
OPENWEATHER_API = "https://api.openweathermap.org/data/2.5"

# High quality stock images for items without photos
FALLBACK_IMAGES = {
    "minerals": {
        "Quartz": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400",
        "Amethyst": "https://images.unsplash.com/photo-1576083500082-7a8be015ec53?w=400",
        "Pyrite": "https://images.unsplash.com/photo-1598886221773-b06e9d971f4e?w=400",
        "Calcite": "https://images.unsplash.com/photo-1611068816888-4e98c17f3e0e?w=400",
        "Agate": "https://images.unsplash.com/photo-1582562124811-c09040d0a901?w=400",
        "Gold Flake": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=400",
        "default": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400"
    },
    "rocks": {
        "Granite": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
        "Basalt": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
        "Limestone": "https://images.unsplash.com/photo-1617791160536-598cf32e7b24?w=400",
        "Sandstone": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400",
        "Obsidian": "https://images.unsplash.com/photo-1612178537253-bccd437b730e?w=400",
        "Meteorite": "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=400",
        "default": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"
    },
    "fossils": {
        "Trilobite": "https://images.unsplash.com/photo-1597424216809-3ba9864aeb18?w=400",
        "Ammonite": "https://images.unsplash.com/photo-1597424216809-3ba9864aeb18?w=400",
        "default": "https://images.unsplash.com/photo-1597424216809-3ba9864aeb18?w=400"
    },
    "artifacts": {
        "Arrowhead": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=400",
        "Pottery Shard": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400",
        "default": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=400"
    }
}

# Poisonous/dangerous species database for safety warnings
DANGEROUS_SPECIES = {
    "Death Cap": {"level": "deadly", "warning": "EXTREMELY POISONOUS - causes fatal liver failure"},
    "Destroying Angel": {"level": "deadly", "warning": "EXTREMELY POISONOUS - no antidote exists"},
    "Amanita": {"level": "deadly", "warning": "Many Amanita species are deadly poisonous"},
    "Poison Hemlock": {"level": "deadly", "warning": "All parts extremely toxic - can be fatal"},
    "Water Hemlock": {"level": "deadly", "warning": "Most toxic plant in North America"},
    "Oleander": {"level": "deadly", "warning": "All parts highly toxic"},
    "Foxglove": {"level": "dangerous", "warning": "Contains cardiac glycosides - toxic"},
    "Nightshade": {"level": "dangerous", "warning": "Berries and leaves are poisonous"},
    "Poison Ivy": {"level": "irritant", "warning": "Causes severe skin rash"},
    "Poison Oak": {"level": "irritant", "warning": "Causes severe skin rash"},
    "Poison Sumac": {"level": "irritant", "warning": "Causes severe skin rash"},
    "False Morel": {"level": "dangerous", "warning": "Contains toxins - can be fatal if eaten raw"},
    "Jack O'Lantern": {"level": "dangerous", "warning": "Poisonous - often confused with chanterelles"},
}

# Lookalike warnings
LOOKALIKES = {
    "Chanterelle": ["Jack O'Lantern (poisonous)", "False Chanterelle"],
    "Morel": ["False Morel (poisonous)", "Wrinkled Thimble Cap"],
    "Chicken of the Woods": ["Jack O'Lantern (poisonous)"],
    "Hen of the Woods": ["Berkeley's Polypore"],
    "Puffball": ["Immature Death Cap (deadly)", "Earthball (poisonous)"],
}

CATEGORIES = {
    "plants": {"name": "Plants", "emoji": "🌿", "color": "#22c55e", "base_points": 10},
    "fungi": {"name": "Fungi", "emoji": "🍄", "color": "#a855f7", "base_points": 25},
    "birds": {"name": "Birds", "emoji": "🐦", "color": "#3b82f6", "base_points": 30},
    "mammals": {"name": "Mammals", "emoji": "🦊", "color": "#f97316", "base_points": 50},
    "reptiles": {"name": "Reptiles", "emoji": "🦎", "color": "#eab308", "base_points": 40},
    "amphibians": {"name": "Amphibians", "emoji": "🐸", "color": "#14b8a6", "base_points": 35},
    "insects": {"name": "Insects", "emoji": "🦋", "color": "#ec4899", "base_points": 15},
    "fish": {"name": "Fish", "emoji": "🐟", "color": "#06b6d4", "base_points": 35},
    "mollusks": {"name": "Mollusks", "emoji": "🐚", "color": "#f472b6", "base_points": 20},
    "minerals": {"name": "Minerals", "emoji": "💎", "color": "#8b5cf6", "base_points": 40},
    "fossils": {"name": "Fossils", "emoji": "🦴", "color": "#78716c", "base_points": 100},
    "artifacts": {"name": "Artifacts", "emoji": "🏺", "color": "#b45309", "base_points": 150},
    "rocks": {"name": "Rocks", "emoji": "🪨", "color": "#64748b", "base_points": 15},
    "tracks": {"name": "Tracks", "emoji": "🐾", "color": "#854d0e", "base_points": 45},
}

ARTIFACTS_DB = {
    "north_america": [
        {"name": "Clovis Point", "age": "13,000 years", "rarity": "legendary", "points": 500, "description": "Prehistoric spear point used by Paleo-Indians", "depth": "0-2m", "photo": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=400"},
        {"name": "Arrowhead", "age": "1,000-10,000 years", "rarity": "uncommon", "points": 75, "description": "Stone projectile point", "depth": "0-1m", "photo": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=400"},
        {"name": "Pottery Shard", "age": "500-3,000 years", "rarity": "common", "points": 30, "description": "Fragment of ancient ceramic vessel", "depth": "0-0.5m", "photo": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=400"},
        {"name": "Grinding Stone", "age": "2,000-8,000 years", "rarity": "rare", "points": 150, "description": "Metate used for processing grain", "depth": "0-1m", "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},
        {"name": "Shell Bead", "age": "1,000-5,000 years", "rarity": "rare", "points": 100, "description": "Ornamental bead from shell", "depth": "0-0.5m", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400"},
        {"name": "Obsidian Blade", "age": "3,000-12,000 years", "rarity": "legendary", "points": 400, "description": "Volcanic glass cutting tool", "depth": "0-1m", "photo": "https://images.unsplash.com/photo-1612178537253-bccd437b730e?w=400"},
        {"name": "Bone Tool", "age": "1,000-15,000 years", "rarity": "rare", "points": 120, "description": "Tool fashioned from animal bone", "depth": "0-1m", "photo": "https://images.unsplash.com/photo-1597424216809-3ba9864aeb18?w=400"},
        {"name": "Petroglyph", "age": "500-15,000 years", "rarity": "legendary", "points": 300, "description": "Rock carving or pictograph", "depth": "surface", "photo": "https://images.unsplash.com/photo-1590069261209-f8e9b8642343?w=400"},
    ],
}

MINERALS_DB = [
    {"name": "Quartz", "rarity": "common", "points": 15, "color": "#ffffff", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Most abundant mineral on Earth, found in many rock types"},
    {"name": "Amethyst", "rarity": "rare", "points": 150, "color": "#a855f7", "photo": "https://images.unsplash.com/photo-1576083500082-7a8be015ec53?w=400", "description": "Purple variety of quartz, prized as a gemstone"},
    {"name": "Pyrite", "rarity": "uncommon", "points": 50, "color": "#fef08a", "photo": "https://images.unsplash.com/photo-1598886221773-b06e9d971f4e?w=400", "description": "Iron sulfide, known as 'fool's gold'"},
    {"name": "Calcite", "rarity": "common", "points": 15, "color": "#f0fdf4", "photo": "https://images.unsplash.com/photo-1611068816888-4e98c17f3e0e?w=400", "description": "Calcium carbonate mineral found in limestone"},
    {"name": "Feldspar", "rarity": "common", "points": 15, "color": "#fce7f3", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Most abundant mineral group in Earth's crust"},
    {"name": "Mica", "rarity": "uncommon", "points": 30, "color": "#a3a3a3", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Sheet silicate mineral with perfect cleavage"},
    {"name": "Tourmaline", "rarity": "rare", "points": 100, "color": "#000000", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Boron silicate mineral, comes in many colors"},
    {"name": "Agate", "rarity": "rare", "points": 100, "color": "#6366f1", "photo": "https://images.unsplash.com/photo-1582562124811-c09040d0a901?w=400", "description": "Banded variety of chalcedony quartz"},
    {"name": "Garnet", "rarity": "rare", "points": 120, "color": "#dc2626", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Silicate mineral group, often deep red"},
    {"name": "Fluorite", "rarity": "uncommon", "points": 60, "color": "#22d3ee", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Calcium fluoride, fluoresces under UV light"},
    {"name": "Opal", "rarity": "legendary", "points": 300, "color": "#ffffff", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Hydrated silica with play of color"},
    {"name": "Gold Flake", "rarity": "legendary", "points": 500, "color": "#fbbf24", "photo": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=400", "description": "Native gold, the most sought-after precious metal"},
    {"name": "Silver Ore", "rarity": "epic", "points": 250, "color": "#9ca3af", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Native silver or silver-bearing ore"},
    {"name": "Copper Ore", "rarity": "rare", "points": 80, "color": "#f97316", "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a8b?w=400", "description": "Native copper or copper minerals"},
]

ROCKS_DB = [
    {"name": "Granite", "rarity": "common", "points": 15, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Coarse-grained igneous rock"},
    {"name": "Basalt", "rarity": "common", "points": 15, "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400", "description": "Fine-grained volcanic rock"},
    {"name": "Limestone", "rarity": "common", "points": 15, "photo": "https://images.unsplash.com/photo-1617791160536-598cf32e7b24?w=400", "description": "Sedimentary rock from marine organisms"},
    {"name": "Sandstone", "rarity": "common", "points": 15, "photo": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400", "description": "Sedimentary rock from sand grains"},
    {"name": "Shale", "rarity": "common", "points": 15, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Fine-grained sedimentary rock"},
    {"name": "Marble", "rarity": "uncommon", "points": 40, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Metamorphosed limestone"},
    {"name": "Slate", "rarity": "uncommon", "points": 35, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Metamorphosed shale"},
    {"name": "Quartzite", "rarity": "uncommon", "points": 40, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Metamorphosed sandstone"},
    {"name": "Obsidian", "rarity": "rare", "points": 100, "photo": "https://images.unsplash.com/photo-1612178537253-bccd437b730e?w=400", "description": "Volcanic glass, extremely sharp"},
    {"name": "Pumice", "rarity": "uncommon", "points": 30, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Lightweight volcanic rock that floats"},
    {"name": "Conglomerate", "rarity": "uncommon", "points": 35, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Sedimentary rock with rounded pebbles"},
    {"name": "Gneiss", "rarity": "uncommon", "points": 45, "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400", "description": "Banded metamorphic rock"},
    {"name": "Meteorite", "rarity": "legendary", "points": 1000, "photo": "https://images.unsplash.com/photo-1614732414444-096e5f1122d5?w=400", "description": "Rock from space! Extremely rare find"},
    {"name": "Tektite", "rarity": "epic", "points": 300, "photo": "https://images.unsplash.com/photo-1612178537253-bccd437b730e?w=400", "description": "Natural glass formed by meteorite impact"},
]

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location_info(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10"
        headers = {"User-Agent": "NatureHunt/3.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        address = data.get("address", {})
        return {
            "city": address.get("city") or address.get("town") or address.get("village") or address.get("county", "Unknown"),
            "state": address.get("state", ""),
            "country": address.get("country", ""),
            "country_code": address.get("country_code", "us"),
            "display": f"{address.get('city') or address.get('town') or address.get('county', 'Unknown')}, {address.get('state', '')}"
        }
    except:
        return {"city": "Unknown", "state": "", "country": "USA", "country_code": "us", "display": "Unknown Location"}

def get_weather(lat, lng):
    try:
        # Using a free weather API that doesn't require key
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true"
        r = requests.get(url, timeout=5)
        data = r.json()
        current = data.get("current_weather", {})
        temp_c = current.get("temperature", 20)
        temp_f = temp_c * 9/5 + 32
        return {
            "temp_f": round(temp_f),
            "temp_c": round(temp_c),
            "conditions": "Clear" if current.get("weathercode", 0) < 3 else "Cloudy",
            "is_good_hunting": 50 < temp_f < 85
        }
    except:
        return {"temp_f": 70, "temp_c": 21, "conditions": "Unknown", "is_good_hunting": True}

def get_species_from_inaturalist(lat, lng, taxon_name, limit=50):
    try:
        url = f"{INATURALIST_API}/observations/species_counts"
        params = {
            "lat": lat, "lng": lng, "radius": 50,
            "iconic_taxa": taxon_name,
            "quality_grade": "research",
            "per_page": limit
        }
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        species = []
        for result in data.get("results", []):
            taxon = result.get("taxon", {})
            obs_count = result.get("count", 0)
            
            if obs_count < 50:
                rarity = "legendary"
                multiplier = 10
            elif obs_count < 200:
                rarity = "epic"
                multiplier = 5
            elif obs_count < 500:
                rarity = "rare"
                multiplier = 3
            elif obs_count < 2000:
                rarity = "uncommon"
                multiplier = 2
            else:
                rarity = "common"
                multiplier = 1
            
            photo = taxon.get("default_photo", {})
            name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
            
            # Check for dangerous species
            danger_info = None
            for dangerous_name, danger_data in DANGEROUS_SPECIES.items():
                if dangerous_name.lower() in name.lower():
                    danger_info = danger_data
                    break
            
            # Check for lookalikes
            lookalike_info = LOOKALIKES.get(name, [])
            
            species.append({
                "id": taxon.get("id"),
                "name": name,
                "scientific": taxon.get("name", ""),
                "photo": photo.get("medium_url") or photo.get("square_url", ""),
                "photo_large": photo.get("large_url") or photo.get("original_url") or photo.get("medium_url", ""),
                "observations": obs_count,
                "rarity": rarity,
                "multiplier": multiplier,
                "points": CATEGORIES.get(taxon_name.lower(), {}).get("base_points", 10) * multiplier,
                "wikipedia": taxon.get("wikipedia_url", ""),
                "conservation": taxon.get("conservation_status", {}).get("status_name", ""),
                "iconic": taxon.get("iconic_taxon_name", taxon_name),
                "endemic": taxon.get("endemic", False),
                "threatened": taxon.get("threatened", False),
                "danger": danger_info,
                "lookalikes": lookalike_info,
            })
        return species
    except Exception as e:
        print(f"iNaturalist error: {e}")
        return []

def get_fossils_from_pbdb(lat, lng):
    try:
        url = f"{PBDB_API}/occs/list.json"
        params = {
            "lngmin": lng - 1, "lngmax": lng + 1,
            "latmin": lat - 1, "latmax": lat + 1,
            "show": "full", "limit": 50
        }
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        fossils = []
        seen = set()
        for record in data.get("records", []):
            name = record.get("tna", "Unknown Fossil")
            if name in seen:
                continue
            seen.add(name)
            
            age_max = record.get("lag", 0)
            
            if age_max > 250:
                rarity = "legendary"
                points = 500
            elif age_max > 65:
                rarity = "epic"
                points = 300
            elif age_max > 10:
                rarity = "rare"
                points = 150
            else:
                rarity = "uncommon"
                points = 75
            
            fossils.append({
                "name": name,
                "scientific": record.get("idt", name),
                "age": f"{record.get('eag', 0)}-{age_max} Ma",
                "period": record.get("oei", "Unknown"),
                "rarity": rarity,
                "points": points,
                "photo": FALLBACK_IMAGES["fossils"].get("default"),
                "environment": record.get("env", ""),
            })
        return fossils[:30]
    except:
        return []

def identify_species(image_base64, lat, lng):
    """Use iNaturalist CV with confidence thresholds"""
    try:
        url = f"{INATURALIST_API}/computervision/score_image"
        
        if ',' in image_base64:
            image_data = image_base64.split(',')[1]
        else:
            image_data = image_base64
        
        files = {'image': ('photo.jpg', base64.b64decode(image_data), 'image/jpeg')}
        params = {"lat": lat, "lng": lng} if lat and lng else {}
        
        r = requests.post(url, files=files, data=params, timeout=30)
        data = r.json()
        
        results = []
        for result in data.get("results", [])[:10]:
            taxon = result.get("taxon", {})
            photo = taxon.get("default_photo", {})
            score = result.get("combined_score", 0)
            name = taxon.get("preferred_common_name") or taxon.get("name")
            
            # Check danger level
            danger_info = None
            for dangerous_name, danger_data in DANGEROUS_SPECIES.items():
                if dangerous_name.lower() in name.lower():
                    danger_info = danger_data
                    break
            
            # Confidence level
            if score > 0.95:
                confidence = "very_high"
            elif score > 0.85:
                confidence = "high"
            elif score > 0.70:
                confidence = "moderate"
            else:
                confidence = "low"
            
            results.append({
                "name": name,
                "scientific": taxon.get("name"),
                "score": score,
                "confidence": confidence,
                "photo": photo.get("medium_url", ""),
                "iconic": taxon.get("iconic_taxon_name", "Unknown"),
                "id": taxon.get("id"),
                "wikipedia": taxon.get("wikipedia_url", ""),
                "danger": danger_info,
                "lookalikes": LOOKALIKES.get(name, []),
            })
        return results
    except Exception as e:
        print(f"CV error: {e}")
        return []

def calculate_points(base_points, rarity, category):
    multipliers = {"common": 1, "uncommon": 2, "rare": 3, "epic": 5, "legendary": 10}
    cat_config = CATEGORIES.get(category, {"base_points": 10})
    return cat_config["base_points"] * multipliers.get(rarity, 1)

@app.route("/")
def home():
    return render_template("home.html", categories=CATEGORIES)

@app.route("/host", methods=["GET", "POST"])
def host():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        lat = float(request.form.get("lat", 0))
        lng = float(request.form.get("lng", 0))
        
        if not name:
            return render_template("host.html", error="Enter your name")
        
        code = gen_code()
        location = get_location_info(lat, lng)
        
        supabase.table("games").insert({"code": code, "biome": location["display"], "active": True}).execute()
        result = supabase.table("players").insert({"game_code": code, "name": name, "score": 0, "is_host": True}).execute()
        
        session["player_id"] = result.data[0]["id"]
        session["game_code"] = code
        session["player_name"] = name
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("host.html")

@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        name = request.form.get("name", "").strip()
        lat = float(request.form.get("lat", 0))
        lng = float(request.form.get("lng", 0))
        
        if not code or not name:
            return render_template("join.html", error="Enter code and name")
        
        result = supabase.table("games").select("*").eq("code", code).eq("active", True).execute()
        if not result.data:
            return render_template("join.html", error="Game not found")
        
        player = supabase.table("players").insert({"game_code": code, "name": name, "score": 0, "is_host": False}).execute()
        
        session["player_id"] = player.data[0]["id"]
        session["game_code"] = code
        session["player_name"] = name
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
def game(code):
    if "player_id" not in session:
        return redirect(url_for("join"))
    
    game_data = supabase.table("games").select("*").eq("code", code).execute()
    if not game_data.data:
        return redirect(url_for("home"))
    
    game = game_data.data[0]
    players = supabase.table("players").select("*").eq("game_code", code).order("score", desc=True).execute()
    
    lat = session.get("lat", 35.4676)
    lng = session.get("lng", -97.5164)
    
    weather = get_weather(lat, lng)
    
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["player_id"]).execute()
    found_items = [f["item_name"] for f in my_finds.data] if my_finds.data else []
    
    return render_template("game.html",
        game=game,
        players=players.data,
        player_name=session.get("player_name", ""),
        found_items=found_items,
        lat=lat,
        lng=lng,
        weather=weather,
        categories=CATEGORIES
    )

@app.route("/explore")
def explore():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    location = get_location_info(lat, lng)
    return render_template("explore.html", lat=lat, lng=lng, location=location, categories=CATEGORIES)

@app.route("/api/species")
def api_species():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    location = get_location_info(lat, lng)
    data = {"location": location, "categories": {}}
    
    taxon_map = {
        "plants": "Plantae", "fungi": "Fungi", "birds": "Aves",
        "mammals": "Mammalia", "reptiles": "Reptilia", "amphibians": "Amphibia",
        "insects": "Insecta", "fish": "Actinopterygii", "mollusks": "Mollusca"
    }
    
    if category == "all":
        for cat, taxon in taxon_map.items():
            species = get_species_from_inaturalist(lat, lng, taxon, limit=15)
            if species:
                data["categories"][cat] = species
        
        data["categories"]["fossils"] = get_fossils_from_pbdb(lat, lng)[:10]
        data["categories"]["minerals"] = MINERALS_DB
        data["categories"]["rocks"] = ROCKS_DB
        data["categories"]["artifacts"] = ARTIFACTS_DB.get("north_america", [])
    elif category in taxon_map:
        data["categories"][category] = get_species_from_inaturalist(lat, lng, taxon_map[category], limit=50)
    elif category == "fossils":
        data["categories"]["fossils"] = get_fossils_from_pbdb(lat, lng)
    elif category == "minerals":
        data["categories"]["minerals"] = MINERALS_DB
    elif category == "rocks":
        data["categories"]["rocks"] = ROCKS_DB
    elif category == "artifacts":
        data["categories"]["artifacts"] = ARTIFACTS_DB.get("north_america", [])
    
    return jsonify(data)

@app.route("/api/identify", methods=["POST"])
def api_identify():
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    image = data.get("image")
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    if not image:
        return jsonify({"error": "No image"}), 400
    
    results = identify_species(image, lat, lng)
    return jsonify({"results": results})

@app.route("/api/confirm_find", methods=["POST"])
def api_confirm_find():
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    name = data.get("name")
    category = data.get("category", "plants")
    rarity = data.get("rarity", "common")
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    confidence = data.get("confidence", "low")
    
    # Require high confidence for confirmation
    if confidence == "low":
        return jsonify({"error": "Confidence too low. Try a clearer photo.", "points": 0})
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    points = calculate_points(10, rarity, category.lower())
    
    supabase.table("finds").insert({
        "user_id": player_id,
        "game_code": game_code,
        "item_name": name,
        "category": category,
        "points": points,
        "latitude": lat,
        "longitude": lng
    }).execute()
    
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = player.data[0]["score"] + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score})

@app.route("/api/leaderboard/<code>")
def api_leaderboard(code):
    players = supabase.table("players").select("name,score,is_host").eq("game_code", code).order("score", desc=True).execute()
    return jsonify(players.data)

@app.route("/collection")
def collection():
    if "player_id" not in session:
        return redirect(url_for("home"))
    
    finds = supabase.table("finds").select("*").eq("user_id", session["player_id"]).order("created_at", desc=True).execute()
    total = sum(f["points"] for f in finds.data) if finds.data else 0
    
    by_category = {}
    for f in (finds.data or []):
        cat = f.get("category", "other")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(f)
    
    return render_template("collection.html", finds=finds.data or [], total=total, by_category=by_category, categories=CATEGORIES)

@app.route("/map")
def map_view():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    return render_template("map.html", lat=lat, lng=lng, categories=CATEGORIES)

@app.route("/safety")
def safety():
    return render_template("safety.html", dangerous=DANGEROUS_SPECIES, lookalikes=LOOKALIKES)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
