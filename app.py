from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os
import random
import string
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = "naturehunt-secret-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BIOMES = {
    "forest": {
        "name": "🌲 Forest",
        "items": {
            "Oak Tree": {"points": 10, "rarity": "common", "emoji": "🌳"},
            "Pine Cone": {"points": 15, "rarity": "common", "emoji": "🌲"},
            "Mushroom": {"points": 25, "rarity": "uncommon", "emoji": "🍄"},
            "Deer": {"points": 50, "rarity": "rare", "emoji": "🦌"},
            "Owl": {"points": 75, "rarity": "rare", "emoji": "🦉"},
            "Bear Tracks": {"points": 100, "rarity": "legendary", "emoji": "🐻"},
        }
    },
    "beach": {
        "name": "🏖️ Beach",
        "items": {
            "Seashell": {"points": 10, "rarity": "common", "emoji": "🐚"},
            "Crab": {"points": 25, "rarity": "uncommon", "emoji": "🦀"},
            "Starfish": {"points": 35, "rarity": "uncommon", "emoji": "⭐"},
            "Dolphin": {"points": 75, "rarity": "rare", "emoji": "🐬"},
            "Sea Turtle": {"points": 100, "rarity": "legendary", "emoji": "🐢"},
            "Whale Sighting": {"points": 150, "rarity": "legendary", "emoji": "🐋"},
        }
    },
    "desert": {
        "name": "🏜️ Desert",
        "items": {
            "Cactus": {"points": 10, "rarity": "common", "emoji": "🌵"},
            "Lizard": {"points": 25, "rarity": "uncommon", "emoji": "🦎"},
            "Scorpion": {"points": 40, "rarity": "uncommon", "emoji": "🦂"},
            "Rattlesnake": {"points": 75, "rarity": "rare", "emoji": "🐍"},
            "Roadrunner": {"points": 60, "rarity": "rare", "emoji": "🐦"},
            "Fossil": {"points": 150, "rarity": "legendary", "emoji": "🦴"},
        }
    },
    "mountain": {
        "name": "⛰️ Mountain",
        "items": {
            "Pine Tree": {"points": 10, "rarity": "common", "emoji": "🌲"},
            "Quartz": {"points": 20, "rarity": "common", "emoji": "💎"},
            "Eagle": {"points": 50, "rarity": "rare", "emoji": "🦅"},
            "Mountain Goat": {"points": 75, "rarity": "rare", "emoji": "🐐"},
            "Elk": {"points": 100, "rarity": "legendary", "emoji": "🫎"},
            "Gold Nugget": {"points": 200, "rarity": "legendary", "emoji": "🥇"},
        }
    },
}

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/host", methods=["GET","POST"])
def host():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        biome = request.form.get("biome","forest")
        if not name:
            return render_template("host.html", biomes=BIOMES, error="Enter your name")
        code = gen_code()
        supabase.table("games").insert({"code":code,"biome":biome,"active":True}).execute()
        result = supabase.table("players").insert({"game_code":code,"name":name,"score":0,"is_host":True}).execute()
        session["player_id"] = result.data[0]["id"]
        session["game_code"] = code
        session["player_name"] = name
        return redirect(url_for("game", code=code))
    return render_template("host.html", biomes=BIOMES)

@app.route("/join", methods=["GET","POST"])
def join():
    if request.method == "POST":
        code = request.form.get("code","").strip().upper()
        name = request.form.get("name","").strip()
        if not code or not name:
            return render_template("join.html", error="Enter code and name")
        result = supabase.table("games").select("*").eq("code",code).eq("active",True).execute()
        if not result.data:
            return render_template("join.html", error="Game not found")
        player = supabase.table("players").insert({"game_code":code,"name":name,"score":0,"is_host":False}).execute()
        session["player_id"] = player.data[0]["id"]
        session["game_code"] = code
        session["player_name"] = name
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
    biome = BIOMES.get(game["biome"], BIOMES["forest"])
    my_finds = supabase.table("finds").select("*").eq("game_code",code).eq("user_id",session["player_id"]).execute()
    found_items = [f["item_name"] for f in my_finds.data] if my_finds.data else []
    return render_template("game.html", game=game, biome=biome, players=players.data, 
                          player_name=session.get("player_name",""), found_items=found_items)

@app.route("/api/find", methods=["POST"])
def log_find():
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    item_name = data.get("item")
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    lat = data.get("lat", 0)
    lng = data.get("lng", 0)
    
    game_data = supabase.table("games").select("biome").eq("code",game_code).execute()
    if not game_data.data:
        return jsonify({"error": "Game not found"}), 404
    
    biome_key = game_data.data[0]["biome"]
    biome = BIOMES.get(biome_key, BIOMES["forest"])
    
    if item_name not in biome["items"]:
        return jsonify({"error": "Invalid item"}), 400
    
    item = biome["items"][item_name]
    points = item["points"]
    
    existing = supabase.table("finds").select("*").eq("game_code",game_code).eq("user_id",player_id).eq("item_name",item_name).execute()
    if existing.data:
        return jsonify({"error": "Already found", "points": 0}), 200
    
    supabase.table("finds").insert({
        "user_id": player_id,
        "game_code": game_code,
        "item_name": item_name,
        "points": points,
        "latitude": lat,
        "longitude": lng,
        "category": biome_key
    }).execute()
    
    player = supabase.table("players").select("score").eq("id",player_id).execute()
    new_score = player.data[0]["score"] + points
    supabase.table("players").update({"score": new_score}).eq("id",player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score, "item": item_name})

@app.route("/api/leaderboard/<code>")
def leaderboard(code):
    players = supabase.table("players").select("name,score,is_host").eq("game_code",code).order("score",desc=True).execute()
    return jsonify(players.data)

@app.route("/collection")
def collection():
    if "player_id" not in session:
        return redirect(url_for("home"))
    finds = supabase.table("finds").select("*").eq("user_id",session["player_id"]).order("created_at",desc=True).execute()
    return render_template("collection.html", finds=finds.data if finds.data else [])

@app.route("/end/<code>")
def end_game(code):
    if "game_code" in session and session["game_code"] == code:
        supabase.table("games").update({"active": False}).eq("code",code).execute()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
