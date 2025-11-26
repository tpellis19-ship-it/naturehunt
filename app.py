from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os
import random
import string
import requests
import base64
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = "naturehunt-secret-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# iNaturalist API for species identification
INATURALIST_API = "https://api.inaturalist.org/v1"

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location_name(lat, lng):
    """Get location name from coordinates using free Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json"
        headers = {"User-Agent": "NatureHunt/1.0"}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        address = data.get("address", {})
        city = address.get("city") or address.get("town") or address.get("village") or address.get("county", "Unknown")
        state = address.get("state", "")
        return f"{city}, {state}" if state else city
    except:
        return "Unknown Location"

def get_nearby_species(lat, lng, radius_km=50):
    """Get species observed near this location from iNaturalist"""
    try:
        url = f"{INATURALIST_API}/observations/species_counts"
        params = {
            "lat": lat,
            "lng": lng,
            "radius": radius_km,
            "per_page": 30,
            "quality_grade": "research",
            "iconic_taxa": "Plantae,Fungi,Aves,Mammalia,Reptilia,Amphibia,Insecta"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        
        species_list = []
        for result in data.get("results", []):
            taxon = result.get("taxon", {})
            species_list.append({
                "id": taxon.get("id"),
                "name": taxon.get("preferred_common_name") or taxon.get("name", "Unknown"),
                "scientific": taxon.get("name"),
                "photo": taxon.get("default_photo", {}).get("square_url", ""),
                "iconic": taxon.get("iconic_taxon_name", "Unknown"),
                "observations": result.get("count", 0),
                "wikipedia": taxon.get("wikipedia_url", "")
            })
        return species_list
    except Exception as e:
        print(f"iNaturalist API error: {e}")
        return []

def identify_photo(image_base64, lat=None, lng=None):
    """Use iNaturalist's computer vision to identify species in photo"""
    try:
        url = f"{INATURALIST_API}/computervision/score_image"
        
        # Prepare the image
        files = {
            'image': ('photo.jpg', base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64), 'image/jpeg')
        }
        
        params = {}
        if lat and lng:
            params['lat'] = lat
            params['lng'] = lng
        
        r = requests.post(url, files=files, data=params, timeout=30)
        data = r.json()
        
        results = []
        for result in data.get("results", [])[:5]:
            taxon = result.get("taxon", {})
            results.append({
                "name": taxon.get("preferred_common_name") or taxon.get("name", "Unknown"),
                "scientific": taxon.get("name"),
                "score": result.get("combined_score", 0),
                "photo": taxon.get("default_photo", {}).get("square_url", ""),
                "iconic": taxon.get("iconic_taxon_name", "Unknown"),
                "wikipedia": taxon.get("wikipedia_url", ""),
                "id": taxon.get("id")
            })
        return results
    except Exception as e:
        print(f"CV API error: {e}")
        return []

def get_species_info(taxon_id):
    """Get detailed info about a species"""
    try:
        url = f"{INATURALIST_API}/taxa/{taxon_id}"
        r = requests.get(url, timeout=10)
        data = r.json()
        taxon = data.get("results", [{}])[0]
        return {
            "name": taxon.get("preferred_common_name") or taxon.get("name"),
            "scientific": taxon.get("name"),
            "wikipedia_summary": taxon.get("wikipedia_summary", ""),
            "conservation_status": taxon.get("conservation_status", {}).get("status", ""),
            "observations_count": taxon.get("observations_count", 0),
            "photos": [p.get("photo", {}).get("medium_url") for p in taxon.get("taxon_photos", [])[:4]]
        }
    except:
        return None

# Calculate points based on rarity
def calculate_points(observations_count, iconic_taxon):
    base_points = {
        "Plantae": 10,
        "Fungi": 25,
        "Insecta": 15,
        "Aves": 30,
        "Mammalia": 50,
        "Reptilia": 40,
        "Amphibia": 35,
    }.get(iconic_taxon, 20)
    
    # Rarer species = more points
    if observations_count < 100:
        return base_points * 5  # Legendary
    elif observations_count < 500:
        return base_points * 3  # Rare
    elif observations_count < 2000:
        return base_points * 2  # Uncommon
    return base_points  # Common

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/host", methods=["GET","POST"])
def host():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        lat = request.form.get("lat", 0)
        lng = request.form.get("lng", 0)
        
        if not name:
            return render_template("host.html", error="Enter your name")
        
        code = gen_code()
        location_name = get_location_name(lat, lng) if lat and lng else "Unknown"
        
        supabase.table("games").insert({
            "code": code,
            "biome": location_name,
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
        session["lat"] = float(lat) if lat else 0
        session["lng"] = float(lng) if lng else 0
        
        return redirect(url_for("game", code=code))
    return render_template("host.html")

@app.route("/join", methods=["GET","POST"])
def join():
    if request.method == "POST":
        code = request.form.get("code","").strip().upper()
        name = request.form.get("name","").strip()
        lat = request.form.get("lat", 0)
        lng = request.form.get("lng", 0)
        
        if not code or not name:
            return render_template("join.html", error="Enter code and name")
        
        result = supabase.table("games").select("*").eq("code",code).eq("active",True).execute()
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
        session["lat"] = float(lat) if lat else 0
        session["lng"] = float(lng) if lng else 0
        
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
def game(code):
    if "player_id" not in session:
        return redirect(url_for("join"))
    
    game_data = supabase.table("games").select("*").eq("code",code).execute()
    if not game_data.data:
        return redirect(url_for("home"))
    
    game = game_data.data[0]
    players = supabase.table("players").select("*").eq("game_code",code).order("score",desc=True).execute()
    
    lat = session.get("lat", 35.4676)  # Default to Oklahoma
    lng = session.get("lng", -97.5164)
    
    # Get species for this location from iNaturalist
    species = get_nearby_species(lat, lng)
    location_name = game.get("biome", "Unknown")
    
    my_finds = supabase.table("finds").select("*").eq("game_code",code).eq("user_id",session["player_id"]).execute()
    found_species = [f["item_name"] for f in my_finds.data] if my_finds.data else []
    
    return render_template("game.html", 
        game=game, 
        species=species,
        players=players.data, 
        player_name=session.get("player_name",""),
        found_species=found_species,
        location=location_name,
        lat=lat,
        lng=lng
    )

@app.route("/api/identify", methods=["POST"])
def api_identify():
    """Identify species from uploaded photo"""
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    image = data.get("image")  # Base64 image
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    if not image:
        return jsonify({"error": "No image provided"}), 400
    
    # Use iNaturalist CV to identify
    results = identify_photo(image, lat, lng)
    
    if not results:
        return jsonify({"error": "Could not identify. Try a clearer photo."}), 200
    
    return jsonify({"results": results})

@app.route("/api/confirm_find", methods=["POST"])
def confirm_find():
    """Confirm a find after AI identification"""
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    species_name = data.get("name")
    scientific_name = data.get("scientific", "")
    iconic = data.get("iconic", "Unknown")
    photo = data.get("photo", "")  # Base64 or URL
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    observations = data.get("observations", 1000)
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    # Check if already found
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", species_name).execute()
    if existing.data:
        return jsonify({"error": "Already found this species!", "points": 0})
    
    points = calculate_points(observations, iconic)
    
    # Save the find
    supabase.table("finds").insert({
        "user_id": player_id,
        "game_code": game_code,
        "item_name": species_name,
        "category": iconic,
        "points": points,
        "latitude": lat,
        "longitude": lng
    }).execute()
    
    # Update player score
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = player.data[0]["score"] + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({
        "success": True,
        "points": points,
        "new_score": new_score,
        "species": species_name,
        "scientific": scientific_name
    })

@app.route("/api/leaderboard/<code>")
def leaderboard(code):
    players = supabase.table("players").select("name,score,is_host").eq("game_code",code).order("score",desc=True).execute()
    return jsonify(players.data)

@app.route("/api/species/<int:taxon_id>")
def species_detail(taxon_id):
    """Get detailed species info"""
    info = get_species_info(taxon_id)
    if info:
        return jsonify(info)
    return jsonify({"error": "Species not found"}), 404

@app.route("/collection")
def collection():
    if "player_id" not in session:
        return redirect(url_for("home"))
    
    finds = supabase.table("finds").select("*").eq("user_id", session["player_id"]).order("created_at", desc=True).execute()
    
    total_points = sum(f["points"] for f in finds.data) if finds.data else 0
    
    return render_template("collection.html", 
        finds=finds.data if finds.data else [],
        total_points=total_points
    )

@app.route("/explore")
def explore():
    """Explore mode - discover species near you"""
    lat = request.args.get("lat", 35.4676)
    lng = request.args.get("lng", -97.5164)
    
    species = get_nearby_species(float(lat), float(lng), radius_km=25)
    location = get_location_name(float(lat), float(lng))
    
    return render_template("explore.html", species=species, location=location, lat=lat, lng=lng)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
