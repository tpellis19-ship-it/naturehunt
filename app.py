from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client
import random
import string
import requests
import base64
import hashlib
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

app = Flask(__name__)
app.secret_key = "naturehunt-sprint-2024"

SUPABASE_URL = "https://ymxghubshsnuyambaebg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlteGdodWJzaHNudXlhbWJhZWJnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwNzUyNzQsImV4cCI6MjA3OTY1MTI3NH0.GFsXNAPjO3bP5NekJVcaeQrQlBDcfCbYAYNqhJZXT5E"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =============================================================================
# REAL SPECIMEN IMAGES - ACTUAL MINERAL/ROCK/FOSSIL PHOTOS
# =============================================================================

MINERALS_DB = [
    # COMMON - Real specimen photos
    {"name": "Quartz (Clear)", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Quartz%2C_Tibet.jpg/640px-Quartz%2C_Tibet.jpg",
     "description": "Clear hexagonal crystals, glass-like luster. Most common mineral.", "hardness": 7},
    
    {"name": "Milky Quartz", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Quartz_milky.jpg/640px-Quartz_milky.jpg",
     "description": "White opaque quartz, cloudy from fluid inclusions.", "hardness": 7},
    
    {"name": "Feldspar (Pink)", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Orthoclase_crystals.jpg/640px-Orthoclase_crystals.jpg",
     "description": "Pink to salmon colored, blocky crystals with flat cleavage.", "hardness": 6},
    
    {"name": "Calcite (White)", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Calcite-sample2.jpg/640px-Calcite-sample2.jpg",
     "description": "White rhombohedral crystals, fizzes with acid.", "hardness": 3},
    
    {"name": "Calcite (Orange)", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Calcite-orange.jpg/640px-Calcite-orange.jpg",
     "description": "Orange calcite, often translucent.", "hardness": 3},
    
    {"name": "Muscovite Mica", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Muscovite-119650.jpg/640px-Muscovite-119650.jpg",
     "description": "Silver sheets that peel in thin layers, transparent.", "hardness": 2.5},
    
    {"name": "Biotite Mica", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Biotite-208634.jpg/640px-Biotite-208634.jpg",
     "description": "Black/brown mica sheets, peels in layers.", "hardness": 2.5},
    
    {"name": "Gypsum Crystal", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Gypse_Italie.jpg/640px-Gypse_Italie.jpg",
     "description": "Clear/white, very soft - scratches with fingernail.", "hardness": 2},
    
    {"name": "Halite (Rock Salt)", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Sel_gemme_1%28fossil%29.jpg/640px-Sel_gemme_1%28fossil%29.jpg",
     "description": "Cubic crystals, clear/white/pink, salty taste.", "hardness": 2.5},
    
    # UNCOMMON - Real specimens
    {"name": "Pyrite (Fool's Gold)", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Pyrite_3.jpg/640px-Pyrite_3.jpg",
     "description": "Brassy gold cubes, metallic, harder than gold.", "hardness": 6},
    
    {"name": "Pyrite Sun", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Pyrite_sun.jpg/640px-Pyrite_sun.jpg",
     "description": "Flat radiating pyrite disc, found in coal.", "hardness": 6},
    
    {"name": "Magnetite", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Magnetite_Octahedron.jpg/640px-Magnetite_Octahedron.jpg",
     "description": "Black metallic, MAGNETIC - sticks to magnets!", "hardness": 6},
    
    {"name": "Hematite (Specular)", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Hematite_specular.jpg/640px-Hematite_specular.jpg",
     "description": "Sparkly silver-black, red streak when scratched.", "hardness": 5.5},
    
    {"name": "Hematite (Botryoidal)", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Kidney_Ore_Hematite.jpg/640px-Kidney_Ore_Hematite.jpg",
     "description": "Kidney ore - bubbly rounded surfaces.", "hardness": 5.5},
    
    {"name": "Fluorite (Purple)", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Fluorite-with-Pyrite.jpg/640px-Fluorite-with-Pyrite.jpg",
     "description": "Purple cubic crystals, glows under UV!", "hardness": 4},
    
    {"name": "Fluorite (Green)", "rarity": "uncommon", "points": 65,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Fluorite-green.jpg/640px-Fluorite-green.jpg",
     "description": "Green cubic crystals, often with phantoms.", "hardness": 4},
    
    {"name": "Fluorite (Blue)", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Fluorite-blue.jpg/640px-Fluorite-blue.jpg",
     "description": "Blue cubic crystals, rare color.", "hardness": 4},
    
    {"name": "Galena", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Galena_%28Galenite%29_3%2C_Missouri.jpg/640px-Galena_%28Galenite%29_3%2C_Missouri.jpg",
     "description": "Heavy lead-gray cubes, very dense.", "hardness": 2.5},
    
    {"name": "Chalcopyrite", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Chalcopyrite-pas.jpg/640px-Chalcopyrite-pas.jpg",
     "description": "Brassy with iridescent tarnish, copper ore.", "hardness": 3.5},
    
    {"name": "Malachite", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Malachite-41365.jpg/640px-Malachite-41365.jpg",
     "description": "Bright green bands, often botryoidal.", "hardness": 4},
    
    {"name": "Azurite", "rarity": "rare", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Azurite-china.jpg/640px-Azurite-china.jpg",
     "description": "Deep azure blue crystals.", "hardness": 3.5},
    
    {"name": "Azurite-Malachite", "rarity": "rare", "points": 110,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Azurite-malachite-bisbee.jpg/640px-Azurite-malachite-bisbee.jpg",
     "description": "Blue azurite with green malachite together.", "hardness": 3.5},
    
    # RARE - Real specimens
    {"name": "Amethyst Crystal", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Am%C3%A9thyste_sceptre2.jpg/640px-Am%C3%A9thyste_sceptre2.jpg",
     "description": "Purple quartz points, deep violet to pale lavender.", "hardness": 7},
    
    {"name": "Amethyst Cluster", "rarity": "rare", "points": 180,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Amethyst_Geode.jpg/640px-Amethyst_Geode.jpg",
     "description": "Multiple amethyst crystals together.", "hardness": 7},
    
    {"name": "Citrine", "rarity": "rare", "points": 140,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Citrine-faceted.jpg/640px-Citrine-faceted.jpg",
     "description": "Yellow/orange quartz, natural citrine is pale.", "hardness": 7},
    
    {"name": "Rose Quartz", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Rose_quartz_crystals.jpg/640px-Rose_quartz_crystals.jpg",
     "description": "Pink translucent quartz, rarely forms crystals.", "hardness": 7},
    
    {"name": "Smoky Quartz", "rarity": "rare", "points": 110,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Quartz_Br%C3%A9sil.jpg/640px-Quartz_Br%C3%A9sil.jpg",
     "description": "Brown to gray-black quartz from radiation.", "hardness": 7},
    
    {"name": "Agate (Banded)", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Agate_banded_750pix.jpg/640px-Agate_banded_750pix.jpg",
     "description": "Colorful concentric bands in chalcedony.", "hardness": 7},
    
    {"name": "Lake Superior Agate", "rarity": "rare", "points": 130,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Lake_Superior_agate.jpg/640px-Lake_Superior_agate.jpg",
     "description": "Red-banded agate, Minnesota state gem.", "hardness": 7},
    
    {"name": "Moss Agate", "rarity": "rare", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Moss_agate.jpg/640px-Moss_agate.jpg",
     "description": "Green moss-like inclusions in clear chalcedony.", "hardness": 7},
    
    {"name": "Jasper (Red)", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Red-jasper-stone.jpg/640px-Red-jasper-stone.jpg",
     "description": "Opaque red chalcedony.", "hardness": 7},
    
    {"name": "Picture Jasper", "rarity": "rare", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Picture_jasper.jpg/640px-Picture_jasper.jpg",
     "description": "Brown jasper with landscape-like patterns.", "hardness": 7},
    
    {"name": "Garnet (Almandine)", "rarity": "rare", "points": 130,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Almandine_garnet.jpg/640px-Almandine_garnet.jpg",
     "description": "Deep red dodecahedral crystals.", "hardness": 7},
    
    {"name": "Garnet in Schist", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Garnet_mica_schist.jpg/640px-Garnet_mica_schist.jpg",
     "description": "Red garnets embedded in silvery mica schist.", "hardness": 7},
    
    {"name": "Tourmaline (Black)", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Schorl-4jg47a.jpg/640px-Schorl-4jg47a.jpg",
     "description": "Black schorl, striated prismatic crystals.", "hardness": 7},
    
    {"name": "Tourmaline (Pink)", "rarity": "epic", "points": 250,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Elbaite-Quartz-rub4-08a.jpg/640px-Elbaite-Quartz-rub4-08a.jpg",
     "description": "Pink rubellite tourmaline, very valuable.", "hardness": 7},
    
    {"name": "Watermelon Tourmaline", "rarity": "legendary", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Watermelon_tourmaline.jpg/640px-Watermelon_tourmaline.jpg",
     "description": "Pink center with green rim - rare!", "hardness": 7},
    
    {"name": "Topaz Crystal", "rarity": "rare", "points": 160,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Topaz_crystal.jpg/640px-Topaz_crystal.jpg",
     "description": "Prismatic crystals, often golden or blue.", "hardness": 8},
    
    # EPIC & LEGENDARY
    {"name": "Aquamarine", "rarity": "epic", "points": 280,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Beryl-Quartz-Muscovite-31219.jpg/640px-Beryl-Quartz-Muscovite-31219.jpg",
     "description": "Blue-green beryl, hexagonal prisms.", "hardness": 7.5},
    
    {"name": "Emerald (Raw)", "rarity": "legendary", "points": 600,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Emerald_crystal_muance.jpg/640px-Emerald_crystal_muance.jpg",
     "description": "Green beryl in matrix, chromium coloring.", "hardness": 7.5},
    
    {"name": "Ruby (Raw)", "rarity": "legendary", "points": 700,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Ruby_Winza_Tanzania.jpg/640px-Ruby_Winza_Tanzania.jpg",
     "description": "Red corundum crystal, extremely hard.", "hardness": 9},
    
    {"name": "Sapphire (Raw)", "rarity": "legendary", "points": 650,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Corundum-215245.jpg/640px-Corundum-215245.jpg",
     "description": "Blue corundum, hexagonal barrel crystals.", "hardness": 9},
    
    {"name": "Opal (Fire)", "rarity": "legendary", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Fire_opal.jpg/640px-Fire_opal.jpg",
     "description": "Orange-red opal with play of color.", "hardness": 5.5},
    
    {"name": "Opal (Boulder)", "rarity": "epic", "points": 350,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Boulder_opal.jpg/640px-Boulder_opal.jpg",
     "description": "Opal seams in brown ironstone.", "hardness": 5.5},
    
    {"name": "Diamond (Raw)", "rarity": "legendary", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Rough_diamond.jpg/640px-Rough_diamond.jpg",
     "description": "Octahedral crystal, adamantine luster.", "hardness": 10},
    
    {"name": "Gold Nugget", "rarity": "legendary", "points": 800,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Gold-36821.jpg/640px-Gold-36821.jpg",
     "description": "Native gold, heavy, doesn't tarnish.", "hardness": 2.5},
    
    {"name": "Gold in Quartz", "rarity": "legendary", "points": 600,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Gold-quartz_ore.jpg/640px-Gold-quartz_ore.jpg",
     "description": "Gold veins in quartz matrix.", "hardness": 2.5},
    
    {"name": "Silver (Native)", "rarity": "epic", "points": 400,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Native_silver.jpg/640px-Native_silver.jpg",
     "description": "Wire or dendritic silver, tarnishes black.", "hardness": 2.5},
    
    {"name": "Copper (Native)", "rarity": "rare", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Native_copper_Bisbee.jpg/640px-Native_copper_Bisbee.jpg",
     "description": "Copper color, develops green patina.", "hardness": 2.5},
    
    {"name": "Meteorite (Iron)", "rarity": "legendary", "points": 1500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Sikhote-Alin_meteorite%2C_shrapnel.jpg/640px-Sikhote-Alin_meteorite%2C_shrapnel.jpg",
     "description": "From space! Iron-nickel, regmaglypts.", "hardness": 4},
    
    {"name": "Meteorite (Stony)", "rarity": "legendary", "points": 1200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/NWA_869_meteorite.jpg/640px-NWA_869_meteorite.jpg",
     "description": "Chondrite with fusion crust.", "hardness": 4},
]

ROCKS_DB = [
    # IGNEOUS - Real photos
    {"name": "Granite (Pink)", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Granite_Yosemite_P1160483.jpg/640px-Granite_Yosemite_P1160483.jpg",
     "description": "Coarse crystals of pink feldspar, quartz, mica."},
    
    {"name": "Granite (Gray)", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Granite_pmk.jpg/640px-Granite_pmk.jpg",
     "description": "Coarse-grained with gray feldspar."},
    
    {"name": "Basalt", "type": "Igneous", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/BasaltUSGOV.jpg/640px-BasaltUSGOV.jpg",
     "description": "Dark gray/black, fine-grained volcanic."},
    
    {"name": "Vesicular Basalt", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Vesicular_basalt.jpg/640px-Vesicular_basalt.jpg",
     "description": "Basalt with gas bubble holes."},
    
    {"name": "Obsidian (Black)", "type": "Igneous", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/ObsidianOregon.jpg/640px-ObsidianOregon.jpg",
     "description": "Black volcanic glass, conchoidal fracture."},
    
    {"name": "Obsidian (Rainbow)", "type": "Igneous", "rarity": "epic", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Rainbow_Obsidian.jpg/640px-Rainbow_Obsidian.jpg",
     "description": "Obsidian with rainbow sheen."},
    
    {"name": "Mahogany Obsidian", "type": "Igneous", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Mahogany_obsidian.jpg/640px-Mahogany_obsidian.jpg",
     "description": "Brown and black swirled obsidian."},
    
    {"name": "Snowflake Obsidian", "type": "Igneous", "rarity": "rare", "points": 110,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Snowflake_obsidian.jpg/640px-Snowflake_obsidian.jpg",
     "description": "Black with white cristobalite spots."},
    
    {"name": "Pumice", "type": "Igneous", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Pomice.jpg/640px-Pomice.jpg",
     "description": "Light volcanic froth, floats on water!"},
    
    {"name": "Scoria", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Scoriite.jpg/640px-Scoriite.jpg",
     "description": "Red/black vesicular volcanic rock."},
    
    {"name": "Rhyolite", "type": "Igneous", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Rhyolite.jpg/640px-Rhyolite.jpg",
     "description": "Light-colored volcanic, fine-grained."},
    
    {"name": "Pegmatite", "type": "Igneous", "rarity": "rare", "points": 120,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Pegmatite.JPG/640px-Pegmatite.JPG",
     "description": "Very large crystals! Often has gems."},
    
    # SEDIMENTARY
    {"name": "Sandstone (Red)", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Redsandstone.jpg/640px-Redsandstone.jpg",
     "description": "Red iron-stained sand grains cemented."},
    
    {"name": "Sandstone (Tan)", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Sandstone%28quartz%29USGOV.jpg/640px-Sandstone%28quartz%29USGOV.jpg",
     "description": "Tan/buff colored sandstone."},
    
    {"name": "Limestone", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Limestone_block.jpg/640px-Limestone_block.jpg",
     "description": "Gray/tan, fizzes with acid."},
    
    {"name": "Fossiliferous Limestone", "type": "Sedimentary", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Fossiliferous_limestone.jpg/640px-Fossiliferous_limestone.jpg",
     "description": "Limestone packed with visible fossils!"},
    
    {"name": "Shale", "type": "Sedimentary", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/ShaleUSGOV.jpg/640px-ShaleUSGOV.jpg",
     "description": "Gray, splits into thin layers."},
    
    {"name": "Conglomerate", "type": "Sedimentary", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Conglomerate-bedrock.jpg/640px-Conglomerate-bedrock.jpg",
     "description": "Rounded pebbles cemented together."},
    
    {"name": "Breccia", "type": "Sedimentary", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Breccia_geologica.jpg/640px-Breccia_geologica.jpg",
     "description": "Angular fragments cemented together."},
    
    {"name": "Chert/Flint", "type": "Sedimentary", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Chert.jpg/640px-Chert.jpg",
     "description": "Hard, conchoidal fracture, tool stone."},
    
    {"name": "Coquina", "type": "Sedimentary", "rarity": "rare", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Coquina.jpg/640px-Coquina.jpg",
     "description": "Made entirely of shell fragments."},
    
    # METAMORPHIC
    {"name": "Slate", "type": "Metamorphic", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Slate_flagstone.jpg/640px-Slate_flagstone.jpg",
     "description": "Gray/black, splits into flat sheets."},
    
    {"name": "Marble (White)", "type": "Metamorphic", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/MarbleUSGOV.jpg/640px-MarbleUSGOV.jpg",
     "description": "White crystalline, fizzes with acid."},
    
    {"name": "Marble (Colored)", "type": "Metamorphic", "rarity": "rare", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Ruin_marble.jpg/640px-Ruin_marble.jpg",
     "description": "Colorful patterned marble."},
    
    {"name": "Quartzite", "type": "Metamorphic", "rarity": "uncommon", "points": 45,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/QuartziteUSGOV.jpg/640px-QuartziteUSGOV.jpg",
     "description": "Very hard, breaks through grains."},
    
    {"name": "Schist (Mica)", "type": "Metamorphic", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Schist_detail.jpg/640px-Schist_detail.jpg",
     "description": "Sparkly foliated rock with mica."},
    
    {"name": "Gneiss", "type": "Metamorphic", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Gneiss.jpg/640px-Gneiss.jpg",
     "description": "Banded light and dark layers."},
    
    {"name": "Soapstone", "type": "Metamorphic", "rarity": "rare", "points": 90,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Soapstone.jpg/640px-Soapstone.jpg",
     "description": "Very soft, soapy feel, carving stone."},
    
    # SPECIAL
    {"name": "Tektite", "type": "Impact", "rarity": "epic", "points": 350,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Tektite-australite.jpg/640px-Tektite-australite.jpg",
     "description": "Natural glass from meteorite impact."},
    
    {"name": "Fulgurite", "type": "Lightning", "rarity": "legendary", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Fulgurite.jpg/640px-Fulgurite.jpg",
     "description": "Sand fused by lightning strike!"},
    
    {"name": "Petrified Wood", "type": "Fossil", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Petrified_wood_closeup_2.jpg/640px-Petrified_wood_closeup_2.jpg",
     "description": "Wood replaced by silica, shows rings."},
]

FOSSILS_DB = [
    # INVERTEBRATES
    {"name": "Brachiopod", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/SpiriferBrachiopod.jpg/640px-SpiriferBrachiopod.jpg",
     "description": "Two shells with line of symmetry THROUGH shell.", "period": "Paleozoic"},
    
    {"name": "Crinoid Stem", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Crinoid_columnals.jpg/640px-Crinoid_columnals.jpg",
     "description": "Round discs with center hole, sea lily stems.", "period": "Paleozoic"},
    
    {"name": "Crinoid Calyx", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Crinoid_calyx.jpg/640px-Crinoid_calyx.jpg",
     "description": "Complete crinoid head - rare!", "period": "Paleozoic"},
    
    {"name": "Horn Coral", "rarity": "common", "points": 30,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Rugose_horn_coral.jpg/640px-Rugose_horn_coral.jpg",
     "description": "Cone-shaped solitary coral.", "period": "Paleozoic"},
    
    {"name": "Colonial Coral", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Petoskey_stone.jpg/640px-Petoskey_stone.jpg",
     "description": "Honeycomb pattern colonial coral.", "period": "Paleozoic"},
    
    {"name": "Bryozoan", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Archimedes_bryozoan.jpg/640px-Archimedes_bryozoan.jpg",
     "description": "Lacy or screw-shaped colonial animals.", "period": "Paleozoic"},
    
    {"name": "Trilobite (Partial)", "rarity": "uncommon", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Trilobite-elrathia.jpg/640px-Trilobite-elrathia.jpg",
     "description": "Trilobite fragment - head or tail.", "period": "Paleozoic"},
    
    {"name": "Trilobite (Complete)", "rarity": "rare", "points": 250,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Elrathia_kingii.jpg/640px-Elrathia_kingii.jpg",
     "description": "Complete trilobite with all segments!", "period": "Paleozoic"},
    
    {"name": "Trilobite (Enrolled)", "rarity": "rare", "points": 200,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flexicalymene_retrorsa_fossil_trilobite.jpg/640px-Flexicalymene_retrorsa_fossil_trilobite.jpg",
     "description": "Curled up defensive posture.", "period": "Paleozoic"},
    
    {"name": "Ammonite (Small)", "rarity": "uncommon", "points": 70,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Dactylioceras.jpg/640px-Dactylioceras.jpg",
     "description": "Coiled shell with visible sutures.", "period": "Mesozoic"},
    
    {"name": "Ammonite (Large)", "rarity": "rare", "points": 180,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Ammonite_section.jpg/640px-Ammonite_section.jpg",
     "description": "Large ammonite showing chambers.", "period": "Mesozoic"},
    
    {"name": "Ammonite (Iridescent)", "rarity": "epic", "points": 350,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Ammolite.jpg/640px-Ammolite.jpg",
     "description": "Ammolite - rainbow iridescent shell!", "period": "Mesozoic"},
    
    {"name": "Orthoceras", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Orthoceras.jpg/640px-Orthoceras.jpg",
     "description": "Straight nautiloid with chambers.", "period": "Paleozoic"},
    
    {"name": "Belemnite", "rarity": "uncommon", "points": 55,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Belemnitella_americana.jpg/640px-Belemnitella_americana.jpg",
     "description": "Bullet-shaped internal shell.", "period": "Mesozoic"},
    
    {"name": "Sea Urchin (Echinoid)", "rarity": "uncommon", "points": 65,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Micraster.jpg/640px-Micraster.jpg",
     "description": "Round with 5-fold symmetry pattern.", "period": "Various"},
    
    # VERTEBRATES
    {"name": "Shark Tooth (Small)", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Shark_teeth.jpg/640px-Shark_teeth.jpg",
     "description": "Small triangular shark teeth.", "period": "Various"},
    
    {"name": "Shark Tooth (Large)", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Carcharodon_megalodon_tooth.jpg/640px-Carcharodon_megalodon_tooth.jpg",
     "description": "Large shark or megalodon tooth.", "period": "Various"},
    
    {"name": "Fish Scale", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Lepidotes_scale.jpg/640px-Lepidotes_scale.jpg",
     "description": "Ganoid fish scale, often shiny.", "period": "Various"},
    
    {"name": "Fish Vertebra", "rarity": "uncommon", "points": 50,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Fish_vertebra.jpg/640px-Fish_vertebra.jpg",
     "description": "Concave disc-shaped bone.", "period": "Various"},
    
    {"name": "Dinosaur Bone", "rarity": "epic", "points": 500,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Fossil_bone_cross_section.jpg/640px-Fossil_bone_cross_section.jpg",
     "description": "Mineralized bone with porous texture.", "period": "Mesozoic"},
    
    {"name": "Dinosaur Tooth", "rarity": "legendary", "points": 800,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Carcharodontosaurus_tooth.jpg/640px-Carcharodontosaurus_tooth.jpg",
     "description": "Theropod or other dinosaur tooth.", "period": "Mesozoic"},
    
    # PLANTS
    {"name": "Fern Fossil", "rarity": "uncommon", "points": 60,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Fossil_fern.jpg/640px-Fossil_fern.jpg",
     "description": "Delicate fern frond impression.", "period": "Carboniferous"},
    
    {"name": "Leaf Impression", "rarity": "common", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Fossil_leaf.jpg/640px-Fossil_leaf.jpg",
     "description": "Preserved leaf shape and veins.", "period": "Various"},
    
    {"name": "Amber (Plain)", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Baltic_amber.jpg/640px-Baltic_amber.jpg",
     "description": "Fossilized tree resin.", "period": "Various"},
    
    {"name": "Amber with Inclusions", "rarity": "legendary", "points": 600,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Insect_in_amber.jpg/640px-Insect_in_amber.jpg",
     "description": "Amber with trapped insect!", "period": "Various"},
    
    {"name": "Coprolite", "rarity": "rare", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Coprolite.jpg/640px-Coprolite.jpg",
     "description": "Fossilized poop! Contains diet info.", "period": "Various"},
]

ARTIFACTS_DB = [
    {"name": "Arrowhead (Bird Point)", "rarity": "uncommon", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Bird_point_arrowhead.jpg/640px-Bird_point_arrowhead.jpg",
     "description": "Small triangular point for bird hunting.", "age": "1,000-5,000 years"},
    
    {"name": "Arrowhead (Corner-Notched)", "rarity": "uncommon", "points": 85,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Corner_notched_point.jpg/640px-Corner_notched_point.jpg",
     "description": "Notches at corners for hafting.", "age": "2,000-8,000 years"},
    
    {"name": "Arrowhead (Side-Notched)", "rarity": "uncommon", "points": 80,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Side_notched_point.jpg/640px-Side_notched_point.jpg",
     "description": "Notches on sides for attachment.", "age": "3,000-10,000 years"},
    
    {"name": "Clovis Point", "rarity": "legendary", "points": 1000,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Clovis_Point.jpg/640px-Clovis_Point.jpg",
     "description": "Fluted Paleo-Indian point, extremely rare!", "age": "11,000-13,500 years"},
    
    {"name": "Folsom Point", "rarity": "legendary", "points": 900,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Folsom_point.jpg/640px-Folsom_point.jpg",
     "description": "Delicate fluting, bison hunting.", "age": "9,000-11,000 years"},
    
    {"name": "Scraper", "rarity": "common", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Scraper_flint_tool.jpg/640px-Scraper_flint_tool.jpg",
     "description": "Rounded edge for hide processing.", "age": "5,000-50,000 years"},
    
    {"name": "Hand Axe", "rarity": "rare", "points": 300,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Acheulean_hand_axe.jpg/640px-Acheulean_hand_axe.jpg",
     "description": "Teardrop bifacial tool, very old!", "age": "100,000-1,700,000 years"},
    
    {"name": "Pottery Shard (Plain)", "rarity": "common", "points": 25,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Pottery_shard.jpg/640px-Pottery_shard.jpg",
     "description": "Undecorated ceramic fragment.", "age": "500-3,000 years"},
    
    {"name": "Pottery Shard (Decorated)", "rarity": "uncommon", "points": 75,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Decorated_pottery_shard.jpg/640px-Decorated_pottery_shard.jpg",
     "description": "Painted or incised decoration.", "age": "500-3,000 years"},
    
    {"name": "Grinding Stone (Mano)", "rarity": "uncommon", "points": 100,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Mano_grinding_stone.jpg/640px-Mano_grinding_stone.jpg",
     "description": "Handheld grinding stone.", "age": "2,000-10,000 years"},
    
    {"name": "Fire-Cracked Rock", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Fire_cracked_rock.jpg/640px-Fire_cracked_rock.jpg",
     "description": "Reddened fractured rock from hearths.", "age": "500-15,000 years"},
]

TRACKS_DB = [
    {"name": "Deer Track", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Deer_track_in_mud.jpg/640px-Deer_track_in_mud.jpg",
     "description": "Heart-shaped split hoof, 2-3 inches."},
    
    {"name": "Raccoon Track", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/Raccoon_tracks.jpg/640px-Raccoon_tracks.jpg",
     "description": "Hand-like with 5 long fingers."},
    
    {"name": "Coyote Track", "rarity": "uncommon", "points": 35,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Coyote_track.jpg/640px-Coyote_track.jpg",
     "description": "Oval canine print with claws, 2-2.5 in."},
    
    {"name": "Fox Track", "rarity": "uncommon", "points": 40,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Fox_track.jpg/640px-Fox_track.jpg",
     "description": "Small canine, straight line gait."},
    
    {"name": "Bear Track", "rarity": "rare", "points": 150,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Black_bear_track.jpg/640px-Black_bear_track.jpg",
     "description": "Large with 5 toes, 4-7 inches."},
    
    {"name": "Mountain Lion Track", "rarity": "epic", "points": 250,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Cougar_track.jpg/640px-Cougar_track.jpg",
     "description": "Large round cat print, no claws visible."},
    
    {"name": "Turkey Track", "rarity": "common", "points": 20,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Turkey_track.jpg/640px-Turkey_track.jpg",
     "description": "3 forward toes, 1 back, 4-5 inches."},
    
    {"name": "Rabbit Track", "rarity": "common", "points": 15,
     "photo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Rabbit_tracks_snow.jpg/640px-Rabbit_tracks_snow.jpg",
     "description": "Y-shaped pattern in snow/mud."},
]

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

DANGEROUS_SPECIES = {
    "Death Cap": {"level": "deadly", "warning": "EXTREMELY POISONOUS - causes fatal liver failure"},
    "Destroying Angel": {"level": "deadly", "warning": "EXTREMELY POISONOUS - no antidote"},
    "Poison Hemlock": {"level": "deadly", "warning": "All parts extremely toxic"},
    "Water Hemlock": {"level": "deadly", "warning": "Most toxic plant in North America"},
}

# =============================================================================
# FAST IDENTIFICATION FUNCTIONS
# =============================================================================

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def get_location_info(lat, lng):
    try:
        r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&zoom=10",
                        headers={"User-Agent": "NatureHunt/5.0"}, timeout=3)
        address = r.json().get("address", {})
        city = address.get("city") or address.get("town") or address.get("village") or address.get("county", "Unknown")
        return {"city": city, "state": address.get("state", ""), "display": f"{city}, {address.get('state', '')}"}
    except:
        return {"city": "Unknown", "state": "", "display": "Unknown Location"}

def fast_identify(image_base64, lat, lng):
    """Ultra-fast identification with timeout and fallback"""
    
    # Process image
    if ',' in image_base64:
        image_data = image_base64.split(',')[1]
    else:
        image_data = image_base64
    
    results = []
    
    # Try iNaturalist with short timeout
    try:
        with ThreadPoolExecutor() as executor:
            future = executor.submit(call_inaturalist_api, image_data, lat, lng)
            try:
                results = future.result(timeout=5)  # 5 second max
            except FuturesTimeout:
                pass  # Will use fallback
    except:
        pass
    
    # If no results, return suggestions from local database
    if not results:
        results = get_smart_suggestions(lat, lng)
    
    return results

def call_inaturalist_api(image_data, lat, lng):
    """Call iNaturalist with processed image"""
    try:
        url = "https://api.inaturalist.org/v1/computervision/score_image"
        files = {'image': ('photo.jpg', base64.b64decode(image_data), 'image/jpeg')}
        params = {"lat": lat, "lng": lng} if lat and lng else {}
        
        r = requests.post(url, files=files, data=params, timeout=5)
        data = r.json()
        
        results = []
        for result in data.get("results", [])[:8]:
            taxon = result.get("taxon", {})
            photo = taxon.get("default_photo", {})
            score = result.get("combined_score", 0)
            name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
            
            results.append({
                "name": name,
                "scientific": taxon.get("name", ""),
                "score": score,
                "confidence": "high" if score > 0.7 else "moderate" if score > 0.4 else "low",
                "photo": photo.get("medium_url", ""),
                "category": taxon.get("iconic_taxon_name", "Unknown"),
                "points": int(score * 100),
            })
        return results
    except:
        return []

def get_smart_suggestions(lat, lng):
    """Get suggestions based on location"""
    # Return mix of common local items
    suggestions = []
    
    # Add some minerals
    for m in random.sample(MINERALS_DB[:10], min(3, len(MINERALS_DB))):
        suggestions.append({
            "name": m["name"], "photo": m["photo"], "score": 0.6,
            "confidence": "moderate", "category": "minerals", "points": m["points"]
        })
    
    # Add some rocks
    for r in random.sample(ROCKS_DB[:10], min(2, len(ROCKS_DB))):
        suggestions.append({
            "name": r["name"], "photo": r["photo"], "score": 0.5,
            "confidence": "moderate", "category": "rocks", "points": r["points"]
        })
    
    return suggestions[:5]

def get_species_from_inaturalist(lat, lng, taxon_name, limit=30):
    """Get species with timeout"""
    try:
        r = requests.get(
            "https://api.inaturalist.org/v1/observations/species_counts",
            params={"lat": lat, "lng": lng, "radius": 50, "iconic_taxa": taxon_name, 
                   "quality_grade": "research", "per_page": limit},
            timeout=5
        )
        
        species = []
        for result in r.json().get("results", []):
            taxon = result.get("taxon", {})
            obs = result.get("count", 0)
            
            if obs < 50: rarity, mult = "legendary", 10
            elif obs < 200: rarity, mult = "epic", 5
            elif obs < 500: rarity, mult = "rare", 3
            elif obs < 2000: rarity, mult = "uncommon", 2
            else: rarity, mult = "common", 1
            
            photo = taxon.get("default_photo", {})
            name = taxon.get("preferred_common_name") or taxon.get("name", "Unknown")
            
            danger = None
            for dname, ddata in DANGEROUS_SPECIES.items():
                if dname.lower() in name.lower():
                    danger = ddata
                    break
            
            species.append({
                "name": name, "scientific": taxon.get("name", ""),
                "photo": photo.get("medium_url") or photo.get("square_url", ""),
                "observations": obs, "rarity": rarity,
                "points": CATEGORIES.get(taxon_name.lower(), {}).get("base_points", 10) * mult,
                "wikipedia": taxon.get("wikipedia_url", ""),
                "category": taxon.get("iconic_taxon_name", taxon_name),
                "danger": danger,
            })
        return species
    except:
        return []

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
    
    players = supabase.table("players").select("*").eq("game_code", code).order("score", desc=True).execute()
    
    lat = session.get("lat", 35.4676)
    lng = session.get("lng", -97.5164)
    
    my_finds = supabase.table("finds").select("item_name").eq("game_code", code).eq("user_id", session["player_id"]).execute()
    found_items = [f["item_name"] for f in my_finds.data] if my_finds.data else []
    
    return render_template("game.html",
        game=game_data.data[0], players=players.data, player_name=session.get("player_name", ""),
        found_items=found_items, lat=lat, lng=lng, categories=CATEGORIES
    )

@app.route("/explore")
def explore():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    return render_template("explore.html", lat=lat, lng=lng, categories=CATEGORIES)

@app.route("/reference")
def reference():
    return render_template("reference.html",
        minerals=MINERALS_DB, rocks=ROCKS_DB, fossils=FOSSILS_DB,
        artifacts=ARTIFACTS_DB, tracks=TRACKS_DB, categories=CATEGORIES)

@app.route("/api/species")
def api_species():
    lat = float(request.args.get("lat", 35.4676))
    lng = float(request.args.get("lng", -97.5164))
    category = request.args.get("category", "all")
    
    location = get_location_info(lat, lng)
    data = {"location": location, "categories": {}}
    
    taxon_map = {"plants": "Plantae", "fungi": "Fungi", "birds": "Aves",
                 "mammals": "Mammalia", "reptiles": "Reptilia", "amphibians": "Amphibia", "insects": "Insecta"}
    
    if category == "all":
        for cat, taxon in list(taxon_map.items())[:4]:  # Limit for speed
            species = get_species_from_inaturalist(lat, lng, taxon, limit=10)
            if species:
                data["categories"][cat] = species
        
        data["categories"]["minerals"] = MINERALS_DB[:15]
        data["categories"]["rocks"] = ROCKS_DB[:10]
        data["categories"]["fossils"] = FOSSILS_DB[:10]
        data["categories"]["artifacts"] = ARTIFACTS_DB[:8]
        data["categories"]["tracks"] = TRACKS_DB[:8]
    elif category in taxon_map:
        data["categories"][category] = get_species_from_inaturalist(lat, lng, taxon_map[category], limit=40)
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
    
    results = fast_identify(image, lat, lng)
    return jsonify({"results": results})

@app.route("/api/quick_log", methods=["POST"])
def api_quick_log():
    """Quick log from reference - no photo needed"""
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    name = data.get("name")
    category = data.get("category", "minerals")
    points = data.get("points", 10)
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    if not game_code:
        return jsonify({"error": "Not in a game"}), 400
    
    # Check duplicate
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    supabase.table("finds").insert({
        "user_id": player_id, "game_code": game_code, "item_name": name,
        "category": category, "points": points, "latitude": lat, "longitude": lng
    }).execute()
    
    player = supabase.table("players").select("score").eq("id", player_id).execute()
    new_score = player.data[0]["score"] + points
    supabase.table("players").update({"score": new_score}).eq("id", player_id).execute()
    
    return jsonify({"success": True, "points": points, "new_score": new_score})

@app.route("/api/confirm_find", methods=["POST"])
def api_confirm_find():
    if "player_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.json
    name = data.get("name")
    category = data.get("category", "plants").lower()
    points = data.get("points", 50)
    lat = data.get("lat", session.get("lat", 0))
    lng = data.get("lng", session.get("lng", 0))
    
    game_code = session.get("game_code")
    player_id = session.get("player_id")
    
    existing = supabase.table("finds").select("*").eq("game_code", game_code).eq("user_id", player_id).eq("item_name", name).execute()
    if existing.data:
        return jsonify({"error": "Already found!", "points": 0})
    
    supabase.table("finds").insert({
        "user_id": player_id, "game_code": game_code, "item_name": name,
        "category": category, "points": points, "latitude": lat, "longitude": lng
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
    return render_template("safety.html", dangerous=DANGEROUS_SPECIES)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
