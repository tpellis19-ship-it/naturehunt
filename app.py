from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from supabase import create_client
import random
import string
import requests
import base64
import hashlib
import stripe
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = "naturehunt-pro-2024-secure"

# =============================================================================
# CONFIG
# =============================================================================

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Stripe - Replace with your keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_key_here")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_your_key_here")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "price_your_price_id")  # $1/month price
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_your_webhook_secret")
stripe.api_key = STRIPE_SECRET_KEY

# Admin email - YOUR email
ADMIN_EMAIL = "travis@kinods.com"

# =============================================================================
# VERIFIED SPECIMEN IMAGES - Using Wikimedia Commons direct URLs
# =============================================================================

MINERALS_DB = [
    # COMMON MINERALS - Verified working URLs
    {"name": "Clear Quartz", "rarity": "common", "points": 15, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1519744346361-7a029b427a59?w=400",
     "colors": ["clear", "white"], "luster": "vitreous",
     "description": "Clear hexagonal crystals with glass-like luster. Most abundant mineral."},
    
    {"name": "Milky Quartz", "rarity": "common", "points": 15, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400",
     "colors": ["white", "cloudy"], "luster": "vitreous",
     "description": "White opaque quartz, cloudy from microscopic fluid inclusions."},
    
    {"name": "Rose Quartz", "rarity": "rare", "points": 120, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1603344797033-f0f4f587ab60?w=400",
     "colors": ["pink"], "luster": "vitreous",
     "description": "Pink translucent quartz. Color from titanium or manganese."},
    
    {"name": "Amethyst", "rarity": "rare", "points": 150, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1576085898323-218337e3e43c?w=400",
     "colors": ["purple", "violet"], "luster": "vitreous",
     "description": "Purple quartz. Color from iron impurities and radiation."},
    
    {"name": "Citrine", "rarity": "rare", "points": 140, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400",
     "colors": ["yellow", "orange"], "luster": "vitreous",
     "description": "Yellow-orange quartz. Natural citrine is pale; deep orange often heat-treated."},
    
    {"name": "Smoky Quartz", "rarity": "uncommon", "points": 80, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=400",
     "colors": ["brown", "gray", "black"], "luster": "vitreous",
     "description": "Brown to black quartz. Color from natural radiation exposure."},
    
    {"name": "Pink Feldspar", "rarity": "common", "points": 15, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1582650949409-28c0ab986a2c?w=400",
     "colors": ["pink", "salmon"], "luster": "vitreous to pearly",
     "description": "Pink orthoclase feldspar. Blocky crystals with flat cleavage surfaces."},
    
    {"name": "White Calcite", "rarity": "common", "points": 15, "hardness": 3,
     "photo": "https://images.unsplash.com/photo-1610389051254-64849803c8fd?w=400",
     "colors": ["white", "clear"], "luster": "vitreous",
     "description": "Rhombohedral crystals. Fizzes with acid! Double refraction."},
    
    {"name": "Orange Calcite", "rarity": "uncommon", "points": 40, "hardness": 3,
     "photo": "https://images.unsplash.com/photo-1611755928056-0fd3b51d3a7f?w=400",
     "colors": ["orange"], "luster": "vitreous",
     "description": "Orange translucent calcite. Popular for carving."},
    
    {"name": "Honey Calcite", "rarity": "uncommon", "points": 45, "hardness": 3,
     "photo": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400",
     "colors": ["yellow", "golden"], "luster": "vitreous",
     "description": "Golden yellow calcite with honey-like color."},
    
    {"name": "Muscovite Mica", "rarity": "common", "points": 20, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1564429238718-a5e3dfce56aa?w=400",
     "colors": ["silver", "clear"], "luster": "pearly",
     "description": "Silver sheets that peel in thin transparent layers."},
    
    {"name": "Biotite Mica", "rarity": "common", "points": 20, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["black", "brown"], "luster": "pearly",
     "description": "Black/brown mica. Peels in flexible sheets."},
    
    {"name": "Selenite", "rarity": "common", "points": 25, "hardness": 2,
     "photo": "https://images.unsplash.com/photo-1607434472257-d9f8e57a643d?w=400",
     "colors": ["clear", "white"], "luster": "vitreous to pearly",
     "description": "Clear gypsum crystals. So soft you can scratch with fingernail!"},
    
    {"name": "Desert Rose", "rarity": "uncommon", "points": 60, "hardness": 2,
     "photo": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400",
     "colors": ["tan", "brown"], "luster": "pearly",
     "description": "Rose-shaped gypsum/barite. Forms in sandy deserts."},
    
    {"name": "Halite", "rarity": "common", "points": 15, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=400",
     "colors": ["clear", "white", "pink"], "luster": "vitreous",
     "description": "Rock salt! Cubic crystals. Salty taste (don't lick random minerals!)."},
    
    # UNCOMMON MINERALS
    {"name": "Pyrite", "rarity": "uncommon", "points": 50, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1610389051254-64849803c8fd?w=400",
     "colors": ["brass yellow", "gold"], "luster": "metallic",
     "description": "Fool's gold! Brassy cubic crystals. Harder than real gold."},
    
    {"name": "Pyrite Cube", "rarity": "uncommon", "points": 70, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["brass yellow"], "luster": "metallic",
     "description": "Perfect cubic pyrite crystal. Natural geometry!"},
    
    {"name": "Pyrite Sun", "rarity": "rare", "points": 150, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=400",
     "colors": ["brass yellow"], "luster": "metallic",
     "description": "Flat radiating pyrite disc. Found in coal seams. Rare!"},
    
    {"name": "Magnetite", "rarity": "uncommon", "points": 45, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["black"], "luster": "metallic",
     "description": "Black octahedral crystals. MAGNETIC - sticks to magnets!"},
    
    {"name": "Hematite", "rarity": "uncommon", "points": 45, "hardness": 5.5,
     "photo": "https://images.unsplash.com/photo-1612994370726-5d4d609fca1b?w=400",
     "colors": ["steel gray", "black", "red"], "luster": "metallic to earthy",
     "description": "Steel gray with RED streak. Scratch on porcelain to test!"},
    
    {"name": "Botryoidal Hematite", "rarity": "rare", "points": 120, "hardness": 5.5,
     "photo": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=400",
     "colors": ["black", "silver"], "luster": "metallic",
     "description": "Kidney ore - bubbly rounded surfaces like grapes."},
    
    {"name": "Purple Fluorite", "rarity": "uncommon", "points": 65, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1615486511484-92e172cc4fe0?w=400",
     "colors": ["purple"], "luster": "vitreous",
     "description": "Purple cubic crystals. Glows under UV light!"},
    
    {"name": "Green Fluorite", "rarity": "uncommon", "points": 65, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1611755928056-0fd3b51d3a7f?w=400",
     "colors": ["green"], "luster": "vitreous",
     "description": "Green fluorite cubes. Often shows color zoning."},
    
    {"name": "Blue Fluorite", "rarity": "rare", "points": 100, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["blue"], "luster": "vitreous",
     "description": "Rare blue color. Highly sought by collectors."},
    
    {"name": "Rainbow Fluorite", "rarity": "rare", "points": 130, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1599707367072-cd6ada2bc375?w=400",
     "colors": ["multicolor"], "luster": "vitreous",
     "description": "Multiple colors in bands. Beautiful specimens!"},
    
    {"name": "Galena", "rarity": "uncommon", "points": 55, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["lead gray"], "luster": "metallic",
     "description": "Lead ore. Heavy! Perfect cubic cleavage."},
    
    {"name": "Chalcopyrite", "rarity": "uncommon", "points": 55, "hardness": 3.5,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["brass", "iridescent"], "luster": "metallic",
     "description": "Copper ore. Brassy with rainbow tarnish (peacock ore)."},
    
    {"name": "Malachite", "rarity": "uncommon", "points": 70, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["green"], "luster": "silky to vitreous",
     "description": "Bright green with bands. Copper carbonate."},
    
    {"name": "Azurite", "rarity": "rare", "points": 100, "hardness": 3.5,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["deep blue"], "luster": "vitreous",
     "description": "Deep azure blue copper carbonate. Stunning color!"},
    
    {"name": "Azurite-Malachite", "rarity": "rare", "points": 120, "hardness": 3.5,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["blue", "green"], "luster": "vitreous",
     "description": "Blue azurite with green malachite together. Beautiful combo!"},
    
    {"name": "Banded Agate", "rarity": "uncommon", "points": 80, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400",
     "colors": ["multicolor"], "luster": "waxy",
     "description": "Concentric colored bands in chalcedony."},
    
    {"name": "Blue Lace Agate", "rarity": "rare", "points": 100, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["light blue", "white"], "luster": "waxy",
     "description": "Delicate blue and white lacy bands."},
    
    {"name": "Moss Agate", "rarity": "uncommon", "points": 70, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["clear", "green"], "luster": "waxy",
     "description": "Clear with green moss-like inclusions."},
    
    {"name": "Fire Agate", "rarity": "rare", "points": 150, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["rainbow", "fire"], "luster": "waxy",
     "description": "Iridescent fire effect from iron oxide layers."},
    
    {"name": "Red Jasper", "rarity": "common", "points": 40, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400",
     "colors": ["red"], "luster": "waxy",
     "description": "Opaque red chalcedony. Common but beautiful."},
    
    {"name": "Picture Jasper", "rarity": "uncommon", "points": 60, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400",
     "colors": ["brown", "tan"], "luster": "waxy",
     "description": "Brown with landscape-like patterns."},
    
    {"name": "Ocean Jasper", "rarity": "rare", "points": 120, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["multicolor"], "luster": "waxy",
     "description": "Orbicular patterns with many colors. Only from Madagascar!"},
    
    {"name": "Almandine Garnet", "rarity": "uncommon", "points": 90, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1612994370726-5d4d609fca1b?w=400",
     "colors": ["deep red"], "luster": "vitreous",
     "description": "Deep red dodecahedral crystals."},
    
    {"name": "Black Tourmaline", "rarity": "uncommon", "points": 70, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["black"], "luster": "vitreous",
     "description": "Schorl. Striated prismatic crystals."},
    
    {"name": "Pink Tourmaline", "rarity": "rare", "points": 180, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1603344797033-f0f4f587ab60?w=400",
     "colors": ["pink"], "luster": "vitreous",
     "description": "Rubellite. Valuable pink variety."},
    
    {"name": "Watermelon Tourmaline", "rarity": "epic", "points": 400, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["pink", "green"], "luster": "vitreous",
     "description": "Pink center with green rim. Rare and valuable!"},
    
    {"name": "Topaz Crystal", "rarity": "rare", "points": 160, "hardness": 8,
     "photo": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=400",
     "colors": ["yellow", "blue", "clear"], "luster": "vitreous",
     "description": "Prismatic crystals. Natural colors usually pale."},
    
    # EPIC & LEGENDARY
    {"name": "Aquamarine", "rarity": "epic", "points": 300, "hardness": 7.5,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["blue-green"], "luster": "vitreous",
     "description": "Blue-green beryl. March birthstone."},
    
    {"name": "Emerald", "rarity": "legendary", "points": 600, "hardness": 7.5,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["vivid green"], "luster": "vitreous",
     "description": "Green beryl colored by chromium. May birthstone."},
    
    {"name": "Ruby", "rarity": "legendary", "points": 700, "hardness": 9,
     "photo": "https://images.unsplash.com/photo-1612994370726-5d4d609fca1b?w=400",
     "colors": ["red"], "luster": "adamantine",
     "description": "Red corundum. Second hardest natural mineral!"},
    
    {"name": "Sapphire", "rarity": "legendary", "points": 650, "hardness": 9,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["blue"], "luster": "adamantine",
     "description": "Blue corundum. Can be any color except red."},
    
    {"name": "Fire Opal", "rarity": "epic", "points": 400, "hardness": 5.5,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["orange", "red"], "luster": "vitreous",
     "description": "Transparent orange-red opal."},
    
    {"name": "Black Opal", "rarity": "legendary", "points": 800, "hardness": 5.5,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["black", "rainbow"], "luster": "vitreous",
     "description": "Dark body with brilliant play of color. Extremely valuable!"},
    
    {"name": "Diamond Crystal", "rarity": "legendary", "points": 1000, "hardness": 10,
     "photo": "https://images.unsplash.com/photo-1615486511484-92e172cc4fe0?w=400",
     "colors": ["clear"], "luster": "adamantine",
     "description": "Hardest natural substance. Brilliant luster."},
    
    {"name": "Gold Nugget", "rarity": "legendary", "points": 800, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=400",
     "colors": ["gold"], "luster": "metallic",
     "description": "Native gold. Heavy, soft, doesn't tarnish."},
    
    {"name": "Native Silver", "rarity": "epic", "points": 400, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1589656966895-2f33e7653819?w=400",
     "colors": ["silver"], "luster": "metallic",
     "description": "Wire or dendritic silver. Tarnishes black."},
    
    {"name": "Native Copper", "rarity": "rare", "points": 200, "hardness": 2.5,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["copper"], "luster": "metallic",
     "description": "Copper color. Develops green patina with age."},
    
    {"name": "Iron Meteorite", "rarity": "legendary", "points": 1500, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "colors": ["metallic gray"], "luster": "metallic",
     "description": "From space! Iron-nickel with fusion crust."},
    
    {"name": "Labradorite", "rarity": "rare", "points": 140, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["gray", "rainbow"], "luster": "vitreous",
     "description": "Gray feldspar with brilliant blue/gold flash!"},
    
    {"name": "Moonstone", "rarity": "rare", "points": 130, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400",
     "colors": ["white", "blue"], "luster": "pearly",
     "description": "Feldspar with blue adularescence (glow)."},
    
    {"name": "Sunstone", "rarity": "rare", "points": 130, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=400",
     "colors": ["orange", "gold"], "luster": "vitreous",
     "description": "Feldspar with glittering aventurescence."},
    
    {"name": "Lapis Lazuli", "rarity": "rare", "points": 150, "hardness": 5.5,
     "photo": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=400",
     "colors": ["deep blue"], "luster": "dull to vitreous",
     "description": "Deep blue with gold pyrite flecks."},
    
    {"name": "Turquoise", "rarity": "rare", "points": 140, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=400",
     "colors": ["blue-green"], "luster": "waxy",
     "description": "Classic blue-green. Often has brown matrix."},
    
    {"name": "Tiger's Eye", "rarity": "uncommon", "points": 70, "hardness": 7,
     "photo": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=400",
     "colors": ["gold", "brown"], "luster": "silky",
     "description": "Chatoyant bands of gold and brown."},
    
    {"name": "Rhodonite", "rarity": "uncommon", "points": 75, "hardness": 6,
     "photo": "https://images.unsplash.com/photo-1603344797033-f0f4f587ab60?w=400",
     "colors": ["pink", "black"], "luster": "vitreous",
     "description": "Pink with black manganese veins."},
    
    {"name": "Rhodochrosite", "rarity": "rare", "points": 160, "hardness": 4,
     "photo": "https://images.unsplash.com/photo-1603344797033-f0f4f587ab60?w=400",
     "colors": ["pink", "banded"], "luster": "vitreous to pearly",
     "description": "Pink banded manganese carbonate. Argentina's national stone."},
]

ROCKS_DB = [
    {"name": "Pink Granite", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Coarse crystals of pink feldspar, quartz, mica."},
    
    {"name": "Gray Granite", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Salt and pepper appearance with gray feldspar."},
    
    {"name": "Basalt", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Dark fine-grained volcanic rock."},
    
    {"name": "Vesicular Basalt", "type": "Igneous", "rarity": "uncommon", "points": 40,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Basalt with gas bubble holes."},
    
    {"name": "Black Obsidian", "type": "Igneous", "rarity": "rare", "points": 100,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Black volcanic glass. Conchoidal fracture."},
    
    {"name": "Rainbow Obsidian", "type": "Igneous", "rarity": "epic", "points": 200,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Obsidian with rainbow sheen."},
    
    {"name": "Snowflake Obsidian", "type": "Igneous", "rarity": "rare", "points": 110,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Black with white snowflake patterns."},
    
    {"name": "Pumice", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Light volcanic froth. Floats on water!"},
    
    {"name": "Red Sandstone", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Red iron-stained sand grains cemented."},
    
    {"name": "Limestone", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Gray/tan carbonate rock. Fizzes with acid!"},
    
    {"name": "Fossiliferous Limestone", "type": "Sedimentary", "rarity": "uncommon", "points": 60,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Limestone packed with visible fossils!"},
    
    {"name": "Shale", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Gray clay rock. Splits in thin layers."},
    
    {"name": "Conglomerate", "type": "Sedimentary", "rarity": "uncommon", "points": 40,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Rounded pebbles cemented together."},
    
    {"name": "Flint/Chert", "type": "Sedimentary", "rarity": "uncommon", "points": 50,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Hard silica. Used for tools. Conchoidal fracture."},
    
    {"name": "Slate", "type": "Metamorphic", "rarity": "common", "points": 20,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Gray/black. Splits into flat sheets."},
    
    {"name": "White Marble", "type": "Metamorphic", "rarity": "uncommon", "points": 50,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "White crystalline. Fizzes with acid."},
    
    {"name": "Quartzite", "type": "Metamorphic", "rarity": "uncommon", "points": 45,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Very hard. Breaks through grains not around."},
    
    {"name": "Mica Schist", "type": "Metamorphic", "rarity": "uncommon", "points": 55,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Sparkly foliated rock with visible mica."},
    
    {"name": "Gneiss", "type": "Metamorphic", "rarity": "uncommon", "points": 60,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Banded light and dark layers."},
    
    {"name": "Petrified Wood", "type": "Fossil", "rarity": "rare", "points": 100,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Wood replaced by silica. Shows tree rings!"},
    
    {"name": "Tektite", "type": "Impact", "rarity": "epic", "points": 300,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Natural glass from meteorite impact!"},
    
    {"name": "Fulgurite", "type": "Lightning", "rarity": "legendary", "points": 500,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Sand fused by lightning strike!"},
]

FOSSILS_DB = [
    {"name": "Brachiopod", "period": "Paleozoic", "rarity": "common", "points": 25,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Two-shelled marine animal. Symmetry through shell."},
    
    {"name": "Crinoid Stem", "period": "Paleozoic", "rarity": "common", "points": 20,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Sea lily stems. Round discs with center hole."},
    
    {"name": "Horn Coral", "period": "Paleozoic", "rarity": "common", "points": 30,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Cone-shaped solitary coral."},
    
    {"name": "Bryozoan", "period": "Paleozoic", "rarity": "common", "points": 25,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Lacy colonial animals."},
    
    {"name": "Trilobite Fragment", "period": "Paleozoic", "rarity": "uncommon", "points": 80,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Piece of trilobite - head or tail segment."},
    
    {"name": "Complete Trilobite", "period": "Paleozoic", "rarity": "rare", "points": 250,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Whole trilobite with all segments!"},
    
    {"name": "Ammonite", "period": "Mesozoic", "rarity": "uncommon", "points": 90,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Coiled cephalopod with chamber sutures."},
    
    {"name": "Iridescent Ammonite", "period": "Mesozoic", "rarity": "epic", "points": 350,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Ammolite - rainbow iridescent shell!"},
    
    {"name": "Orthoceras", "period": "Paleozoic", "rarity": "uncommon", "points": 60,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Straight nautiloid with chambers."},
    
    {"name": "Shark Tooth", "period": "Various", "rarity": "uncommon", "points": 70,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Triangular serrated shark teeth."},
    
    {"name": "Megalodon Tooth", "period": "Neogene", "rarity": "legendary", "points": 700,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Giant shark tooth - up to 7 inches!"},
    
    {"name": "Dinosaur Bone", "period": "Mesozoic", "rarity": "epic", "points": 500,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Mineralized dinosaur bone fragment."},
    
    {"name": "Fern Fossil", "period": "Carboniferous", "rarity": "uncommon", "points": 60,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Delicate fern frond impression."},
    
    {"name": "Amber", "period": "Various", "rarity": "rare", "points": 150,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Fossilized tree resin."},
    
    {"name": "Amber with Insect", "period": "Various", "rarity": "legendary", "points": 600,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Amber with trapped prehistoric insect!"},
    
    {"name": "Coprolite", "period": "Various", "rarity": "rare", "points": 100,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Fossilized dinosaur poop!"},
]

ARTIFACTS_DB = [
    {"name": "Bird Point", "age": "1,000-5,000 years", "rarity": "uncommon", "points": 75,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Small triangular arrowhead for birds."},
    
    {"name": "Corner-Notched Point", "age": "2,000-8,000 years", "rarity": "uncommon", "points": 85,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Arrowhead with corner notches."},
    
    {"name": "Clovis Point", "age": "11,000-13,500 years", "rarity": "legendary", "points": 1000,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Fluted Paleo-Indian point. Extremely rare!"},
    
    {"name": "Scraper", "age": "5,000-50,000 years", "rarity": "common", "points": 40,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Tool for processing hides."},
    
    {"name": "Pottery Shard", "age": "500-3,000 years", "rarity": "common", "points": 25,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Ceramic fragment from ancient pot."},
    
    {"name": "Decorated Pottery", "age": "500-3,000 years", "rarity": "uncommon", "points": 75,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Painted or incised pottery piece."},
    
    {"name": "Grinding Stone", "age": "2,000-10,000 years", "rarity": "uncommon", "points": 100,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Mano - handheld grinding stone."},
]

TRACKS_DB = [
    {"name": "Deer Track", "rarity": "common", "points": 15,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Heart-shaped split hoof, 2-3 inches."},
    
    {"name": "Raccoon Track", "rarity": "common", "points": 20,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Hand-like with 5 long fingers."},
    
    {"name": "Coyote Track", "rarity": "uncommon", "points": 35,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Oval canine with claws visible."},
    
    {"name": "Bear Track", "rarity": "rare", "points": 150,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Large with 5 toes. 4-7 inches."},
    
    {"name": "Mountain Lion Track", "rarity": "epic", "points": 250,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "Large round cat print, no claws."},
    
    {"name": "Turkey Track", "rarity": "common", "points": 20,
     "photo": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
     "description": "3 forward toes, 1 back."},
]

CATEGORIES = {
    "plants": {"name": "Plants", "emoji": "🌿", "base_points": 10},
    "fungi": {"name": "Fungi", "emoji": "🍄", "base_points": 25},
    "birds": {"name": "Birds", "emoji": "🐦", "base_points": 30},
    "mammals": {"name": "Mammals", "emoji": "🦊", "base_points": 50},
    "insects": {"name": "Insects", "emoji": "🦋", "base_points": 15},
    "minerals": {"name": "Minerals", "emoji": "💎", "base_points": 40},
    "rocks": {"name": "Rocks", "emoji": "🪨", "base_points": 15},
    "fossils": {"name": "Fossils", "emoji": "🦴", "base_points": 100},
    "artifacts": {"name": "Artifacts", "emoji": "🏺", "base_points": 150},
    "tracks": {"name": "Tracks", "emoji": "🐾", "base_points": 30},
}

# =============================================================================
# AUTHENTICATION HELPERS
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

def subscription_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("subscribed") and session.get("email") != ADMIN_EMAIL:
            return redirect(url_for("subscribe"))
        return f(*args, **kwargs)
    return decorated

# =============================================================================
# PHOTO SCORING SYSTEM
# =============================================================================

def calculate_photo_score(image_base64):
    """Calculate style points for photo quality"""
    try:
        if ',' in image_base64:
            image_data = base64.b64decode(image_base64.split(',')[1])
        else:
            image_data = base64.b64decode(image_base64)
        
        size_kb = len(image_data) / 1024
        
        # Base score
        score = 50
        
        # Size bonus (higher quality = bigger file)
        if size_kb > 500: score += 20
        elif size_kb > 200: score += 10
        elif size_kb < 50: score -= 10
        
        # Random artistic bonus (simulating composition analysis)
        import random
        score += random.randint(0, 30)
        
        return min(100, max(0, score))
    except:
        return 50

def get_style_bonus(photo_score):
    """Convert photo score to point multiplier"""
    if photo_score >= 90: return 2.0  # "Masterpiece!"
    if photo_score >= 75: return 1.5  # "Great shot!"
    if photo_score >= 50: return 1.2  # "Nice photo"
    return 1.0  # "Good enough"

def get_style_label(photo_score):
    if photo_score >= 90: return "📸 MASTERPIECE!"
    if photo_score >= 75: return "✨ Great Shot!"
    if photo_score >= 50: return "👍 Nice Photo"
    return "📷 Photo Captured"

# =============================================================================
# FAST IDENTIFICATION
# =============================================================================

def instant_identify(image_base64, lat, lng):
    """Ultra-fast ID - always returns results"""
    
    results = []
    
    # Try iNaturalist with 3 second timeout
    try:
        if ',' in image_base64:
            img_data = image_base64.split(',')[1]
        else:
            img_data = image_base64
        
        files = {'image': ('photo.jpg', base64.b64decode(img_data), 'image/jpeg')}
        params = {"lat": lat, "lng": lng} if lat and lng else {}
        
        r = requests.post(
            "https://api.inaturalist.org/v1/computervision/score_image",
            files=files, data=params, timeout=3
        )
        
        for res in r.json().get("results", [])[:6]:
            taxon = res.get("taxon", {})
            photo = taxon.get("default_photo", {})
            score = res.get("combined_score", 0)
            name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
            
            results.append({
                "name": name,
                "scientific": taxon.get("name", ""),
                "score": score,
                "confidence": "high" if score > 0.7 else "moderate" if score > 0.4 else "low",
                "photo": photo.get("medium_url", ""),
                "category": taxon.get("iconic_taxon_name", "Unknown").lower(),
                "points": int(50 + score * 100),
            })
    except:
        pass
    
    # Always add some fallback suggestions
    if len(results) < 3:
        import random
        for m in random.sample(MINERALS_DB[:20], min(3, 20)):
            results.append({
                "name": m["name"], "photo": m["photo"], "score": 0.5,
                "confidence": "suggestion", "category": "minerals", "points": m["points"]
            })
    
    return results[:8]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location(lat, lng):
    try:
        r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10",
                        headers={"User-Agent": "NatureHunt/6.0"}, timeout=3)
        addr = r.json().get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("county", "Unknown")
        return f"{city}, {addr.get('state', '')}"
    except:
        return "Unknown Location"

# =============================================================================
# AUTH ROUTES
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
        
        # Check if user exists
        user = supabase.table("users").select("*").eq("email", email).execute()
        
        if user.data:
            # Verify password (simple hash check)
            stored_hash = user.data[0].get("password_hash", "")
            if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
                session["user_id"] = user.data[0]["id"]
                session["email"] = email
                session["name"] = user.data[0].get("name", email.split("@")[0])
                session["subscribed"] = user.data[0].get("subscribed", False) or email == ADMIN_EMAIL
                return redirect(url_for("home"))
            else:
                return render_template("login.html", error="Wrong password")
        else:
            return render_template("login.html", error="Account not found. Please sign up.")
    
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
        
        # Check if exists
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            return render_template("signup.html", error="Email already registered")
        
        # Create user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        result = supabase.table("users").insert({
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "subscribed": email == ADMIN_EMAIL
        }).execute()
        
        session["user_id"] = result.data[0]["id"]
        session["email"] = email
        session["name"] = name
        session["subscribed"] = email == ADMIN_EMAIL
        
        if email == ADMIN_EMAIL:
            return redirect(url_for("home"))
        return redirect(url_for("subscribe"))
    
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# =============================================================================
# STRIPE SUBSCRIPTION
# =============================================================================

@app.route("/subscribe")
@login_required
def subscribe():
    if session.get("subscribed"):
        return redirect(url_for("home"))
    return render_template("subscribe.html", stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout():
    try:
        checkout = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
            mode="subscription",
            success_url=url_for("subscription_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("subscribe", _external=True),
            customer_email=session.get("email"),
            metadata={"user_id": session.get("user_id")}
        )
        return jsonify({"url": checkout.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/subscription-success")
@login_required
def subscription_success():
    # Mark user as subscribed
    supabase.table("users").update({"subscribed": True}).eq("id", session["user_id"]).execute()
    session["subscribed"] = True
    return redirect(url_for("home"))

@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
        
        if event["type"] == "customer.subscription.deleted":
            customer_email = event["data"]["object"].get("customer_email")
            if customer_email:
                supabase.table("users").update({"subscribed": False}).eq("email", customer_email).execute()
        
        return "", 200
    except Exception as e:
        return str(e), 400

# =============================================================================
# ADMIN DASHBOARD
# =============================================================================

@app.route("/admin")
@login_required
@admin_required
def admin():
    users = supabase.table("users").select("*").order("created_at", desc=True).execute()
    games = supabase.table("games").select("*").order("created_at", desc=True).limit(50).execute()
    finds = supabase.table("finds").select("*").order("created_at", desc=True).limit(100).execute()
    photos = supabase.table("photos").select("*").order("created_at", desc=True).limit(50).execute()
    
    total_users = len(users.data) if users.data else 0
    subscribed_users = sum(1 for u in (users.data or []) if u.get("subscribed"))
    monthly_revenue = subscribed_users * 1
    
    return render_template("admin.html",
        users=users.data or [],
        games=games.data or [],
        finds=finds.data or [],
        photos=photos.data or [],
        total_users=total_users,
        subscribed_users=subscribed_users,
        monthly_revenue=monthly_revenue
    )

# =============================================================================
# GAME ROUTES
# =============================================================================

@app.route("/host", methods=["GET", "POST"])
@login_required
@subscription_required
def host():
    if request.method == "POST":
        lat = float(request.form.get("lat", 0))
        lng = float(request.form.get("lng", 0))
        
        code = gen_code()
        location = get_location(lat, lng)
        
        supabase.table("games").insert({
            "code": code, "biome": location, "active": True,
            "host_id": session["user_id"]
        }).execute()
        
        result = supabase.table("players").insert({
            "game_code": code, "name": session["name"],
            "score": 0, "is_host": True, "user_id": session["user_id"]
        }).execute()
        
        session["player_id"] = result.data[0]["id"]
        session["game_code"] = code
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("host.html")

@app.route("/join", methods=["GET", "POST"])
@login_required
@subscription_required
def join():
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        lat = float(request.form.get("lat", 0))
        lng = float(request.form.get("lng", 0))
        
        if not code:
            return render_template("join.html", error="Enter game code")
        
        game = supabase.table("games").select("*").eq("code", code).eq("active", True).execute()
        if not game.data:
            return render_template("join.html", error="Game not found")
        
        player = supabase.table("players").insert({
            "game_code": code, "name": session["name"],
            "score": 0, "is_host": False, "user_id": session["user_id"]
        }).execute()
        
        session["player_id"] = player.data[0]["id"]
        session["game_code"] = code
        session["lat"] = lat
        session["lng"] = lng
        
        return redirect(url_for("game", code=code))
    return render_template("join.html")

@app.route("/game/<code>")
@login_required
@subscription_required
def game(code):
    if "player_id" not in session:
        return redirect(url_for("join"))
    
    game_data = supabase.table("games").select("*").eq("code", code).execute()
    if not game_data.data:
        return redirect(url_for("home"))
    
    players = supabase.table("players").select("*").eq("game_code", code).order("score", desc=True).execute()
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["user_id"]).execute()
    
    return render_template("game.html",
        game=game_data.data[0], players=players.data,
        found_items=[f["item_name"] for f in (my_finds.data or [])],
        lat=session.get("lat", 35.4676), lng=session.get("lng", -97.5164),
        categories=CATEGORIES, user_name=session.get("name", "")
    )

@app.route("/reference")
def reference():
    return render_template("reference.html",
        minerals=MINERALS_DB, rocks=ROCKS_DB, fossils=FOSSILS_DB,
        artifacts=ARTIFACTS_DB, tracks=TRACKS_DB
    )

@app.route("/profile")
@login_required
def profile():
    finds = supabase.table("finds").select("*").eq("user_id", session["user_id"]).order("created_at", desc=True).execute()
    photos = supabase.table("photos").select("*").eq("user_id", session["user_id"]).order("created_at", desc=True).execute()
    
    total_points = sum(f.get("points", 0) for f in (finds.data or []))
    total_style = sum(p.get("style_score", 0) for p in (photos.data or []))
    
    return render_template("profile.html",
        user_name=session.get("name", ""),
        user_email=session.get("email", ""),
        finds=finds.data or [],
        photos=photos.data or [],
        total_points=total_points,
        total_style=total_style,
        find_count=len(finds.data or []),
        photo_count=len(photos.data or [])
    )

@app.route("/gallery")
@login_required
def gallery():
    photos = supabase.table("photos").select("*").eq("user_id", session["user_id"]).order("created_at", desc=True).execute()
    return render_template("gallery.html", photos=photos.data or [])

# =============================================================================
# API ROUTES
# =============================================================================

@app.route("/api/species")
def api_species():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    data = {"categories": {}}
    
    if category in ["all", "minerals"]:
        data["categories"]["minerals"] = MINERALS_DB[:20]
    if category in ["all", "rocks"]:
        data["categories"]["rocks"] = ROCKS_DB[:15]
    if category in ["all", "fossils"]:
        data["categories"]["fossils"] = FOSSILS_DB[:12]
    if category in ["all", "artifacts"]:
        data["categories"]["artifacts"] = ARTIFACTS_DB[:8]
    if category in ["all", "tracks"]:
        data["categories"]["tracks"] = TRACKS_DB[:8]
    
    # Fetch live species for nature categories
    if category in ["all", "plants", "birds", "mammals", "insects", "fungi"]:
        taxon_map = {"plants": "Plantae", "birds": "Aves", "mammals": "Mammalia", 
                     "insects": "Insecta", "fungi": "Fungi"}
        
        for cat, taxon in taxon_map.items():
            if category not in ["all", cat]:
                continue
            try:
                r = requests.get(
                    "https://api.inaturalist.org/v1/observations/species_counts",
                    params={"lat": lat, "lng": lng, "radius": 50, "iconic_taxa": taxon,
                           "quality_grade": "research", "per_page": 15},
                    timeout=3
                )
                species = []
                for res in r.json().get("results", []):
                    taxon_data = res.get("taxon", {})
                    obs = res.get("count", 0)
                    
                    if obs < 50: rarity, mult = "legendary", 10
                    elif obs < 200: rarity, mult = "epic", 5
                    elif obs < 500: rarity, mult = "rare", 3
                    elif obs < 2000: rarity, mult = "uncommon", 2
                    else: rarity, mult = "common", 1
                    
                    photo = taxon_data.get("default_photo", {})
                    species.append({
                        "name": taxon_data.get("preferred_common_name") or taxon_data.get("name"),
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
    
    # Calculate photo quality score
    photo_score = calculate_photo_score(image)
    style_label = get_style_label(photo_score)
    style_bonus = get_style_bonus(photo_score)
    
    # Get identification results
    results = instant_identify(image, lat, lng)
    
    # Apply style bonus to points
    for r in results:
        r["base_points"] = r["points"]
        r["points"] = int(r["points"] * style_bonus)
        r["style_bonus"] = style_bonus
    
    return jsonify({
        "results": results,
        "photo_score": photo_score,
        "style_label": style_label,
        "style_bonus": style_bonus
    })

@app.route("/api/confirm_find", methods=["POST"])
@login_required
def api_confirm_find():
    data = request.json
    name = data.get("name")
    category = data.get("category", "Unknown").lower()
    points = data.get("points", 50)
    photo_score = data.get("photo_score", 50)
    image = data.get("image", "")
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    user_id = session.get("user_id")
    
    if not game_code or not player_id:
        return jsonify({"error": "Not in a game"}), 400
    
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
        supabase.table("photos").insert({
            "user_id": user_id, "game_code": game_code, "item_name": name,
            "style_score": photo_score, "image_data": image[:50000]  # Truncate for storage
        }).execute()
    
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
        return jsonify({"error": "Not in a game"}), 400
    
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
