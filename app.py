from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import os
import random
import string
import requests
from datetime import datetime
import base64
import hashlib

app = Flask(__name__)
app.secret_key = "naturehunt-ultimate-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

INATURALIST_API = "https://api.inaturalist.org/v1"
GBIF_API = "https://api.gbif.org/v1"
PBDB_API = "https://paleobiodb.org/data1.2"

# =============================================================================
# COMPLETE REFERENCE DATABASES WITH HD IMAGES
# =============================================================================

MINERALS_DB = [
    # Common Minerals
    {"name": "Quartz", "formula": "SiO₂", "hardness": 7, "rarity": "common", "points": 15, 
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Quartz%2C_Tibet.jpg/1200px-Quartz%2C_Tibet.jpg",
     "description": "Most abundant mineral on Earth. Clear to milky white, hexagonal crystals.", 
     "colors": ["clear", "white", "pink", "purple", "yellow"], "crystal_system": "Hexagonal"},
    
    {"name": "Feldspar", "formula": "KAlSi₃O₈", "hardness": 6, "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Feldspar-Group-291254.jpg/1200px-Feldspar-Group-291254.jpg",
     "description": "Most abundant mineral group. Pink, white, or gray with cleavage planes.",
     "colors": ["pink", "white", "gray"], "crystal_system": "Monoclinic"},
    
    {"name": "Calcite", "formula": "CaCO₃", "hardness": 3, "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Calcite-20188.jpg/1200px-Calcite-20188.jpg",
     "description": "Reacts with acid. Often clear or white rhombohedral crystals.",
     "colors": ["clear", "white", "yellow", "orange"], "crystal_system": "Trigonal"},
    
    {"name": "Mica (Muscovite)", "formula": "KAl₂(AlSi₃O₁₀)", "hardness": 2.5, "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Muscovite-119650.jpg/1200px-Muscovite-119650.jpg",
     "description": "Thin, flexible, transparent sheets. Peels in layers.",
     "colors": ["clear", "silver", "brown"], "crystal_system": "Monoclinic"},
    
    {"name": "Biotite Mica", "formula": "K(Mg,Fe)₃AlSi₃O₁₀", "hardness": 2.5, "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Biotite-208634.jpg/1200px-Biotite-208634.jpg",
     "description": "Dark mica. Black to dark brown sheets.",
     "colors": ["black", "brown"], "crystal_system": "Monoclinic"},
    
    {"name": "Gypsum", "formula": "CaSO₄·2H₂O", "hardness": 2, "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Gypse_Naica.jpg/1200px-Gypse_Naica.jpg",
     "description": "Very soft. Can be scratched with fingernail. Clear to white.",
     "colors": ["clear", "white"], "crystal_system": "Monoclinic"},
    
    {"name": "Halite (Rock Salt)", "formula": "NaCl", "hardness": 2.5, "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Halite-249324.jpg/1200px-Halite-249324.jpg",
     "description": "Cubic crystals. Tastes salty (don't lick random minerals!).",
     "colors": ["clear", "white", "pink", "blue"], "crystal_system": "Cubic"},
    
    # Uncommon Minerals
    {"name": "Pyrite (Fool's Gold)", "formula": "FeS₂", "hardness": 6, "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Pyrite_3.jpg/1200px-Pyrite_3.jpg",
     "description": "Metallic, brass-yellow cubic crystals. Harder than gold.",
     "colors": ["brass yellow"], "crystal_system": "Cubic"},
    
    {"name": "Magnetite", "formula": "Fe₃O₄", "hardness": 6, "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Magnetite-118736.jpg/1200px-Magnetite-118736.jpg",
     "description": "Magnetic! Black, metallic. Will attract a magnet.",
     "colors": ["black"], "crystal_system": "Cubic"},
    
    {"name": "Hematite", "formula": "Fe₂O₃", "hardness": 5.5, "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Hematite-118647.jpg/1200px-Hematite-118647.jpg",
     "description": "Red streak test. Steel gray to black with red-brown streak.",
     "colors": ["steel gray", "black", "red-brown"], "crystal_system": "Trigonal"},
    
    {"name": "Fluorite", "formula": "CaF₂", "hardness": 4, "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Fluorite_with_Pyrite.jpg/1200px-Fluorite_with_Pyrite.jpg",
     "description": "Glows under UV light! Cubic crystals in many colors.",
     "colors": ["purple", "green", "yellow", "blue", "clear"], "crystal_system": "Cubic"},
    
    {"name": "Galena", "formula": "PbS", "hardness": 2.5, "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Galena-4321.jpg/1200px-Galena-4321.jpg",
     "description": "Lead ore. Heavy, metallic gray cubic crystals.",
     "colors": ["lead gray"], "crystal_system": "Cubic"},
    
    {"name": "Chalcopyrite", "formula": "CuFeS₂", "hardness": 3.5, "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Chalcopyrite-Pyrite-Sphalerite-148028.jpg/1200px-Chalcopyrite-Pyrite-Sphalerite-148028.jpg",
     "description": "Copper ore. Brassy yellow with iridescent tarnish.",
     "colors": ["brass yellow", "iridescent"], "crystal_system": "Tetragonal"},
    
    {"name": "Malachite", "formula": "Cu₂CO₃(OH)₂", "hardness": 4, "rarity": "uncommon", "points": 65,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Malachite-41365.jpg/1200px-Malachite-41365.jpg",
     "description": "Distinctive green banded patterns. Copper ore.",
     "colors": ["green", "banded green"], "crystal_system": "Monoclinic"},
    
    {"name": "Azurite", "formula": "Cu₃(CO₃)₂(OH)₂", "hardness": 3.5, "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Azurite-Malachite-282829.jpg/1200px-Azurite-Malachite-282829.jpg",
     "description": "Deep azure blue. Often found with malachite.",
     "colors": ["deep blue"], "crystal_system": "Monoclinic"},
    
    # Rare Minerals
    {"name": "Amethyst", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Amethyst._Magaliesburg%2C_South_Africa.jpg/1200px-Amethyst._Magaliesburg%2C_South_Africa.jpg",
     "description": "Purple variety of quartz. Deep purple to light lavender.",
     "colors": ["purple", "violet"], "crystal_system": "Hexagonal"},
    
    {"name": "Citrine", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 130,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Citrine_crystal.jpg/1200px-Citrine_crystal.jpg",
     "description": "Yellow variety of quartz. Pale to golden yellow.",
     "colors": ["yellow", "golden"], "crystal_system": "Hexagonal"},
    
    {"name": "Rose Quartz", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Rose_quartz.jpg/1200px-Rose_quartz.jpg",
     "description": "Pink variety of quartz. Usually massive, rarely crystallized.",
     "colors": ["pink", "rose"], "crystal_system": "Hexagonal"},
    
    {"name": "Smoky Quartz", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Quartz%2C_var._Smoky%2C_Minas_Gerais%2C_Brazil.jpg/1200px-Quartz%2C_var._Smoky%2C_Minas_Gerais%2C_Brazil.jpg",
     "description": "Brown to black quartz. Color from natural radiation.",
     "colors": ["brown", "gray", "black"], "crystal_system": "Hexagonal"},
    
    {"name": "Agate", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Agate_bridge.jpg/1200px-Agate_bricks.jpg",
     "description": "Banded chalcedony. Concentric colorful bands.",
     "colors": ["multicolored", "banded"], "crystal_system": "Hexagonal"},
    
    {"name": "Jasper", "formula": "SiO₂", "hardness": 7, "rarity": "rare", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Jaspe_imperial_-_Guadalajara%2C_Mexico.jpg/1200px-Jaspe_imperial.jpg",
     "description": "Opaque chalcedony. Red, brown, yellow patterns.",
     "colors": ["red", "brown", "yellow"], "crystal_system": "Hexagonal"},
    
    {"name": "Garnet", "formula": "X₃Y₂(SiO₄)₃", "hardness": 7, "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Almandine_-_Emerald_Creek%2C_Idaho.jpg/1200px-Almandine_-_Emerald_Creek.jpg",
     "description": "Deep red dodecahedral crystals. January birthstone.",
     "colors": ["red", "orange", "green"], "crystal_system": "Cubic"},
    
    {"name": "Tourmaline", "formula": "Complex borosilicate", "hardness": 7, "rarity": "rare", "points": 140,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Tourmaline-164039.jpg/1200px-Tourmaline-164039.jpg",
     "description": "Prismatic crystals with triangular cross-section. Many colors.",
     "colors": ["black", "pink", "green", "blue"], "crystal_system": "Trigonal"},
    
    {"name": "Topaz", "formula": "Al₂SiO₄(F,OH)₂", "hardness": 8, "rarity": "rare", "points": 160,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Topaz-270054.jpg/1200px-Topaz-270054.jpg",
     "description": "Prismatic crystals. Yellow, blue, or colorless.",
     "colors": ["yellow", "blue", "colorless"], "crystal_system": "Orthorhombic"},
    
    # Epic Minerals
    {"name": "Aquamarine", "formula": "Be₃Al₂Si₆O₁₈", "hardness": 7.5, "rarity": "epic", "points": 250,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Beryl-Quartz-Muscovite-118736.jpg/1200px-Beryl-Quartz-Muscovite-118736.jpg",
     "description": "Blue-green beryl. March birthstone. Hexagonal prisms.",
     "colors": ["blue-green", "aqua"], "crystal_system": "Hexagonal"},
    
    {"name": "Emerald", "formula": "Be₃Al₂Si₆O₁₈", "hardness": 7.5, "rarity": "epic", "points": 350,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Emerald_on_quartz.jpg/1200px-Emerald_on_quartz.jpg",
     "description": "Green beryl. Colored by chromium. May birthstone.",
     "colors": ["green", "vivid green"], "crystal_system": "Hexagonal"},
    
    {"name": "Ruby", "formula": "Al₂O₃", "hardness": 9, "rarity": "epic", "points": 400,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Ruby_-_Winza%2C_Tanzania.jpg/1200px-Ruby_-_Winza.jpg",
     "description": "Red corundum. Second hardest natural mineral.",
     "colors": ["red", "pigeon blood red"], "crystal_system": "Trigonal"},
    
    {"name": "Sapphire", "formula": "Al₂O₃", "hardness": 9, "rarity": "epic", "points": 380,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Corundum-275089.jpg/1200px-Corundum-275089.jpg",
     "description": "Blue corundum. Can be any color except red.",
     "colors": ["blue", "yellow", "pink"], "crystal_system": "Trigonal"},
    
    # Legendary Minerals
    {"name": "Opal", "formula": "SiO₂·nH₂O", "hardness": 5.5, "rarity": "legendary", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Opal_from_Yowah%2C_Queensland%2C_Australia_2.jpg/1200px-Opal_from_Yowah.jpg",
     "description": "Play of color! Hydrated silica with rainbow fire.",
     "colors": ["multicolored", "play of color"], "crystal_system": "Amorphous"},
    
    {"name": "Diamond", "formula": "C", "hardness": 10, "rarity": "legendary", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Rough_diamond.jpg/1200px-Rough_diamond.jpg",
     "description": "Hardest natural substance. Brilliant adamantine luster.",
     "colors": ["colorless", "yellow", "blue"], "crystal_system": "Cubic"},
    
    {"name": "Gold (Native)", "formula": "Au", "hardness": 2.5, "rarity": "legendary", "points": 800,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Gold-native-224709.jpg/1200px-Gold-native-224709.jpg",
     "description": "Metallic yellow. Heavy, malleable, doesn't tarnish.",
     "colors": ["yellow", "golden"], "crystal_system": "Cubic"},
    
    {"name": "Silver (Native)", "formula": "Ag", "hardness": 2.5, "rarity": "legendary", "points": 600,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Native_silver_-_Imiter_mine.jpg/1200px-Native_silver_-_Imiter_mine.jpg",
     "description": "Metallic white. Often tarnishes to black.",
     "colors": ["silver", "white"], "crystal_system": "Cubic"},
    
    {"name": "Copper (Native)", "formula": "Cu", "hardness": 2.5, "rarity": "epic", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/NativeCopperMichigan.jpg/1200px-NativeCopperMichigan.jpg",
     "description": "Metallic copper color. Green patina with age.",
     "colors": ["copper", "red-brown"], "crystal_system": "Cubic"},
    
    {"name": "Meteorite (Iron)", "formula": "Fe-Ni", "hardness": 4, "rarity": "legendary", "points": 1500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Sikhote_Alin_Meteorite.jpg/1200px-Sikhote_Alin_Meteorite.jpg",
     "description": "From space! Iron-nickel alloy. Widmanstätten patterns.",
     "colors": ["metallic", "gray"], "crystal_system": "Cubic"},
]

ROCKS_DB = [
    # Igneous Rocks
    {"name": "Granite", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Granite_Yosemite_P1160483.jpg/1200px-Granite_Yosemite_P1160483.jpg",
     "description": "Coarse-grained intrusive rock. Contains quartz, feldspar, mica.",
     "texture": "Coarse-grained", "minerals": ["quartz", "feldspar", "mica"]},
    
    {"name": "Basalt", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/BasaltUSGOV.jpg/1200px-BasaltUSGOV.jpg",
     "description": "Fine-grained volcanic rock. Dark gray to black.",
     "texture": "Fine-grained", "minerals": ["plagioclase", "pyroxene"]},
    
    {"name": "Rhyolite", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Rhyolite.jpg/1200px-Rhyolite.jpg",
     "description": "Volcanic equivalent of granite. Light colored, fine-grained.",
     "texture": "Fine-grained", "minerals": ["quartz", "feldspar"]},
    
    {"name": "Obsidian", "type": "Igneous", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/ObsidianOregon.jpg/1200px-ObsidianOregon.jpg",
     "description": "Volcanic glass. Black, glassy, conchoidal fracture. Very sharp!",
     "texture": "Glassy", "minerals": ["volcanic glass"]},
    
    {"name": "Pumice", "type": "Igneous", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Pomice.jpg/1200px-Pomice.jpg",
     "description": "Volcanic froth. So light it floats on water!",
     "texture": "Vesicular", "minerals": ["volcanic glass"]},
    
    {"name": "Scoria", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Scoria.jpg/1200px-Scoria.jpg",
     "description": "Vesicular basalt. Red to black with many holes.",
     "texture": "Vesicular", "minerals": ["basaltic glass"]},
    
    {"name": "Diorite", "type": "Igneous", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Diorite.jpg/1200px-Diorite.jpg",
     "description": "Salt and pepper appearance. Intermediate composition.",
     "texture": "Coarse-grained", "minerals": ["plagioclase", "hornblende"]},
    
    {"name": "Gabbro", "type": "Igneous", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Gabbro.jpg/1200px-Gabbro.jpg",
     "description": "Coarse-grained dark rock. Intrusive equivalent of basalt.",
     "texture": "Coarse-grained", "minerals": ["plagioclase", "pyroxene"]},
    
    {"name": "Pegmatite", "type": "Igneous", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Pegmatite.JPG/1200px-Pegmatite.JPG",
     "description": "Very coarse crystals! Often contains rare minerals.",
     "texture": "Very coarse-grained", "minerals": ["quartz", "feldspar", "mica", "tourmaline"]},
    
    # Sedimentary Rocks
    {"name": "Sandstone", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Sandstone%28quartz%29USGOV.jpg/1200px-Sandstone.jpg",
     "description": "Sand-sized grains cemented together. Often red or tan.",
     "texture": "Gritty", "minerals": ["quartz", "feldspar"]},
    
    {"name": "Limestone", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Limestone_with_fossils.jpg/1200px-Limestone_with_fossils.jpg",
     "description": "Made from marine organisms. Reacts with acid (fizzes!).",
     "texture": "Variable", "minerals": ["calcite"]},
    
    {"name": "Shale", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/ShaleUSGOV.jpg/1200px-ShaleUSGOV.jpg",
     "description": "Clay-sized particles. Splits into thin layers.",
     "texture": "Fine-grained", "minerals": ["clay minerals"]},
    
    {"name": "Conglomerate", "type": "Sedimentary", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Conglomerate_on_San_Gorgonio_trail.jpg/1200px-Conglomerate.jpg",
     "description": "Rounded pebbles in a matrix. Like natural concrete.",
     "texture": "Coarse clasts", "minerals": ["various"]},
    
    {"name": "Breccia", "type": "Sedimentary", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Breccia_in_Mosaic_Canyon.jpg/1200px-Breccia.jpg",
     "description": "Angular fragments in matrix. Unlike rounded conglomerate.",
     "texture": "Angular clasts", "minerals": ["various"]},
    
    {"name": "Chert/Flint", "type": "Sedimentary", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Chert.JPG/1200px-Chert.JPG",
     "description": "Microcrystalline quartz. Conchoidal fracture. Used for tools.",
     "texture": "Cryptocrystalline", "minerals": ["quartz"]},
    
    {"name": "Coquina", "type": "Sedimentary", "rarity": "rare", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Coquina.jpg/1200px-Coquina.jpg",
     "description": "Made entirely of shells! Loosely cemented.",
     "texture": "Shell fragments", "minerals": ["calcite", "aragonite"]},
    
    # Metamorphic Rocks
    {"name": "Slate", "type": "Metamorphic", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/SlateUSGOV.jpg/1200px-SlateUSGOV.jpg",
     "description": "Metamorphosed shale. Splits into flat sheets.",
     "texture": "Foliated", "minerals": ["clay minerals", "mica"]},
    
    {"name": "Marble", "type": "Metamorphic", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/MarbleUSGOV.jpg/1200px-MarbleUSGOV.jpg",
     "description": "Metamorphosed limestone. Interlocking calcite crystals.",
     "texture": "Non-foliated", "minerals": ["calcite"]},
    
    {"name": "Quartzite", "type": "Metamorphic", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/QuartziteUSGOV.jpg/1200px-QuartziteUSGOV.jpg",
     "description": "Metamorphosed sandstone. Very hard, breaks through grains.",
     "texture": "Non-foliated", "minerals": ["quartz"]},
    
    {"name": "Schist", "type": "Metamorphic", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Schist_detail.jpg/1200px-Schist_detail.jpg",
     "description": "Medium-grade metamorphic. Visible mica crystals.",
     "texture": "Foliated", "minerals": ["mica", "quartz", "feldspar"]},
    
    {"name": "Gneiss", "type": "Metamorphic", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Gneiss.jpg/1200px-Gneiss.jpg",
     "description": "High-grade metamorphic. Banded light and dark layers.",
     "texture": "Banded", "minerals": ["quartz", "feldspar", "mica"]},
    
    {"name": "Phyllite", "type": "Metamorphic", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Phyllite.jpg/1200px-Phyllite.jpg",
     "description": "Between slate and schist. Silky sheen surface.",
     "texture": "Foliated", "minerals": ["mica", "chlorite"]},
    
    {"name": "Hornfels", "type": "Metamorphic", "rarity": "rare", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Hornfels.jpg/1200px-Hornfels.jpg",
     "description": "Contact metamorphism. Very hard, dense, dark.",
     "texture": "Non-foliated", "minerals": ["various"]},
    
    {"name": "Eclogite", "type": "Metamorphic", "rarity": "epic", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Eclogite_Norway.jpg/1200px-Eclogite_Norway.jpg",
     "description": "High-pressure metamorphic. Green and red (garnet + pyroxene).",
     "texture": "Granular", "minerals": ["garnet", "omphacite"]},
    
    {"name": "Soapstone", "type": "Metamorphic", "rarity": "rare", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Soapstone_from_Venezuela.jpg/1200px-Soapstone.jpg",
     "description": "Made of talc. Soft, soapy feel. Used for carving.",
     "texture": "Soft", "minerals": ["talc"]},
    
    # Special Rocks
    {"name": "Tektite", "type": "Impact", "rarity": "epic", "points": 350,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Tektite-black.jpg/1200px-Tektite-black.jpg",
     "description": "Natural glass from meteorite impact. Usually black.",
     "texture": "Glassy", "minerals": ["impact glass"]},
    
    {"name": "Meteorite (Stony)", "type": "Extraterrestrial", "rarity": "legendary", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/NWA869Meteorite.jpg/1200px-NWA869Meteorite.jpg",
     "description": "Rock from space! Chondrites contain ancient solar system material.",
     "texture": "Variable", "minerals": ["olivine", "pyroxene", "metal"]},
    
    {"name": "Fulgurite", "type": "Lightning", "rarity": "legendary", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Fulgurite.jpg/1200px-Fulgurite.jpg",
     "description": "Lightning-fused sand! Tubular natural glass.",
     "texture": "Glassy tubes", "minerals": ["fused silica"]},
]

FOSSILS_DB = [
    # Invertebrates - Common
    {"name": "Brachiopod", "age_range": "Cambrian-Present", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Spiriferid_brachiopod.jpg/1200px-Spiriferid_brachiopod.jpg",
     "description": "Lamp shells. Two shells, symmetry through shell not between shells.",
     "period": "Paleozoic", "type": "Marine invertebrate"},
    
    {"name": "Crinoid Stem", "age_range": "Ordovician-Present", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Crinoid_columnals.jpg/1200px-Crinoid_columnals.jpg",
     "description": "Sea lily stems. Round discs with hole in center.",
     "period": "Paleozoic", "type": "Echinoderm"},
    
    {"name": "Bryozoan", "age_range": "Ordovician-Present", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Fenestella_fossil.jpg/1200px-Fenestella_fossil.jpg",
     "description": "Colonial animals. Lacy or branching patterns.",
     "period": "Paleozoic", "type": "Colonial invertebrate"},
    
    {"name": "Horn Coral", "age_range": "Ordovician-Permian", "rarity": "common", "points": 30,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Horn_coral.jpg/1200px-Horn_coral.jpg",
     "description": "Solitary coral. Cone-shaped with internal septa.",
     "period": "Paleozoic", "type": "Coral"},
    
    # Invertebrates - Uncommon
    {"name": "Trilobite", "age_range": "Cambrian-Permian", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Elrathia_kingii.jpg/1200px-Elrathia_kingii.jpg",
     "description": "Extinct arthropod. Three-lobed body, compound eyes.",
     "period": "Paleozoic", "type": "Arthropod"},
    
    {"name": "Ammonite", "age_range": "Devonian-Cretaceous", "rarity": "uncommon", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Asteroceras_obtusum.jpg/1200px-Asteroceras_obtusum.jpg",
     "description": "Coiled cephalopod. Complex suture patterns.",
     "period": "Mesozoic", "type": "Cephalopod"},
    
    {"name": "Nautiloid", "age_range": "Cambrian-Present", "rarity": "uncommon", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Nautiloid_fossil.jpg/1200px-Nautiloid_fossil.jpg",
     "description": "Straight or coiled shell. Simple suture patterns.",
     "period": "Paleozoic", "type": "Cephalopod"},
    
    {"name": "Echinoid (Sea Urchin)", "age_range": "Ordovician-Present", "rarity": "uncommon", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Micraster.jpg/1200px-Micraster.jpg",
     "description": "Five-fold symmetry. Round with tubercles for spines.",
     "period": "Various", "type": "Echinoderm"},
    
    {"name": "Belemnite", "age_range": "Jurassic-Cretaceous", "rarity": "uncommon", "points": 85,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Belemnite.jpg/1200px-Belemnite.jpg",
     "description": "Bullet-shaped internal shell. Squid-like animal.",
     "period": "Mesozoic", "type": "Cephalopod"},
    
    # Invertebrates - Rare
    {"name": "Complete Trilobite", "age_range": "Cambrian-Permian", "rarity": "rare", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Trilobite_Eldredgeops.jpg/1200px-Trilobite_Eldredgeops.jpg",
     "description": "Complete specimen with all segments preserved.",
     "period": "Paleozoic", "type": "Arthropod"},
    
    {"name": "Orthoceras", "age_range": "Ordovician-Triassic", "rarity": "uncommon", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Orthoceras.jpg/1200px-Orthoceras.jpg",
     "description": "Straight nautiloid. Often polished and sold.",
     "period": "Paleozoic", "type": "Cephalopod"},
    
    # Vertebrates - Rare
    {"name": "Shark Tooth", "age_range": "Devonian-Present", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Megalodon_tooth.jpg/1200px-Megalodon_tooth.jpg",
     "description": "Triangular, serrated edges. Many species.",
     "period": "Various", "type": "Fish"},
    
    {"name": "Fish Scale", "age_range": "Silurian-Present", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Fish_scales.jpg/1200px-Fish_scales.jpg",
     "description": "Circular or diamond-shaped. Often iridescent.",
     "period": "Various", "type": "Fish"},
    
    {"name": "Fish Vertebra", "age_range": "Silurian-Present", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Fish_vertebra_fossil.jpg/1200px-Fish_vertebra_fossil.jpg",
     "description": "Circular with concave surfaces.",
     "period": "Various", "type": "Fish"},
    
    # Plants - Uncommon
    {"name": "Fern Fossil", "age_range": "Devonian-Present", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Fossil_fern.jpg/1200px-Fossil_fern.jpg",
     "description": "Delicate frond impressions. Common in coal deposits.",
     "period": "Carboniferous", "type": "Plant"},
    
    {"name": "Leaf Impression", "age_range": "Devonian-Present", "rarity": "common", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Fossil_leaf.jpg/1200px-Fossil_leaf.jpg",
     "description": "Preserved leaf shape and venation.",
     "period": "Various", "type": "Plant"},
    
    {"name": "Petrified Wood", "age_range": "Devonian-Present", "rarity": "uncommon", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Petrified_wood_2.jpg/1200px-Petrified_wood_2.jpg",
     "description": "Wood replaced by silica. Preserves cell structure.",
     "period": "Various", "type": "Plant"},
    
    # Epic & Legendary
    {"name": "Dinosaur Bone Fragment", "age_range": "Triassic-Cretaceous", "rarity": "epic", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Dinosaur_bone.jpg/1200px-Dinosaur_bone.jpg",
     "description": "Mineralized bone. Porous texture, often colorful.",
     "period": "Mesozoic", "type": "Reptile"},
    
    {"name": "Dinosaur Tooth", "age_range": "Triassic-Cretaceous", "rarity": "legendary", "points": 800,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/T._rex_tooth.jpg/1200px-T._rex_tooth.jpg",
     "description": "Rare and valuable. Varies by species.",
     "period": "Mesozoic", "type": "Reptile"},
    
    {"name": "Megalodon Tooth", "age_range": "Miocene-Pliocene", "rarity": "legendary", "points": 700,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Megalodon_tooth_2.jpg/1200px-Megalodon_tooth_2.jpg",
     "description": "Massive shark tooth. Up to 7 inches long!",
     "period": "Neogene", "type": "Fish"},
    
    {"name": "Amber with Inclusion", "age_range": "Cretaceous-Present", "rarity": "legendary", "points": 600,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Baltic_amber_with_insect.jpg/1200px-Baltic_amber_with_insect.jpg",
     "description": "Fossilized tree resin with trapped organisms.",
     "period": "Various", "type": "Trace/Insect"},
    
    {"name": "Coprolite", "age_range": "Cambrian-Present", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Coprolite.jpg/1200px-Coprolite.jpg",
     "description": "Fossilized poop! Contains diet information.",
     "period": "Various", "type": "Trace"},
]

ARTIFACTS_DB = [
    # Lithics (Stone Tools)
    {"name": "Arrowhead (Bird Point)", "age": "1,000-5,000 years", "rarity": "uncommon", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Bird_point_arrowhead.jpg/1200px-Bird_point_arrowhead.jpg",
     "description": "Small triangular point for bird hunting. Usually under 1 inch.",
     "material": "Flint/Chert", "region": "North America"},
    
    {"name": "Arrowhead (Corner-Notched)", "age": "2,000-8,000 years", "rarity": "uncommon", "points": 85,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Corner_notched_point.jpg/1200px-Corner_notched_point.jpg",
     "description": "Notches at base corners for hafting.",
     "material": "Flint/Chert", "region": "North America"},
    
    {"name": "Clovis Point", "age": "11,000-13,500 years", "rarity": "legendary", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Clovis_Point.jpg/1200px-Clovis_Point.jpg",
     "description": "Paleo-Indian spear point. Fluted base. Very rare!",
     "material": "Flint/Chert", "region": "North America"},
    
    {"name": "Folsom Point", "age": "9,000-11,000 years", "rarity": "legendary", "points": 900,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Folsom_point.jpg/1200px-Folsom_point.jpg",
     "description": "Delicate fluting nearly to tip. Bison hunting.",
     "material": "Flint/Chert", "region": "North America"},
    
    {"name": "Scraper", "age": "5,000-50,000 years", "rarity": "common", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Scraper_tool.jpg/1200px-Scraper_tool.jpg",
     "description": "Rounded working edge for hide processing.",
     "material": "Flint/Chert", "region": "Worldwide"},
    
    {"name": "Hand Axe", "age": "100,000-1,700,000 years", "rarity": "rare", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/British_Museum_Acheulean_handaxe.jpg/1200px-British_Museum_Acheulean_handaxe.jpg",
     "description": "Teardrop-shaped bifacial tool. Acheulean culture.",
     "material": "Flint/Quartzite", "region": "Africa/Europe"},
    
    {"name": "Obsidian Blade", "age": "3,000-15,000 years", "rarity": "rare", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Obsidian_blade.jpg/1200px-Obsidian_blade.jpg",
     "description": "Volcanic glass. Extremely sharp pressure-flaked blade.",
     "material": "Obsidian", "region": "Various"},
    
    {"name": "Grinding Stone (Mano)", "age": "2,000-10,000 years", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Mano_and_metate.jpg/1200px-Mano_and_metate.jpg",
     "description": "Handheld grinding stone. Rounded from use.",
     "material": "Granite/Sandstone", "region": "Worldwide"},
    
    {"name": "Metate (Grinding Slab)", "age": "2,000-10,000 years", "rarity": "rare", "points": 180,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Metate.jpg/1200px-Metate.jpg",
     "description": "Large concave grinding surface for grain.",
     "material": "Sandstone/Basalt", "region": "Americas"},
    
    # Pottery
    {"name": "Pottery Shard (Plain)", "age": "500-3,000 years", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Pottery_shard.jpg/1200px-Pottery_shard.jpg",
     "description": "Fragment of ceramic vessel. Undecorated.",
     "material": "Ceramic", "region": "Worldwide"},
    
    {"name": "Pottery Shard (Decorated)", "age": "500-3,000 years", "rarity": "uncommon", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Decorated_pottery_shard.jpg/1200px-Decorated_pottery_shard.jpg",
     "description": "Painted or incised decoration visible.",
     "material": "Ceramic", "region": "Worldwide"},
    
    {"name": "Pottery Rim Shard", "age": "500-3,000 years", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Rim_shard.jpg/1200px-Rim_shard.jpg",
     "description": "Edge piece showing vessel form.",
     "material": "Ceramic", "region": "Worldwide"},
    
    # Other Artifacts
    {"name": "Shell Bead", "age": "1,000-10,000 years", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Shell_beads.jpg/1200px-Shell_beads.jpg",
     "description": "Drilled shell ornament. Trade item.",
     "material": "Shell", "region": "Worldwide"},
    
    {"name": "Bone Awl", "age": "1,000-20,000 years", "rarity": "rare", "points": 140,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Bone_awl.jpg/1200px-Bone_awl.jpg",
     "description": "Pointed bone tool for punching holes.",
     "material": "Bone", "region": "Worldwide"},
    
    {"name": "Fire-Cracked Rock", "age": "500-15,000 years", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Fire_cracked_rock.jpg/1200px-Fire_cracked_rock.jpg",
     "description": "Reddened, fractured rock from hearths.",
     "material": "Various", "region": "Worldwide"},
    
    {"name": "Petroglyph", "age": "500-15,000 years", "rarity": "legendary", "points": 400,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Petroglyph_National_Monument.jpg/1200px-Petroglyph_National_Monument.jpg",
     "description": "Rock carving. DO NOT DISTURB - photograph only!",
     "material": "Rock surface", "region": "Worldwide"},
]

TRACKS_DB = [
    {"name": "Deer Track", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Deer_track.jpg/1200px-Deer_track.jpg",
     "description": "Heart-shaped split hoof. 2-3 inches long."},
    
    {"name": "Raccoon Track", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Raccoon_tracks.jpg/1200px-Raccoon_tracks.jpg",
     "description": "Hand-like with 5 long fingers. Like tiny human hands."},
    
    {"name": "Coyote Track", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Coyote_track.jpg/1200px-Coyote_track.jpg",
     "description": "Oval with 4 toes, claws visible. 2-2.5 inches."},
    
    {"name": "Bear Track", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Black_bear_track.jpg/1200px-Black_bear_track.jpg",
     "description": "Large with 5 toes. Rear track human-like. 4-7 inches."},
    
    {"name": "Mountain Lion Track", "rarity": "epic", "points": 250,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Cougar_track.jpg/1200px-Cougar_track.jpg",
     "description": "Large round cat print. No claws visible. 3-4 inches."},
    
    {"name": "Wolf Track", "rarity": "epic", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Wolf_track.jpg/1200px-Wolf_track.jpg",
     "description": "Very large canine print. 4-5 inches. Straight gait."},
    
    {"name": "Beaver Track", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Beaver_tracks.jpg/1200px-Beaver_tracks.jpg",
     "description": "Webbed hind feet. Often with tail drag mark."},
    
    {"name": "Turkey Track", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Turkey_track.jpg/1200px-Turkey_track.jpg",
     "description": "3 forward toes, 1 back. 4-5 inches long."},
    
    {"name": "Snake Trail", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Snake_trail_in_sand.jpg/1200px-Snake_trail_in_sand.jpg",
     "description": "S-curve or sidewinding pattern in sand/dust."},
    
    {"name": "Elk Track", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Elk_track.jpg/1200px-Elk_track.jpg",
     "description": "Like deer but much larger. 4-5 inches. Rounded tips."},
    
    {"name": "Moose Track", "rarity": "epic", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/m/m8/Moose_track.jpg/1200px-Moose_track.jpg",
     "description": "Massive heart-shaped. 5-7 inches. Pointed tips."},
]

# Dangerous species warnings
DANGEROUS_SPECIES = {
    "Death Cap": {"level": "deadly", "warning": "EXTREMELY POISONOUS - causes fatal liver failure. DO NOT TOUCH."},
    "Destroying Angel": {"level": "deadly", "warning": "EXTREMELY POISONOUS - no antidote exists."},
    "Amanita": {"level": "deadly", "warning": "Many Amanita species are deadly poisonous."},
    "Poison Hemlock": {"level": "deadly", "warning": "All parts extremely toxic - can be fatal."},
    "Water Hemlock": {"level": "deadly", "warning": "Most toxic plant in North America."},
    "False Morel": {"level": "dangerous", "warning": "Contains toxins - can be fatal if eaten raw."},
    "Jack O'Lantern": {"level": "dangerous", "warning": "Poisonous - often confused with chanterelles."},
    "Poison Ivy": {"level": "irritant", "warning": "Causes severe skin rash. Leaves of three, let it be."},
    "Poison Oak": {"level": "irritant", "warning": "Causes severe skin rash."},
}

LOOKALIKES = {
    "Chanterelle": ["Jack O'Lantern (poisonous)", "False Chanterelle"],
    "Morel": ["False Morel (poisonous)", "Wrinkled Thimble Cap"],
    "Puffball": ["Immature Death Cap (deadly)", "Earthball (poisonous)"],
    "Hen of the Woods": ["Berkeley's Polypore"],
}

CATEGORIES = {
    "plants": {"name": "Plants", "emoji": "🌿", "base_points": 10},
    "fungi": {"name": "Fungi", "emoji": "🍄", "base_points": 25},
    "birds": {"name": "Birds", "emoji": "🐦", "base_points": 30},
    "mammals": {"name": "Mammals", "emoji": "🦊", "base_points": 50},
    "reptiles": {"name": "Reptiles", "emoji": "🦎", "base_points": 40},
    "amphibians": {"name": "Amphibians", "emoji": "🐸", "base_points": 35},
    "insects": {"name": "Insects", "emoji": "🦋", "base_points": 15},
    "minerals": {"name": "Minerals", "emoji": "💎", "base_points": 40},
    "rocks": {"name": "Rocks", "emoji": "🪨", "base_points": 15},
    "fossils": {"name": "Fossils", "emoji": "🦴", "base_points": 100},
    "artifacts": {"name": "Artifacts", "emoji": "🏺", "base_points": 150},
    "tracks": {"name": "Tracks", "emoji": "🐾", "base_points": 30},
}

# =============================================================================
# ANTI-CHEAT & VERIFICATION SYSTEMS
# =============================================================================

def generate_image_hash(image_base64):
    """Generate hash of image for duplicate detection"""
    if ',' in image_base64:
        image_data = image_base64.split(',')[1]
    else:
        image_data = image_base64
    return hashlib.md5(image_data[:10000].encode()).hexdigest()

def verify_gps_plausibility(lat, lng, player_id, game_code):
    """Check if GPS location is plausible (not teleporting)"""
    try:
        last_find = supabase.table("finds").select("latitude,longitude,created_at").eq("user_id", player_id).eq("game_code", game_code).order("created_at", desc=True).limit(1).execute()
        if not last_find.data:
            return True
        
        last = last_find.data[0]
        if not last.get("latitude") or not last.get("longitude"):
            return True
        
        # Calculate distance (rough approximation)
        import math
        lat1, lon1 = float(last["latitude"]), float(last["longitude"])
        lat2, lon2 = float(lat), float(lng)
        
        # Haversine formula
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c
        
        # If moved more than 10km in short time, suspicious
        # For now, allow up to 50km to be lenient
        return distance_km < 50
    except:
        return True

def check_duplicate_image(image_hash, player_id, game_code):
    """Check if this exact image was already submitted"""
    # Would need image_hash column in finds table
    # For now, return True (allow)
    return True

def multi_source_verify(name, lat, lng):
    """Verify species exists in location using multiple sources"""
    confidence_boost = 0
    
    # Check iNaturalist observations
    try:
        url = f"https://api.inaturalist.org/v1/observations"
        params = {"taxon_name": name, "lat": lat, "lng": lng, "radius": 100, "per_page": 1}
        r = requests.get(url, params=params, timeout=5)
        if r.json().get("total_results", 0) > 0:
            confidence_boost += 0.1
    except:
        pass
    
    # Check GBIF
    try:
        url = f"https://api.gbif.org/v1/occurrence/search"
        params = {"scientificName": name, "decimalLatitude": f"{lat-1},{lat+1}", "decimalLongitude": f"{lng-1},{lng+1}", "limit": 1}
        r = requests.get(url, params=params, timeout=5)
        if r.json().get("count", 0) > 0:
            confidence_boost += 0.1
    except:
        pass
    
    return confidence_boost

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location_info(lat, lng):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10"
        r = requests.get(url, headers={"User-Agent": "NatureHunt/4.0"}, timeout=5)
        data = r.json()
        address = data.get("address", {})
        return {
            "city": address.get("city") or address.get("town") or address.get("village") or address.get("county", "Unknown"),
            "state": address.get("state", ""),
            "country": address.get("country", ""),
            "display": f"{address.get('city') or address.get('town') or address.get('county', 'Unknown')}, {address.get('state', '')}"
        }
    except:
        return {"city": "Unknown", "state": "", "country": "", "display": "Unknown Location"}

def get_weather(lat, lng):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true"
        r = requests.get(url, timeout=5)
        data = r.json().get("current_weather", {})
        temp_c = data.get("temperature", 20)
        return {"temp_f": round(temp_c * 9/5 + 32), "temp_c": round(temp_c)}
    except:
        return {"temp_f": 70, "temp_c": 21}

def get_species_from_inaturalist(lat, lng, taxon_name, limit=50):
    try:
        url = f"https://api.inaturalist.org/v1/observations/species_counts"
        params = {"lat": lat, "lng": lng, "radius": 50, "iconic_taxa": taxon_name, "quality_grade": "research", "per_page": limit}
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        
        species = []
        for result in data.get("results", []):
            taxon = result.get("taxon", {})
            obs_count = result.get("count", 0)
            
            if obs_count < 50: rarity, multiplier = "legendary", 10
            elif obs_count < 200: rarity, multiplier = "epic", 5
            elif obs_count < 500: rarity, multiplier = "rare", 3
            elif obs_count < 2000: rarity, multiplier = "uncommon", 2
            else: rarity, multiplier = "common", 1
            
            photo = taxon.get("default_photo", {})
            name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
            
            danger_info = None
            for dname, ddata in DANGEROUS_SPECIES.items():
                if dname.lower() in name.lower():
                    danger_info = ddata
                    break
            
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
                "iconic": taxon.get("iconic_taxon_name", taxon_name),
                "danger": danger_info,
                "lookalikes": LOOKALIKES.get(name, []),
            })
        return species
    except Exception as e:
        print(f"iNaturalist error: {e}")
        return []

def identify_species(image_base64, lat, lng):
    try:
        url = f"https://api.inaturalist.org/v1/computervision/score_image"
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
            
            # Multi-source verification boost
            verification_boost = multi_source_verify(name, lat, lng)
            adjusted_score = min(score + verification_boost, 1.0)
            
            if adjusted_score > 0.90: confidence = "very_high"
            elif adjusted_score > 0.80: confidence = "high"
            elif adjusted_score > 0.65: confidence = "moderate"
            else: confidence = "low"
            
            danger_info = None
            for dname, ddata in DANGEROUS_SPECIES.items():
                if dname.lower() in name.lower():
                    danger_info = ddata
                    break
            
            results.append({
                "name": name,
                "scientific": taxon.get("name"),
                "score": adjusted_score,
                "raw_score": score,
                "confidence": confidence,
                "photo": photo.get("medium_url", ""),
                "iconic": taxon.get("iconic_taxon_name", "Unknown"),
                "id": taxon.get("id"),
                "wikipedia": taxon.get("wikipedia_url", ""),
                "danger": danger_info,
                "lookalikes": LOOKALIKES.get(name, []),
                "verified_sources": 1 + (1 if verification_boost > 0 else 0),
            })
        return results
    except Exception as e:
        print(f"CV error: {e}")
        return []

def calculate_points(rarity, category):
    multipliers = {"common": 1, "uncommon": 2, "rare": 3, "epic": 5, "legendary": 10}
    base = CATEGORIES.get(category, {}).get("base_points", 10)
    return base * multipliers.get(rarity, 1)

# =============================================================================
# ROUTES
# =============================================================================

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
        game=game, players=players.data, player_name=session.get("player_name", ""),
        found_items=found_items, lat=lat, lng=lng, weather=weather, categories=CATEGORIES
    )

@app.route("/explore")
def explore():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    location = get_location_info(lat, lng)
    return render_template("explore.html", lat=lat, lng=lng, location=location, categories=CATEGORIES)

@app.route("/reference")
def reference():
    """Complete reference guide with all items and images"""
    return render_template("reference.html",
        minerals=MINERALS_DB, rocks=ROCKS_DB, fossils=FOSSILS_DB,
        artifacts=ARTIFACTS_DB, tracks=TRACKS_DB, categories=CATEGORIES
    )

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
        "insects": "Insecta"
    }
    
    if category == "all":
        for cat, taxon in taxon_map.items():
            species = get_species_from_inaturalist(lat, lng, taxon, limit=15)
            if species:
                data["categories"][cat] = species
        
        data["categories"]["minerals"] = MINERALS_DB
        data["categories"]["rocks"] = ROCKS_DB[:15]
        data["categories"]["fossils"] = FOSSILS_DB[:15]
        data["categories"]["artifacts"] = ARTIFACTS_DB[:10]
        data["categories"]["tracks"] = TRACKS_DB
    elif category in taxon_map:
        data["categories"][category] = get_species_from_inaturalist(lat, lng, taxon_map[category], limit=50)
    elif category == "minerals":
        data["categories"]["minerals"] = MINERALS_DB
    elif category == "rocks":
        data["categories"]["rocks"] = ROCKS_DB
    elif category == "fossils":
        data["categories"]["fossils"] = FOSSILS_DB
    elif category == "artifacts":
        data["categories"]["artifacts"] = ARTIFACTS_DB
    elif category == "tracks":
        data["categories"]["tracks"] = TRACKS_DB
    
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
    
    # Anti-cheat: Check GPS plausibility
    if not verify_gps_plausibility(lat, lng, session["player_id"], session.get("game_code", "")):
        return jsonify({"error": "Location verification failed. Please enable GPS."}), 400
    
    results = identify_species(image, lat, lng)
    return jsonify({"results": results})

@app.route("/api/confirm_find", methods=["POST"])
def api_confirm_find():
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    name = data.get("name")
    category = data.get("category", "plants").lower()
    rarity = data.get("rarity", "common")
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    confidence = data.get("confidence", "low")
    
    # Require at least moderate confidence
    if confidence == "low":
        return jsonify({"error": "Confidence too low. Try a clearer photo.", "points": 0})
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    # Check for duplicate
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found this!", "points": 0})
    
    # Anti-cheat: GPS verification
    if not verify_gps_plausibility(lat, lng, player_id, game_code):
        return jsonify({"error": "Location verification failed", "points": 0})
    
    # Calculate points based on rarity and category
    points = calculate_points(rarity, category)
    
    # Bonus for high confidence
    if confidence == "very_high":
        points = int(points * 1.2)
    
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

@app.route("/safety")
def safety():
    return render_template("safety.html", dangerous=DANGEROUS_SPECIES, lookalikes=LOOKALIKES)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
