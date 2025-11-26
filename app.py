from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import os
import random
import string
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "naturehunt-ultimate-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# API Endpoints
INATURALIST_API = "https://api.inaturalist.org/v1"
GBIF_API = "https://api.gbif.org/v1"
PBDB_API = "https://paleobiodb.org/data1.2"
MACROSTRAT_API = "https://macrostrat.org/api"

# Category configuration with rarity multipliers
CATEGORIES = {
    "plants": {"name": "Plants", "emoji": "🌿", "color": "#22c55e", "base_points": 10, "api": "inaturalist", "taxon": "Plantae"},
    "fungi": {"name": "Fungi", "emoji": "🍄", "color": "#a855f7", "base_points": 25, "api": "inaturalist", "taxon": "Fungi"},
    "birds": {"name": "Birds", "emoji": "🐦", "color": "#3b82f6", "base_points": 30, "api": "inaturalist", "taxon": "Aves"},
    "mammals": {"name": "Mammals", "emoji": "🦊", "color": "#f97316", "base_points": 50, "api": "inaturalist", "taxon": "Mammalia"},
    "reptiles": {"name": "Reptiles", "emoji": "🦎", "color": "#eab308", "base_points": 40, "api": "inaturalist", "taxon": "Reptilia"},
    "amphibians": {"name": "Amphibians", "emoji": "🐸", "color": "#14b8a6", "base_points": 35, "api": "inaturalist", "taxon": "Amphibia"},
    "insects": {"name": "Insects", "emoji": "🦋", "color": "#ec4899", "base_points": 15, "api": "inaturalist", "taxon": "Insecta"},
    "fish": {"name": "Fish", "emoji": "🐟", "color": "#06b6d4", "base_points": 35, "api": "inaturalist", "taxon": "Actinopterygii"},
    "mollusks": {"name": "Mollusks", "emoji": "🐚", "color": "#f472b6", "base_points": 20, "api": "inaturalist", "taxon": "Mollusca"},
    "minerals": {"name": "Minerals", "emoji": "💎", "color": "#8b5cf6", "base_points": 40, "api": "macrostrat"},
    "fossils": {"name": "Fossils", "emoji": "🦴", "color": "#78716c", "base_points": 100, "api": "pbdb"},
    "artifacts": {"name": "Artifacts", "emoji": "🏺", "color": "#b45309", "base_points": 150, "api": "local"},
    "rocks": {"name": "Rocks", "emoji": "🪨", "color": "#64748b", "base_points": 15, "api": "macrostrat"},
    "tracks": {"name": "Tracks", "emoji": "🐾", "color": "#854d0e", "base_points": 45, "api": "local"},
}

# Artifact database by region type
ARTIFACTS_DB = {
    "north_america": [
        {"name": "Clovis Point", "age": "13,000 years", "rarity": "legendary", "points": 500, "description": "Prehistoric spear point used by Paleo-Indians", "depth": "0-2m"},
        {"name": "Arrowhead", "age": "1,000-10,000 years", "rarity": "uncommon", "points": 75, "description": "Stone projectile point", "depth": "0-1m"},
        {"name": "Pottery Shard", "age": "500-3,000 years", "rarity": "common", "points": 30, "description": "Fragment of ancient ceramic vessel", "depth": "0-0.5m"},
        {"name": "Grinding Stone", "age": "2,000-8,000 years", "rarity": "rare", "points": 150, "description": "Metate used for processing grain", "depth": "0-1m"},
        {"name": "Shell Bead", "age": "1,000-5,000 years", "rarity": "rare", "points": 100, "description": "Ornamental bead from shell", "depth": "0-0.5m"},
        {"name": "Obsidian Blade", "age": "3,000-12,000 years", "rarity": "legendary", "points": 400, "description": "Volcanic glass cutting tool", "depth": "0-1m"},
        {"name": "Bone Tool", "age": "1,000-15,000 years", "rarity": "rare", "points": 120, "description": "Tool fashioned from animal bone", "depth": "0-1m"},
        {"name": "Petroglyph", "age": "500-15,000 years", "rarity": "legendary", "points": 300, "description": "Rock carving or pictograph", "depth": "surface"},
    ],
    "europe": [
        {"name": "Roman Coin", "age": "1,500-2,000 years", "rarity": "rare", "points": 200, "description": "Currency from Roman Empire", "depth": "0-2m"},
        {"name": "Medieval Pottery", "age": "500-1,000 years", "rarity": "uncommon", "points": 60, "description": "Ceramic from Middle Ages", "depth": "0-1m"},
        {"name": "Flint Scraper", "age": "5,000-300,000 years", "rarity": "common", "points": 40, "description": "Stone tool for hide processing", "depth": "0-2m"},
        {"name": "Bronze Age Axe", "age": "3,000-4,000 years", "rarity": "legendary", "points": 600, "description": "Metal tool from Bronze Age", "depth": "0-2m"},
    ],
}

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location_info(lat, lng):
    """Get detailed location information"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10"
        headers = {"User-Agent": "NatureHunt/2.0"}
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

def get_species_from_inaturalist(lat, lng, taxon_name, limit=50):
    """Get species from iNaturalist with full details"""
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
            
            # Calculate rarity
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
            species.append({
                "id": taxon.get("id"),
                "name": taxon.get("preferred_common_name") or taxon.get("name", "Unknown"),
                "scientific": taxon.get("name", ""),
                "photo": photo.get("medium_url") or photo.get("square_url", ""),
                "photo_large": photo.get("large_url") or photo.get("medium_url", ""),
                "observations": obs_count,
                "rarity": rarity,
                "multiplier": multiplier,
                "wikipedia": taxon.get("wikipedia_url", ""),
                "conservation": taxon.get("conservation_status", {}).get("status_name", ""),
                "taxon_id": taxon.get("id"),
                "iconic": taxon.get("iconic_taxon_name", taxon_name),
                "endemic": taxon.get("endemic", False),
                "threatened": taxon.get("threatened", False),
            })
        return species
    except Exception as e:
        print(f"iNaturalist error: {e}")
        return []

def get_fossils_from_pbdb(lat, lng, radius_km=100):
    """Get fossil data from Paleobiology Database"""
    try:
        url = f"{PBDB_API}/occs/list.json"
        params = {
            "lngmin": lng - 1, "lngmax": lng + 1,
            "latmin": lat - 1, "latmax": lat + 1,
            "show": "full",
            "limit": 50
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
            
            age_min = record.get("eag", 0)
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
                "age": f"{age_min}-{age_max} Ma",
                "period": record.get("oei", "Unknown"),
                "type": record.get("rnk", "specimen"),
                "rarity": rarity,
                "points": points,
                "lat": record.get("lat"),
                "lng": record.get("lng"),
                "environment": record.get("env", ""),
            })
        return fossils[:30]
    except Exception as e:
        print(f"PBDB error: {e}")
        return []

def get_geology_from_macrostrat(lat, lng):
    """Get geological data including rock types and minerals"""
    try:
        url = f"{MACROSTRAT_API}/geologic_units/map"
        params = {"lat": lat, "lng": lng, "response": "long"}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        geology = {
            "rock_types": [],
            "minerals": [],
            "age": "",
            "formation": ""
        }
        
        features = data.get("success", {}).get("data", [])
        if features:
            unit = features[0]
            geology["formation"] = unit.get("name", "Unknown Formation")
            geology["age"] = f"{unit.get('b_age', '')} - {unit.get('t_age', '')} Ma"
            
            # Common minerals by rock type
            lith = unit.get("lith", "").lower()
            if "granite" in lith or "ignite" in lith:
                geology["minerals"] = [
                    {"name": "Quartz", "rarity": "common", "points": 15, "color": "#ffffff"},
                    {"name": "Feldspar", "rarity": "common", "points": 15, "color": "#fce7f3"},
                    {"name": "Mica", "rarity": "uncommon", "points": 30, "color": "#a3a3a3"},
                    {"name": "Tourmaline", "rarity": "rare", "points": 100, "color": "#000000"},
                ]
                geology["rock_types"] = [
                    {"name": "Granite", "rarity": "common", "points": 20},
                    {"name": "Pegmatite", "rarity": "rare", "points": 80},
                ]
            elif "limestone" in lith or "sediment" in lith:
                geology["minerals"] = [
                    {"name": "Calcite", "rarity": "common", "points": 15, "color": "#ffffff"},
                    {"name": "Aragonite", "rarity": "uncommon", "points": 40, "color": "#f0fdf4"},
                    {"name": "Pyrite", "rarity": "rare", "points": 75, "color": "#fef08a"},
                ]
                geology["rock_types"] = [
                    {"name": "Limestone", "rarity": "common", "points": 15},
                    {"name": "Shale", "rarity": "common", "points": 15},
                    {"name": "Chert", "rarity": "uncommon", "points": 35},
                ]
            elif "sandstone" in lith:
                geology["minerals"] = [
                    {"name": "Quartz", "rarity": "common", "points": 15, "color": "#ffffff"},
                    {"name": "Iron Oxide", "rarity": "common", "points": 20, "color": "#dc2626"},
                    {"name": "Agate", "rarity": "rare", "points": 100, "color": "#6366f1"},
                ]
                geology["rock_types"] = [
                    {"name": "Sandstone", "rarity": "common", "points": 15},
                    {"name": "Conglomerate", "rarity": "uncommon", "points": 30},
                ]
            else:
                geology["minerals"] = [
                    {"name": "Quartz", "rarity": "common", "points": 15, "color": "#ffffff"},
                    {"name": "Calcite", "rarity": "common", "points": 15, "color": "#f0fdf4"},
                    {"name": "Pyrite", "rarity": "uncommon", "points": 50, "color": "#fef08a"},
                    {"name": "Amethyst", "rarity": "rare", "points": 150, "color": "#a855f7"},
                    {"name": "Gold Flake", "rarity": "legendary", "points": 500, "color": "#fbbf24"},
                ]
                geology["rock_types"] = [
                    {"name": "Granite", "rarity": "common", "points": 15},
                    {"name": "Basalt", "rarity": "common", "points": 15},
                    {"name": "Obsidian", "rarity": "rare", "points": 100},
                    {"name": "Meteorite", "rarity": "legendary", "points": 1000},
                ]
        
        return geology
    except Exception as e:
        print(f"Macrostrat error: {e}")
        return {"rock_types": [], "minerals": [], "age": "", "formation": ""}

def get_artifacts_for_region(country_code):
    """Get artifacts possible in this region"""
    if country_code in ["us", "ca", "mx"]:
        return ARTIFACTS_DB.get("north_america", [])
    elif country_code in ["gb", "de", "fr", "it", "es"]:
        return ARTIFACTS_DB.get("europe", [])
    return ARTIFACTS_DB.get("north_america", [])

def identify_species(image_base64, lat, lng):
    """Use iNaturalist CV to identify from photo"""
    try:
        url = f"{INATURALIST_API}/computervision/score_image"
        
        # Decode base64
        if ',' in image_base64:
            image_data = image_base64.split(',')[1]
        else:
            image_data = image_base64
        
        import base64
        files = {'image': ('photo.jpg', base64.b64decode(image_data), 'image/jpeg')}
        params = {"lat": lat, "lng": lng} if lat and lng else {}
        
        r = requests.post(url, files=files, data=params, timeout=30)
        data = r.json()
        
        results = []
        for result in data.get("results", [])[:10]:
            taxon = result.get("taxon", {})
            photo = taxon.get("default_photo", {})
            results.append({
                "name": taxon.get("preferred_common_name") or taxon.get("name"),
                "scientific": taxon.get("name"),
                "score": result.get("combined_score", 0),
                "photo": photo.get("medium_url", ""),
                "iconic": taxon.get("iconic_taxon_name", "Unknown"),
                "id": taxon.get("id"),
                "wikipedia": taxon.get("wikipedia_url", ""),
            })
        return results
    except Exception as e:
        print(f"CV error: {e}")
        return []

def calculate_points(base_points, rarity, category):
    """Calculate points based on rarity and category"""
    multipliers = {"common": 1, "uncommon": 2, "rare": 3, "epic": 5, "legendary": 10}
    cat_config = CATEGORIES.get(category, {"base_points": 10})
    return cat_config["base_points"] * multipliers.get(rarity, 1)

# Routes
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
        
        supabase.table("games").insert({
            "code": code,
            "biome": location["display"],
            "active": True
        }).execute()
        
        result = supabase.table("players").insert({
            "game_code": code,
            "name": name,
            "score": 0,
            "is_host": True
        }).execute()
        
        session["player_id"] = result.data[0]["id"]
        session["game_code"] = code
        session["player_name"] = name
        session["lat"] = lat
        session["lng"] = lng
        session["location"] = location
        
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
        
        player = supabase.table("players").insert({
            "game_code": code,
            "name": name,
            "score": 0,
            "is_host": False
        }).execute()
        
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
    
    # Get finds for this player
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["player_id"]).execute()
    found_items = [f["item_name"] for f in my_finds.data] if my_finds.data else []
    
    return render_template("game.html",
        game=game,
        players=players.data,
        player_name=session.get("player_name", ""),
        found_items=found_items,
        lat=lat,
        lng=lng,
        categories=CATEGORIES
    )

@app.route("/explore")
def explore():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    location = get_location_info(lat, lng)
    
    return render_template("explore.html",
        lat=lat,
        lng=lng,
        location=location,
        category=category,
        categories=CATEGORIES
    )

@app.route("/api/species")
def api_species():
    """Get all species data for location"""
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    location = get_location_info(lat, lng)
    data = {"location": location, "categories": {}}
    
    if category == "all" or category in ["plants", "fungi", "birds", "mammals", "reptiles", "amphibians", "insects", "fish", "mollusks"]:
        taxon_map = {
            "plants": "Plantae", "fungi": "Fungi", "birds": "Aves",
            "mammals": "Mammalia", "reptiles": "Reptilia", "amphibians": "Amphibia",
            "insects": "Insecta", "fish": "Actinopterygii", "mollusks": "Mollusca"
        }
        
        if category == "all":
            for cat, taxon in taxon_map.items():
                species = get_species_from_inaturalist(lat, lng, taxon, limit=20)
                if species:
                    data["categories"][cat] = species
        else:
            species = get_species_from_inaturalist(lat, lng, taxon_map.get(category, "Plantae"), limit=50)
            data["categories"][category] = species
    
    if category == "all" or category == "fossils":
        fossils = get_fossils_from_pbdb(lat, lng)
        if fossils:
            data["categories"]["fossils"] = fossils
    
    if category == "all" or category in ["minerals", "rocks"]:
        geology = get_geology_from_macrostrat(lat, lng)
        if geology["minerals"]:
            data["categories"]["minerals"] = geology["minerals"]
        if geology["rock_types"]:
            data["categories"]["rocks"] = geology["rock_types"]
        data["geology"] = {"formation": geology["formation"], "age": geology["age"]}
    
    if category == "all" or category == "artifacts":
        artifacts = get_artifacts_for_region(location.get("country_code", "us"))
        data["categories"]["artifacts"] = artifacts
    
    return jsonify(data)

@app.route("/api/identify", methods=["POST"])
def api_identify():
    """Identify species from photo"""
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
    """Confirm and log a find"""
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    name = data.get("name")
    category = data.get("category", "plants")
    rarity = data.get("rarity", "common")
    base_points = data.get("points", 10)
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    # Check if already found
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    points = calculate_points(base_points, rarity, category)
    
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
    
    # Group by category
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
