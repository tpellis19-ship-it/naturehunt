from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client
from dotenv import load_dotenv
import os
import random
import string

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "naturehunt-secret-2024")

# Direct credentials (Render env vars not working)
SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BIOMES = {
    "forest": {"name": "Forest", "items": {"Oak": 10, "Pine": 15, "Mushroom": 25}},
    "beach": {"name": "Beach", "items": {"Shell": 10, "Crab": 40, "Starfish": 50}},
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
            return render_template("host.html", biomes=BIOMES, error="Need name")
        code = gen_code()
        supabase.table("games").insert({"code":code,"biome":biome,"active":True}).execute()
        result = supabase.table("players").insert({"game_code":code,"name":name,"score":0,"is_host":True}).execute()
        session["player_id"] = result.data[0]["id"]
        session["game_code"] = code
        return redirect(url_for("game", code=code))
    return render_template("host.html", biomes=BIOMES)

@app.route("/join", methods=["GET","POST"])
def join():
    if request.method == "POST":
        code = request.form.get("code","").strip().upper()
        name = request.form.get("name","").strip()
        if not code or not name:
            return render_template("join.html", error="Need both")
        result = supabase.table("games").select("*").eq("code",code).eq("active",True).execute()
        if not result.data:
            return render_template("join.html", error="Game not found")
        player = supabase.table("players").insert({"game_code":code,"name":name,"score":0}).execute()
        session["player_id"] = player.data[0]["id"]
        session["game_code"] = code
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
def game(code):
    if "player_id" not in session:
        return redirect(url_for("join"))
    game = supabase.table("games").select("*").eq("code",code).execute().data[0]
    players = supabase.table("players").select("*").eq("game_code",code).order("score",desc=True).execute()
    biome = BIOMES.get(game["biome"], BIOMES["forest"])
    return render_template("game.html", game=game, biome=biome, players=players.data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
