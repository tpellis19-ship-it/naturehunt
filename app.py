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
app.secret_key = "naturehunt-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
ADMIN_EMAIL = "tpellis19@icloud.com"

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def home():
    return render_template("home.html", logged_in="user_id" in session, user_name=session.get("name",""), is_admin=session.get("email")==ADMIN_EMAIL)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = supabase.table("users").select("*").eq("email", email).execute()
        if user.data:
            if hashlib.sha256(password.encode()).hexdigest() == user.data[0].get("password_hash",""):
                session["user_id"] = str(user.data[0]["id"])
                session["email"] = email
                session["name"] = user.data[0].get("name", email.split("@")[0])
                return redirect(url_for("home"))
            return render_template("login.html", error="Wrong password")
        return render_template("login.html", error="Account not found")
    return render_template("login.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        name = request.form.get("name","").strip()
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return render_template("signup.html", error="Email exists")
        result = supabase.table("users").insert({"email": email, "name": name, "password_hash": hashlib.sha256(password.encode()).hexdigest()}).execute()
        session["user_id"] = str(result.data[0]["id"])
        session["email"] = email
        session["name"] = name
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/host", methods=["GET","POST"])
@login_required
def host():
    if request.method == "POST":
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        supabase.table("games").insert({"code": code, "biome": "Nature Hunt", "active": True}).execute()
        result = supabase.table("players").insert({"game_code": code, "name": session["name"], "score": 0, "is_host": True, "user_id": session["user_id"]}).execute()
        session["player_id"] = str(result.data[0]["id"])
        session["game_code"] = code
        return redirect(url_for("game", code=code))
    return render_template("host.html")

@app.route("/join", methods=["GET","POST"])
@login_required
def join():
    if request.method == "POST":
        code = request.form.get("code","").upper()
        game = supabase.table("games").select("*").eq("code", code).eq("active", True).execute()
        if not game.data:
            return render_template("join.html", error="Game not found")
        result = supabase.table("players").insert({"game_code": code, "name": session["name"], "score": 0, "is_host": False, "user_id": session["user_id"]}).execute()
        session["player_id"] = str(result.data[0]["id"])
        session["game_code"] = code
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
@login_required
def game(code):
    game_data = supabase.table("games").select("*").eq("code", code).execute()
    if not game_data.data:
        return redirect(url_for("home"))
    players = supabase.table("players").select("*").eq("game_code", code).order("score", desc=True).execute()
    return render_template("game.html", game=game_data.data[0], players=players.data, user_name=session.get("name",""))

@app.route("/api/identify", methods=["POST"])
@login_required
def api_identify():
    data = request.json
    image = data.get("image")
    if not image:
        return jsonify({"error": "No image"}), 400
    
    try:
        if ',' in image:
            img_data = image.split(',')[1]
        else:
            img_data = image
        
        files = {'image': ('photo.jpg', base64.b64decode(img_data), 'image/jpeg')}
        r = requests.post("https://api.inaturalist.org/v1/computervision/score_image", files=files, timeout=15)
        
        results = []
        for res in r.json().get("results", [])[:10]:
            taxon = res.get("taxon", {})
            score = res.get("combined_score", 0)
            photo = taxon.get("default_photo", {})
            results.append({
                "name": taxon.get("preferred_common_name") or taxon.get("name", "Unknown"),
                "scientific_name": taxon.get("name", ""),
                "score": round(score * 100, 1),
                "photo": photo.get("medium_url", ""),
                "category": taxon.get("iconic_taxon_name", "Unknown"),
                "points": 50 if score < 0.5 else 100 if score < 0.8 else 150
            })
        return jsonify({"results": results, "photo_score": 75})
    except Exception as e:
        return jsonify({"error": str(e), "results": []})

@app.route("/api/confirm_find", methods=["POST"])
@login_required
def api_confirm_find():
    data = request.json
    name = data.get("name")
    points = data.get("points", 50)
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    user_id = session.get("user_id")
    
    if not game_code:
        return jsonify({"error": "Not in game"})
    
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", user_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found"})
    
    supabase.table("finds").insert({"user_id": user_id, "game_code": game_code, "item_name": name, "points": points}).execute()
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = (player.data[0]["score"] if player.data else 0) + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score})

@app.route("/api/leaderboard/<code>")
def api_leaderboard(code):
    players = supabase.table("players").select("name,score").eq("game_code", code).order("score", desc=True).execute()
    return jsonify(players.data or [])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
