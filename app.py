from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import random
import string
import requests
import base64
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = "naturehunt-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
ADMIN_EMAIL = "tpellis19@icloud.com"

# =============================================================================
# COMPLETE SPECIES DATABASE - Real Wikimedia Images
# =============================================================================

MINERALS = [
    {"name": "Clear Quartz", "scientific": "SiO2", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Quartz%2C_Tibet.jpg/320px-Quartz%2C_Tibet.jpg",
     "description": "Clear hexagonal crystals with glass-like luster. Most abundant mineral on Earth.",
     "how_to_find": "Look in granite outcrops, stream beds, and geodes.",
     "identify": "6-sided crystals, glass-like, CLEAR or WHITE. Hardness 7 - scratches glass."},
    
    {"name": "Amethyst", "scientific": "SiO2 (purple)", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Amethyst._Magaliesburg%2C_South_Africa.jpg/320px-Amethyst._Magaliesburg%2C_South_Africa.jpg",
     "description": "Purple quartz colored by iron and radiation. February birthstone.",
     "how_to_find": "Found in volcanic geodes. Look for round hollow rocks in basalt.",
     "identify": "Purple color, hexagonal crystals, glass luster."},
    
    {"name": "Rose Quartz", "scientific": "SiO2 (pink)", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Rose_quartz.jpg/320px-Rose_quartz.jpg",
     "description": "Pink quartz. Rarely forms crystals - usually massive chunks.",
     "how_to_find": "Found in pegmatite deposits. Brazil, Madagascar, South Dakota.",
     "identify": "Pink color, translucent, usually no crystal faces."},
    
    {"name": "Smoky Quartz", "scientific": "SiO2 (brown)", "rarity": "uncommon", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Smoky_quartz_2.jpg/320px-Smoky_quartz_2.jpg",
     "description": "Brown to black quartz colored by natural radiation over millions of years.",
     "how_to_find": "Common in granite mountains and pegmatite pockets.",
     "identify": "Brown/gray color, hexagonal crystals, transparent to translucent."},
    
    {"name": "Citrine", "scientific": "SiO2 (yellow)", "rarity": "rare", "points": 140,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Citrine_crystal.jpg/320px-Citrine_crystal.jpg",
     "description": "Yellow-orange quartz. Natural citrine is pale - deep orange is often heated amethyst.",
     "how_to_find": "Rare naturally. Found in granite pegmatites.",
     "identify": "Yellow/orange, hexagonal crystals. Natural is PALE yellow."},
    
    {"name": "Pyrite (Fool's Gold)", "scientific": "FeS2", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/PyriteCubes.jpg/320px-PyriteCubes.jpg",
     "description": "Iron sulfide with brassy metallic luster. NOT gold - harder and lighter than real gold.",
     "how_to_find": "Found in shale, coal seams, and hydrothermal veins.",
     "identify": "BRASSY YELLOW, METALLIC, CUBIC crystals. Pyrite is NOT clear like quartz!"},
    
    {"name": "Malachite", "scientific": "Cu2CO3(OH)2", "rarity": "uncommon", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Malachite_-_Kolwezi%2C_Katanga%2C_Democratic_Republic_of_Congo.jpg/320px-Malachite_-_Kolwezi%2C_Katanga%2C_Democratic_Republic_of_Congo.jpg",
     "description": "Bright green copper carbonate with distinctive banding.",
     "how_to_find": "Found in oxidized copper deposits. Check old copper mine dumps.",
     "identify": "Bright GREEN with bands, soft (H=4), fizzes in acid."},
    
    {"name": "Azurite", "scientific": "Cu3(CO3)2(OH)2", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Azurite-Malachite-284371.jpg/320px-Azurite-Malachite-284371.jpg",
     "description": "Deep azure blue copper carbonate. Often found with malachite.",
     "how_to_find": "Found in oxidized copper deposits, desert regions.",
     "identify": "Deep BLUE, soft, often with green malachite."},
    
    {"name": "Fluorite", "scientific": "CaF2", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Fluorite_crystals_%28purple%29.jpg/320px-Fluorite_crystals_%28purple%29.jpg",
     "description": "Cubic crystals in many colors. Often fluoresces under UV light!",
     "how_to_find": "Found in limestone caves and hydrothermal veins.",
     "identify": "CUBIC crystals, many colors, soft (H=4), often glows under UV."},
    
    {"name": "Calcite", "scientific": "CaCO3", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Calcite-sample.jpg/320px-Calcite-sample.jpg",
     "description": "Calcium carbonate. Shows double refraction - images appear doubled!",
     "how_to_find": "Found in limestone caves and hydrothermal veins.",
     "identify": "Rhombohedral crystals, FIZZES in acid, double image through clear pieces."},
    
    {"name": "Labradorite", "scientific": "(Ca,Na)AlSi3O8", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Labradorite-RoyalOntarioMuseum-Jan18-09.jpg/320px-Labradorite-RoyalOntarioMuseum-Jan18-09.jpg",
     "description": "Gray feldspar with brilliant blue/gold flash (labradorescence)!",
     "how_to_find": "Found in anorthosite and gabbro rocks.",
     "identify": "Gray stone that FLASHES blue/gold when turned in light."},
    
    {"name": "Obsidian", "scientific": "Volcanic glass", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Obsidian_1.jpg/320px-Obsidian_1.jpg",
     "description": "Volcanic glass - cooled so fast crystals couldn't form. Razor sharp!",
     "how_to_find": "Found in volcanic areas - Western USA, Mexico, Iceland.",
     "identify": "Black GLASS, conchoidal fracture, very sharp edges."},
    
    {"name": "Tiger's Eye", "scientific": "SiO2 with fibers", "rarity": "uncommon", "points": 85,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tiger%27s_eye.jpg/320px-Tiger%27s_eye.jpg",
     "description": "Chatoyant quartz with silky golden-brown bands.",
     "how_to_find": "Found in South Africa, Australia, metamorphic iron formations.",
     "identify": "Golden-brown with SILKY bands that shift in light."},
    
    {"name": "Turquoise", "scientific": "CuAl6(PO4)4(OH)8", "rarity": "rare", "points": 160,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Turquoise_with_quartz.jpg/320px-Turquoise_with_quartz.jpg",
     "description": "Classic blue-green gemstone treasured for 5000+ years.",
     "how_to_find": "Found in arid copper deposits - Arizona, Iran, Egypt.",
     "identify": "Blue-green, opaque, often with brown matrix veins."},
    
    {"name": "Garnet", "scientific": "Various silicates", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Almandine_garnet.jpg/320px-Almandine_garnet.jpg",
     "description": "Deep red crystals common in metamorphic rocks.",
     "how_to_find": "Look in mica schist - garnets pop out when rock weathers.",
     "identify": "Red, 12 or 24-faced crystals, hard (H=7), no cleavage."},
    
    {"name": "Hematite", "scientific": "Fe2O3", "rarity": "common", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Hematite-119580.jpg/320px-Hematite-119580.jpg",
     "description": "Iron oxide with RED streak. Mars is red from hematite!",
     "how_to_find": "Found in banded iron formations and volcanic areas.",
     "identify": "Steel gray/black but RED streak on tile. Heavy."},
    
    {"name": "Magnetite", "scientific": "Fe3O4", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Magnetite-118736.jpg/320px-Magnetite-118736.jpg",
     "description": "Iron oxide that sticks to magnets! Natural compass mineral.",
     "how_to_find": "Found in igneous rocks and black sand beaches.",
     "identify": "Black, MAGNETIC (sticks to magnet), octahedral crystals."},
    
    {"name": "Gold Nugget", "scientific": "Au", "rarity": "legendary", "points": 2000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Gold_nugget_%28Australia%29_4_%2816848647509%29.jpg/320px-Gold_nugget_%28Australia%29_4_%2816848647509%29.jpg",
     "description": "Native gold metal. Heavy, soft, never tarnishes. The eternal metal!",
     "how_to_find": "Pan streams in gold country. Gold sinks to bedrock.",
     "identify": "GOLD color, very HEAVY, soft (scratches with knife), doesn't tarnish."},
    
    {"name": "Diamond", "scientific": "C", "rarity": "legendary", "points": 5000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Rough_diamond.jpg/320px-Rough_diamond.jpg",
     "description": "Hardest natural substance. Pure carbon in cubic crystals.",
     "how_to_find": "Found in kimberlite pipes. Crater of Diamonds State Park, Arkansas!",
     "identify": "Hardest mineral (scratches everything), adamantine luster."},
    
    {"name": "Ruby", "scientific": "Al2O3 (red)", "rarity": "legendary", "points": 3000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Ruby_gem.JPG/320px-Ruby_gem.JPG",
     "description": "Red corundum. Second hardest natural mineral!",
     "how_to_find": "Found in metamorphic marble and basalt gravels.",
     "identify": "RED, extremely hard (H=9), hexagonal crystals."},
    
    {"name": "Sapphire", "scientific": "Al2O3 (blue)", "rarity": "legendary", "points": 2500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Sapphire_gem.jpg/320px-Sapphire_gem.jpg",
     "description": "Blue corundum. Can be any color except red.",
     "how_to_find": "Found in metamorphic rocks and alluvial gravels. Montana has sapphires!",
     "identify": "Blue, extremely hard (H=9), hexagonal barrel crystals."},
    
    {"name": "Emerald", "scientific": "Be3Al2Si6O18", "rarity": "legendary", "points": 3500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Emerald_-_GIA.jpg/320px-Emerald_-_GIA.jpg",
     "description": "Green beryl colored by chromium. One of the precious gems.",
     "how_to_find": "Found in mica schist near pegmatites. Colombia, Zambia, Brazil.",
     "identify": "Vivid GREEN, hexagonal crystals, hard (H=7.5)."},
    
    {"name": "Opal", "scientific": "SiO2·nH2O", "rarity": "epic", "points": 400,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Fire_opal.jpg/320px-Fire_opal.jpg",
     "description": "Hydrated silica with rainbow play of color.",
     "how_to_find": "Found in volcanic areas - Australia, Mexico, Ethiopia.",
     "identify": "Rainbow flashes of color, waxy luster, relatively soft."},
    
    {"name": "Meteorite (Iron)", "scientific": "Fe-Ni alloy", "rarity": "legendary", "points": 3000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Sikhote-Alin_meteorite.jpg/320px-Sikhote-Alin_meteorite.jpg",
     "description": "From space! Iron-nickel alloy from asteroid cores.",
     "how_to_find": "Use metal detector in deserts. Very heavy and magnetic.",
     "identify": "MAGNETIC, very HEAVY, fusion crust, Widmanstatten patterns inside."},
]

FOSSILS = [
    {"name": "Trilobite", "scientific": "Trilobita", "rarity": "rare", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Trilobite_fossil.jpg/320px-Trilobite_fossil.jpg",
     "period": "Cambrian-Permian (520-252 MYA)",
     "description": "Ancient marine arthropod. Over 20,000 species existed!",
     "how_to_find": "Look in shale and limestone from Paleozoic seas.",
     "identify": "Three-lobed body, compound eyes, segmented."},
    
    {"name": "Ammonite", "scientific": "Ammonoidea", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Ammonite_fossil.jpg/320px-Ammonite_fossil.jpg",
     "period": "Devonian-Cretaceous (400-66 MYA)",
     "description": "Coiled cephalopod related to squid. Complex suture patterns.",
     "how_to_find": "Found in marine limestone and shale.",
     "identify": "Spiral shell with chambers, complex suture lines visible."},
    
    {"name": "Megalodon Tooth", "scientific": "Otodus megalodon", "rarity": "epic", "points": 800,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Megalodon_tooth.jpg/320px-Megalodon_tooth.jpg",
     "period": "Miocene-Pliocene (23-3 MYA)",
     "description": "Giant shark tooth up to 7 inches! Meg was 50+ feet long.",
     "how_to_find": "Found in coastal areas, rivers, dive sites. Florida, Carolinas, Morocco.",
     "identify": "HUGE (3-7 inches), triangular, serrated edges, V-shaped root."},
    
    {"name": "T. rex Tooth", "scientific": "Tyrannosaurus rex", "rarity": "legendary", "points": 5000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Tyrannosaurus_tooth.jpg/320px-Tyrannosaurus_tooth.jpg",
     "period": "Late Cretaceous (68-66 MYA)",
     "description": "Tooth from the king of dinosaurs! Banana-sized killing teeth.",
     "how_to_find": "Hell Creek Formation - Montana, Wyoming, South Dakota.",
     "identify": "Large (4-12 inches), thick, serrated, D-shaped cross section."},
    
    {"name": "Dinosaur Bone", "scientific": "Dinosauria", "rarity": "rare", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Dinosaur_bone.jpg/320px-Dinosaur_bone.jpg",
     "period": "Triassic-Cretaceous (230-66 MYA)",
     "description": "Mineralized dinosaur bone. Internal spongy structure visible.",
     "how_to_find": "Morrison Formation (Western USA), Argentina, Mongolia.",
     "identify": "Spongy internal texture, heavy, often has cell structure visible."},
    
    {"name": "Raptor Claw", "scientific": "Dromaeosauridae", "rarity": "epic", "points": 1500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Dromaeosaur_claw.jpg/320px-Dromaeosaur_claw.jpg",
     "period": "Cretaceous (145-66 MYA)",
     "description": "Curved killing claw from velociraptor-type dinosaur.",
     "how_to_find": "Found in Cretaceous formations. Mongolia, Western USA.",
     "identify": "Curved, pointed, groove on side, 2-6 inches."},
    
    {"name": "Shark Tooth", "scientific": "Various", "rarity": "common", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Shark_tooth.jpg/320px-Shark_tooth.jpg",
     "period": "Devonian-Present (400 MYA - today)",
     "description": "Sharks constantly shed teeth - common fossils!",
     "how_to_find": "Search beaches, rivers, coastal areas. Florida, Maryland, Morocco.",
     "identify": "Triangular, pointed, often dark colored from minerals."},
    
    {"name": "Crinoid Stem", "scientific": "Crinoidea", "rarity": "common", "points": 30,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Crinoid_stem.jpg/320px-Crinoid_stem.jpg",
     "period": "Ordovician-Present (480 MYA - today)",
     "description": "Sea lily stem segments - round discs with star-shaped hole.",
     "how_to_find": "Very common in Midwest limestone. Called 'Indian beads'.",
     "identify": "Round disc-shaped segments, star or round hole in center."},
    
    {"name": "Brachiopod", "scientific": "Brachiopoda", "rarity": "common", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Brachiopod_Terebratula.jpg/320px-Brachiopod_Terebratula.jpg",
     "period": "Cambrian-Present (540 MYA - today)",
     "description": "Two-shelled marine animal. Symmetry through shell, not between shells.",
     "how_to_find": "Abundant in Paleozoic limestone worldwide.",
     "identify": "Two shells, symmetry through MIDDLE of each shell."},
    
    {"name": "Orthoceras", "scientific": "Orthoceras", "rarity": "common", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Orthoceras_fossil.jpg/320px-Orthoceras_fossil.jpg",
     "period": "Ordovician (485-443 MYA)",
     "description": "Straight-shelled nautiloid with internal chambers.",
     "how_to_find": "Morocco exports tons of polished orthoceras slabs.",
     "identify": "Straight cone shape with visible chambers inside."},
    
    {"name": "Petrified Wood", "scientific": "Silicified wood", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Petrified_wood.jpg/320px-Petrified_wood.jpg",
     "period": "Various (up to 400 MYA)",
     "description": "Ancient wood replaced with silica. Shows tree rings!",
     "how_to_find": "Arizona Petrified Forest, Madagascar, Indonesia.",
     "identify": "Wood grain visible, hard as rock, often colorful."},
    
    {"name": "Amber with Insect", "scientific": "Fossil resin", "rarity": "epic", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Insect_in_amber.jpg/320px-Insect_in_amber.jpg",
     "period": "Cretaceous-Miocene (100-20 MYA)",
     "description": "Ancient insect perfectly preserved in tree resin!",
     "how_to_find": "Dominican Republic, Baltic, Myanmar.",
     "identify": "Transparent yellow-orange, insect visible inside."},
    
    {"name": "Mammoth Tooth", "scientific": "Mammuthus", "rarity": "rare", "points": 400,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Mammoth_tooth.jpg/320px-Mammoth_tooth.jpg",
     "period": "Pleistocene (2.5 MYA - 4,000 years ago)",
     "description": "Massive grinding tooth from woolly mammoth.",
     "how_to_find": "Alaska, Siberia, Great Plains, Florida rivers.",
     "identify": "LARGE (fist-sized+), flat grinding surface with ridges."},
    
    {"name": "Mosasaur Tooth", "scientific": "Mosasaurus", "rarity": "uncommon", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Mosasaur_tooth.jpg/320px-Mosasaur_tooth.jpg",
     "period": "Late Cretaceous (100-66 MYA)",
     "description": "Tooth from giant marine lizard - apex predator of Cretaceous seas.",
     "how_to_find": "Morocco, Kansas, New Jersey chalk deposits.",
     "identify": "Conical, curved, striations on surface, 1-3 inches."},
    
    {"name": "Sabertooth Cat Fang", "scientific": "Smilodon", "rarity": "epic", "points": 1500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Smilodon_fang.jpg/320px-Smilodon_fang.jpg",
     "period": "Pleistocene (2.5 MYA - 10,000 years ago)",
     "description": "Canine tooth up to 11 inches long!",
     "how_to_find": "La Brea Tar Pits (California), Florida.",
     "identify": "Long curved fang, serrated edges, flat cross-section."},
]

# Badge definitions
BADGES = {
    "first_find": {"name": "First Discovery", "icon": "🌟", "desc": "Found your first specimen", "points": 100},
    "ten_finds": {"name": "Explorer", "icon": "🧭", "desc": "Found 10 specimens", "points": 250},
    "fifty_finds": {"name": "Field Scientist", "icon": "🔬", "desc": "Found 50 specimens", "points": 500},
    "mineral_hunter": {"name": "Rock Hound", "icon": "💎", "desc": "Found 10 minerals", "points": 200},
    "fossil_hunter": {"name": "Paleontologist", "icon": "🦴", "desc": "Found 10 fossils", "points": 300},
    "rare_find": {"name": "Rare Discovery", "icon": "💜", "desc": "Found a rare specimen", "points": 200},
    "epic_find": {"name": "Epic Discovery", "icon": "🟣", "desc": "Found an epic specimen", "points": 500},
    "legendary_find": {"name": "Legendary!", "icon": "🌈", "desc": "Found a legendary specimen", "points": 2000},
    "trex": {"name": "T-Rex Hunter", "icon": "🦖", "desc": "Found T-Rex remains!", "points": 5000},
    "megalodon": {"name": "Megalodon Hunter", "icon": "🦈", "desc": "Found Megalodon tooth!", "points": 3000},
    "gold": {"name": "Gold Fever", "icon": "🥇", "desc": "Found gold!", "points": 5000},
}

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
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["user_id"]).execute()
    found = [f["item_name"] for f in (my_finds.data or [])]
    return render_template("game.html", game=game_data.data[0], players=players.data, user_name=session.get("name",""), minerals=MINERALS, fossils=FOSSILS, found=found)

@app.route("/reference")
def reference():
    return render_template("reference.html", minerals=MINERALS, fossils=FOSSILS)

@app.route("/api/species")
def api_species():
    return jsonify({"minerals": MINERALS, "fossils": FOSSILS})

@app.route("/api/identify", methods=["POST"])
@login_required  
def api_identify():
    data = request.json
    image = data.get("image")
    user_guess = data.get("guess", "").lower()
    
    if not image:
        return jsonify({"error": "No image"}), 400
    
    results = []
    
    # First check local database for minerals/fossils
    all_items = MINERALS + FOSSILS
    for item in all_items:
        if user_guess and user_guess in item["name"].lower():
            results.insert(0, {
                "name": item["name"],
                "scientific_name": item.get("scientific", item.get("period", "")),
                "score": 90,
                "photo": item["photo"],
                "category": "Minerals" if item in MINERALS else "Fossils",
                "points": item["points"],
                "rarity": item["rarity"],
                "description": item["description"],
                "identify": item.get("identify", ""),
            })
    
    # Then try iNaturalist for living things
    try:
        if ',' in image:
            img_data = image.split(',')[1]
        else:
            img_data = image
        
        files = {'image': ('photo.jpg', base64.b64decode(img_data), 'image/jpeg')}
        r = requests.post("https://api.inaturalist.org/v1/computervision/score_image", files=files, timeout=15)
        
        for res in r.json().get("results", [])[:8]:
            taxon = res.get("taxon", {})
            score = res.get("combined_score", 0)
            photo = taxon.get("default_photo", {})
            
            # Determine rarity based on score
            if score > 0.9: rarity, pts = "common", 50
            elif score > 0.7: rarity, pts = "uncommon", 100
            elif score > 0.5: rarity, pts = "rare", 150
            else: rarity, pts = "epic", 200
            
            results.append({
                "name": taxon.get("preferred_common_name") or taxon.get("name", "Unknown"),
                "scientific_name": taxon.get("name", ""),
                "score": round(score * 100, 1),
                "photo": photo.get("medium_url", ""),
                "category": taxon.get("iconic_taxon_name", "Unknown"),
                "points": pts,
                "rarity": rarity,
            })
    except Exception as e:
        print(f"iNat error: {e}")
    
    # Calculate photo quality score
    try:
        if ',' in image:
            img_bytes = base64.b64decode(image.split(',')[1])
        else:
            img_bytes = base64.b64decode(image)
        size_kb = len(img_bytes) / 1024
        photo_score = min(100, max(30, 50 + (size_kb - 100) / 10))
    except:
        photo_score = 50
    
    return jsonify({"results": results[:10], "photo_score": int(photo_score)})

@app.route("/api/confirm_find", methods=["POST"])
@login_required
def api_confirm_find():
    data = request.json
    name = data.get("name")
    points = data.get("points", 50)
    rarity = data.get("rarity", "common")
    photo_score = data.get("photo_score", 50)
    category = data.get("category", "unknown")
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    user_id = session.get("user_id")
    
    if not game_code:
        return jsonify({"error": "Not in game"})
    
    # Check duplicate
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", user_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "duplicate": True})
    
    # Apply photo quality bonus
    if photo_score >= 90:
        points = int(points * 2.0)
        style = "MASTERPIECE! 2x"
    elif photo_score >= 75:
        points = int(points * 1.5)
        style = "Great Shot! 1.5x"
    elif photo_score >= 50:
        points = int(points * 1.2)
        style = "Nice Photo 1.2x"
    else:
        style = "Photo Logged"
    
    # Save find
    supabase.table("finds").insert({
        "user_id": user_id, 
        "game_code": game_code, 
        "item_name": name, 
        "category": category,
        "points": points,
        "style_score": photo_score
    }).execute()
    
    # Update player score
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = (player.data[0]["score"] if player.data else 0) + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    # Check for badges
    badges_earned = []
    all_finds = supabase.table("finds").select("*").eq("user_id", user_id).execute()
    total = len(all_finds.data or [])
    
    # Milestone badges
    if total == 1:
        badges_earned.append(BADGES["first_find"])
    elif total == 10:
        badges_earned.append(BADGES["ten_finds"])
    elif total == 50:
        badges_earned.append(BADGES["fifty_finds"])
    
    # Rarity badges
    if rarity == "rare":
        badges_earned.append(BADGES["rare_find"])
    elif rarity == "epic":
        badges_earned.append(BADGES["epic_find"])
    elif rarity == "legendary":
        badges_earned.append(BADGES["legendary_find"])
    
    # Special find badges
    name_lower = name.lower()
    if "t. rex" in name_lower or "tyrannosaurus" in name_lower:
        badges_earned.append(BADGES["trex"])
    if "megalodon" in name_lower:
        badges_earned.append(BADGES["megalodon"])
    if "gold" in name_lower:
        badges_earned.append(BADGES["gold"])
    
    return jsonify({
        "success": True, 
        "points": points, 
        "new_score": new_score, 
        "style": style,
        "badges": badges_earned
    })

@app.route("/api/leaderboard/<code>")
def api_leaderboard(code):
    players = supabase.table("players").select("name,score").eq("game_code", code).order("score", desc=True).execute()
    return jsonify(players.data or [])

if __name__ == "__main__":
    app.run(debug=True, port=5001)
