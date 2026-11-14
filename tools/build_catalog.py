#!/usr/bin/env python3
"""Erzeugt die Block- und Item-Einträge in site/data/catalog.json aus den offenen Registry-Daten
von PrismarineJS/minecraft-data (https://github.com/PrismarineJS/minecraft-data).

Übernommen werden nur Fakten (Block-IDs, englische Anzeigenamen). Die deutschen Namen werden
hier über Regeln und die Tabelle MANUAL gebildet; wo keine Regel passt, steht der englische Name.
Bei reinen Items (Art "i") bleiben bereits im Katalog stehende deutsche Namen erhalten.

Aufruf:  python3 -I tools/build_catalog.py <pfad-zu-minecraft-data> <java-version> <bedrock-version>
Beispiel: python3 -I tools/build_catalog.py ../minecraft-data 26.1 1.26.60
"""
import json
import re
import sys
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "site" / "data" / "catalog.json"

# ---- Was nicht in die Auswahl gehört (technische Varianten, Lern-Edition, Platzhalter) ----
SKIP = [
    r"^element_", r"_double_slab$", r"^double_cut_copper_slab$", r"^hard_", r"^colored_torch_", r"^underwater_",
    r"^(compound_creator|lab_table|material_reducer|element_constructor|chemical_heat|camera|chalkboard)$",
    r"^(info_update2?|reserved6|unknown|client_request_placeholder_block|moving_block|netherreactor|glowingobsidian)$",
    r"piston_arm_collision$", r"^deprecated_", r"^lit_(?!pumpkin)", r"^(un)?powered_(comparator|repeater)$",
    r"^unlit_", r"_standing_sign$", r"^(standing|wall)_(sign|banner)$", r"^darkoak_wall_sign$", r"^flowing_",
    r"^cave_vines_", r"^trip_wire$", r"^daylight_detector_inverted$", r"^stonecutter$",
    r"^potted_", r"_wall_(sign|hanging_sign|banner|head|skull|torch)$", r"^wall_torch$", r"^(cave|void)_air$",
    r"^(moving_piston|piston_head|tripwire)$", r"_plant$", r"^attached_", r"^big_dripleaf_stem$", r"^tall_seagrass$",
    r"_wall_fan$", r"^(bubble_column|kelp_plant|bamboo_sapling|sweet_berry_bush|fire|soul_fire)$",
]
KEEP = {"fire", "soul_fire"}

# ---- Bedrock-ID -> Java-ID, wenn derselbe Block anders heißt (für Namen und Kategorie) ----
ALIAS = {
    "brick_block": "bricks", "web": "cobweb", "magma": "magma_block", "noteblock": "note_block", "slime": "slime_block",
    "mob_spawner": "spawner", "hardened_clay": "terracotta", "reeds": "sugar_cane", "undyed_shulker_box": "shulker_box",
    "golden_rail": "powered_rail", "melon_block": "melon", "lit_pumpkin": "jack_o_lantern", "waterlily": "lily_pad",
    "deadbush": "dead_bush", "grass_path": "dirt_path", "end_bricks": "end_stone_bricks", "nether_brick": "nether_bricks",
    "red_nether_brick": "red_nether_bricks", "quartz_ore": "nether_quartz_ore", "portal": "nether_portal",
    "frog_spawn": "frogspawn", "dirt_with_roots": "rooted_dirt", "waxed_copper": "waxed_copper_block",
    "silver_glazed_terracotta": "light_gray_glazed_terracotta", "azalea_leaves_flowered": "flowering_azalea_leaves",
    "wooden_button": "oak_button", "wooden_door": "oak_door", "wooden_pressure_plate": "oak_pressure_plate",
    "fence_gate": "oak_fence_gate", "trapdoor": "oak_trapdoor", "stonecutter_block": "stonecutter",
    "small_dripleaf_block": "small_dripleaf", "normal_stone_slab": "stone_slab", "normal_stone_stairs": "stone_stairs",
    "prismarine_bricks_stairs": "prismarine_brick_stairs", "end_brick_stairs": "end_stone_brick_stairs",
    "beetroot": "beetroots", "snow_layer": "snow", "frame": "item_frame", "glow_frame": "glow_item_frame",
}

# ---- Deutsche Namen: Farben ----
COLORS = {
    "white": "Weiß", "orange": "Orange", "magenta": "Magenta", "light_blue": "Hellblau", "yellow": "Gelb", "lime": "Hellgrün",
    "pink": "Rosa", "gray": "Grau", "light_gray": "Hellgrau", "cyan": "Türkis", "purple": "Violett", "blue": "Blau",
    "brown": "Braun", "green": "Grün", "red": "Rot", "black": "Schwarz",
}
ENDING = {"f": "e", "m": "er", "n": "es"}


def adj(color, gender):
    base = COLORS[color]
    if base in ("Magenta", "Rosa"):
        return base
    if base == "Orange":
        return "Orangen" + ENDING[gender]
    return base + ENDING[gender]


COLOR_NOUNS = {
    "wool": ("Wolle", "f"), "carpet": ("Teppich", "m"), "concrete": ("Beton", "m"), "concrete_powder": ("Trockenbeton", "m"),
    "terracotta": ("Keramik", "f"), "stained_glass": ("Glas", "n"), "stained_glass_pane": ("Glasscheibe", "f"),
    "concrete_stairs": ("Betontreppe", "f"), "concrete_slab": ("Betonstufe", "f"),
    "wool_stairs": ("Wolltreppe", "f"), "wool_slab": ("Wollstufe", "f"),
    "bed": ("Bett", "n"), "banner": ("Banner", "n"), "candle": ("Kerze", "f"), "shulker_box": ("Shulker-Kiste", "f"),
}

# ---- Deutsche Namen: Holz ----
WOODS = {  # id: (Holz-Stamm, Baum-Stamm)
    "oak": ("Eichenholz", "Eichen"), "spruce": ("Fichtenholz", "Fichten"), "birch": ("Birkenholz", "Birken"),
    "jungle": ("Tropenholz", "Tropenbaum"), "acacia": ("Akazienholz", "Akazien"), "dark_oak": ("Schwarzeichenholz", "Schwarzeichen"),
    "mangrove": ("Mangrovenholz", "Mangroven"), "cherry": ("Kirschholz", "Kirsch"), "pale_oak": ("Blasseichenholz", "Blasseichen"),
    "bamboo": ("Bambus", None), "crimson": ("Karmesin", None), "warped": ("Wirr", None),
}
WOOD_PARTS = {
    "planks": "bretter", "stairs": "treppe", "slab": "stufe", "fence": "zaun", "fence_gate": "zauntor", "door": "tür",
    "trapdoor": "falltür", "button": "knopf", "pressure_plate": "druckplatte", "sign": "schild",
    "hanging_sign": "hängeschild", "shelf": "regal",
}

# ---- Deutsche Namen: Stein-Familien (Treppe, Stufe, Mauer) ----
FAMILIES = {
    "stone": ("", "Stein"), "smooth_stone": ("Glatte", "Stein"), "cobblestone": ("", "Bruchstein"),
    "mossy_cobblestone": ("Bemooste", "Bruchstein"), "stone_brick": ("", "Steinziegel"),
    "mossy_stone_brick": ("Bemooste", "Steinziegel"), "granite": ("", "Granit"), "polished_granite": ("Polierte", "Granit"),
    "diorite": ("", "Diorit"), "polished_diorite": ("Polierte", "Diorit"), "andesite": ("", "Andesit"),
    "polished_andesite": ("Polierte", "Andesit"), "sandstone": ("", "Sandstein"), "smooth_sandstone": ("Glatte", "Sandstein"),
    "cut_sandstone": ("Geschnittene", "Sandstein"), "red_sandstone": ("Rote", "Sandstein"),
    "smooth_red_sandstone": ("Glatte rote", "Sandstein"), "cut_red_sandstone": ("Geschnittene rote", "Sandstein"),
    "brick": ("", "Ziegel"), "nether_brick": ("", "Netherziegel"), "red_nether_brick": ("Rote", "Netherziegel"),
    "prismarine": ("", "Prismarin"), "prismarine_brick": ("", "Prismarinziegel"), "dark_prismarine": ("Dunkle", "Prismarin"),
    "quartz": ("", "Quarz"), "smooth_quartz": ("Glatte", "Quarz"), "purpur": ("", "Purpur"),
    "end_stone_brick": ("", "Endsteinziegel"), "blackstone": ("", "Schwarzstein"),
    "polished_blackstone": ("Polierte", "Schwarzstein"), "polished_blackstone_brick": ("Polierte", "Schwarzsteinziegel"),
    "deepslate_brick": ("", "Tiefenschieferziegel"), "deepslate_tile": ("", "Tiefenschieferfliesen"),
    "cobbled_deepslate": ("", "Bruchtiefenschiefer"), "polished_deepslate": ("Polierte", "Tiefenschiefer"),
    "tuff": ("", "Tuffstein"), "polished_tuff": ("Polierte", "Tuffstein"), "tuff_brick": ("", "Tuffsteinziegel"),
    "mud_brick": ("", "Schlammziegel"), "resin_brick": ("", "Harzziegel"), "bamboo_mosaic": ("", "Bambusmosaik"),
}
FAMILY_PARTS = {"stairs": "treppe", "slab": "stufe", "wall": "mauer"}

# ---- Deutsche Namen: einzelne Blöcke ----
MANUAL = {
    "air": "Luft (löscht den Block)", "water": "Wasser", "lava": "Lava", "fire": "Feuer", "soul_fire": "Seelenfeuer",
    "bedrock": "Grundgestein", "barrier": "Barriere (unsichtbarer Block)", "light": "Lichtblock", "structure_void": "Konstruktionsleere",
    "structure_block": "Konstruktionsblock", "jigsaw": "Verbundblock", "command_block": "Befehlsblock",
    "chain_command_block": "Ketten-Befehlsblock", "repeating_command_block": "Wiederhol-Befehlsblock",
    "spawner": "Spawner", "trial_spawner": "Prüfungs-Spawner", "vault": "Tresor", "dragon_egg": "Drachenei",
    "end_portal": "Endportal", "end_portal_frame": "Endportalrahmen", "end_gateway": "Endtransitportal",
    "nether_portal": "Netherportal", "allow": "Erlauben-Block", "deny": "Verbieten-Block", "border_block": "Grenzblock",
    "invisible_bedrock": "Unsichtbares Grundgestein", "bed": "Bett", "item_frame": "Rahmen", "glow_item_frame": "Leuchtrahmen",
    "grass_block": "Grasblock", "dirt": "Erde", "coarse_dirt": "Grobe Erde", "rooted_dirt": "Wurzelerde", "podzol": "Podsol",
    "mycelium": "Myzel", "dirt_path": "Trampelpfad", "farmland": "Ackerboden", "mud": "Schlamm", "packed_mud": "Fester Schlamm",
    "mud_bricks": "Schlammziegel", "clay": "Ton", "sand": "Sand", "red_sand": "Roter Sand", "gravel": "Kies",
    "suspicious_sand": "Seltsamer Sand", "suspicious_gravel": "Seltsamer Kies", "snow": "Schnee", "snow_block": "Schneeblock",
    "powder_snow": "Pulverschnee", "ice": "Eis", "packed_ice": "Packeis", "blue_ice": "Blaueis", "frosted_ice": "Brüchiges Eis",
    "stone": "Stein", "smooth_stone": "Glatter Stein", "cobblestone": "Bruchstein", "mossy_cobblestone": "Bemooster Bruchstein",
    "stone_bricks": "Steinziegel", "mossy_stone_bricks": "Bemooste Steinziegel", "cracked_stone_bricks": "Rissige Steinziegel",
    "chiseled_stone_bricks": "Gemeißelte Steinziegel", "granite": "Granit", "polished_granite": "Polierter Granit",
    "diorite": "Diorit", "polished_diorite": "Polierter Diorit", "andesite": "Andesit", "polished_andesite": "Polierter Andesit",
    "deepslate": "Tiefenschiefer", "cobbled_deepslate": "Bruchtiefenschiefer", "polished_deepslate": "Polierter Tiefenschiefer",
    "deepslate_bricks": "Tiefenschieferziegel", "deepslate_tiles": "Tiefenschieferfliesen",
    "chiseled_deepslate": "Gemeißelter Tiefenschiefer", "reinforced_deepslate": "Verstärkter Tiefenschiefer",
    "tuff": "Tuffstein", "polished_tuff": "Polierter Tuffstein", "tuff_bricks": "Tuffsteinziegel",
    "chiseled_tuff": "Gemeißelter Tuffstein", "calcite": "Kalzit", "dripstone_block": "Tropfsteinblock",
    "pointed_dripstone": "Spitzer Tropfstein", "sandstone": "Sandstein", "smooth_sandstone": "Glatter Sandstein",
    "cut_sandstone": "Geschnittener Sandstein", "chiseled_sandstone": "Gemeißelter Sandstein",
    "red_sandstone": "Roter Sandstein", "smooth_red_sandstone": "Glatter roter Sandstein",
    "cut_red_sandstone": "Geschnittener roter Sandstein", "chiseled_red_sandstone": "Gemeißelter roter Sandstein",
    "bricks": "Ziegelsteine", "obsidian": "Obsidian", "crying_obsidian": "Weinender Obsidian", "terracotta": "Keramik",
    "glass": "Glas", "glass_pane": "Glasscheibe", "tinted_glass": "Getöntes Glas", "bookshelf": "Bücherregal",
    "chiseled_bookshelf": "Gemeißeltes Bücherregal", "hay_block": "Strohballen", "honey_block": "Honigblock",
    "honeycomb_block": "Honigwabenblock", "slime_block": "Schleimblock", "sponge": "Schwamm", "wet_sponge": "Nasser Schwamm",
    "cobweb": "Spinnennetz", "ladder": "Leiter", "scaffolding": "Gerüst", "iron_bars": "Eisengitter", "iron_door": "Eisentür",
    "iron_trapdoor": "Eisenfalltür", "chain": "Kette", "iron_chain": "Eisenkette", "bone_block": "Knochenblock",
    "prismarine": "Prismarin", "prismarine_bricks": "Prismarinziegel", "dark_prismarine": "Dunkler Prismarin",
    "sea_lantern": "Seelaterne", "purpur_block": "Purpurblock", "purpur_pillar": "Purpursäule", "end_stone": "Endstein",
    "end_stone_bricks": "Endsteinziegel", "end_rod": "Endstab", "chorus_plant": "Choruspflanze", "chorus_flower": "Chorusblüte",
    "netherrack": "Netherrack", "nether_bricks": "Netherziegel", "red_nether_bricks": "Rote Netherziegel",
    "cracked_nether_bricks": "Rissige Netherziegel", "chiseled_nether_bricks": "Gemeißelte Netherziegel",
    "nether_brick_fence": "Netherziegelzaun", "soul_sand": "Seelensand", "soul_soil": "Seelenerde", "glowstone": "Glowstone",
    "magma_block": "Magmablock", "basalt": "Basalt", "polished_basalt": "Polierter Basalt", "smooth_basalt": "Glatter Basalt",
    "blackstone": "Schwarzstein", "polished_blackstone": "Polierter Schwarzstein",
    "polished_blackstone_bricks": "Polierte Schwarzsteinziegel", "gilded_blackstone": "Golddurchzogener Schwarzstein",
    "chiseled_polished_blackstone": "Gemeißelter polierter Schwarzstein", "nether_wart_block": "Netherwarzenblock",
    "warped_wart_block": "Wirrwarzenblock", "shroomlight": "Pilzlicht", "crimson_nylium": "Karmesin-Nezel",
    "warped_nylium": "Wirr-Nezel", "crimson_stem": "Karmesinstiel", "warped_stem": "Wirrstiel",
    "crimson_hyphae": "Karmesinhyphen", "warped_hyphae": "Wirrhyphen", "crimson_fungus": "Karmesinpilz",
    "warped_fungus": "Wirrpilz", "crimson_roots": "Karmesinwurzeln", "warped_roots": "Wirrwurzeln",
    "nether_sprouts": "Nethersprossen", "weeping_vines": "Trauerranken", "twisting_vines": "Zwirbelranken",
    "ancient_debris": "Antiker Schrott", "respawn_anchor": "Seelenanker", "lodestone": "Leitstein",
    "quartz_block": "Quarzblock", "smooth_quartz": "Glatter Quarzblock", "quartz_pillar": "Quarzsäule",
    "chiseled_quartz_block": "Gemeißelter Quarzblock", "quartz_bricks": "Quarzziegel",
    "diamond_block": "Diamantblock", "emerald_block": "Smaragdblock", "gold_block": "Goldblock", "iron_block": "Eisenblock",
    "netherite_block": "Netheritblock", "copper_block": "Kupferblock", "coal_block": "Kohleblock",
    "lapis_block": "Lapislazuliblock", "redstone_block": "Redstone-Block", "amethyst_block": "Amethystblock",
    "budding_amethyst": "Knospender Amethyst", "amethyst_cluster": "Amethysthaufen", "raw_iron_block": "Roheisenblock",
    "raw_gold_block": "Rohgoldblock", "raw_copper_block": "Rohkupferblock", "resin_block": "Harzblock",
    "resin_bricks": "Harzziegel", "resin_clump": "Harzklumpen",
    "coal_ore": "Steinkohle", "iron_ore": "Eisenerz", "copper_ore": "Kupfererz", "gold_ore": "Golderz",
    "redstone_ore": "Redstone-Erz", "lapis_ore": "Lapislazulierz", "diamond_ore": "Diamanterz", "emerald_ore": "Smaragderz",
    "nether_gold_ore": "Nethergolderz", "nether_quartz_ore": "Netherquarzerz",
    "deepslate_coal_ore": "Tiefenschiefer-Steinkohle", "deepslate_iron_ore": "Tiefenschiefer-Eisenerz",
    "deepslate_copper_ore": "Tiefenschiefer-Kupfererz", "deepslate_gold_ore": "Tiefenschiefer-Golderz",
    "deepslate_redstone_ore": "Tiefenschiefer-Redstone-Erz", "deepslate_lapis_ore": "Tiefenschiefer-Lapislazulierz",
    "deepslate_diamond_ore": "Tiefenschiefer-Diamanterz", "deepslate_emerald_ore": "Tiefenschiefer-Smaragderz",
    "short_grass": "Gras", "tall_grass": "Hohes Gras", "fern": "Farn", "large_fern": "Großer Farn", "dead_bush": "Toter Busch",
    "bush": "Busch", "dandelion": "Löwenzahn", "poppy": "Mohn", "blue_orchid": "Blaue Orchidee", "allium": "Sternlauch",
    "azure_bluet": "Porzellansternchen", "red_tulip": "Rote Tulpe", "orange_tulip": "Orange Tulpe",
    "white_tulip": "Weiße Tulpe", "pink_tulip": "Rosa Tulpe", "oxeye_daisy": "Margerite", "cornflower": "Kornblume",
    "lily_of_the_valley": "Maiglöckchen", "wither_rose": "Wither-Rose", "torchflower": "Fackellilie",
    "sunflower": "Sonnenblume", "lilac": "Flieder", "rose_bush": "Rosenstrauch", "peony": "Pfingstrose",
    "pitcher_plant": "Kannenpflanze", "pink_petals": "Rosa Blütenblätter", "wildflowers": "Wildblumen",
    "leaf_litter": "Laubstreu", "spore_blossom": "Sporenblüte", "brown_mushroom": "Brauner Pilz", "red_mushroom": "Roter Pilz",
    "brown_mushroom_block": "Brauner Pilzblock", "red_mushroom_block": "Roter Pilzblock", "mushroom_stem": "Pilzstiel",
    "cactus": "Kaktus", "cactus_flower": "Kaktusblüte", "sugar_cane": "Zuckerrohr", "bamboo": "Bambus", "vine": "Ranken",
    "glow_lichen": "Leuchtflechte", "lily_pad": "Seerosenblatt", "seagrass": "Seegras", "kelp": "Seetang",
    "dried_kelp_block": "Getrockneter Seetangblock", "sea_pickle": "Seegurke", "moss_block": "Moosblock",
    "moss_carpet": "Moosteppich", "pale_moss_block": "Blasser Moosblock", "pale_moss_carpet": "Blasser Moosteppich",
    "pale_hanging_moss": "Blasses Hängemoos", "azalea": "Azalee", "flowering_azalea": "Blühende Azalee",
    "azalea_leaves": "Azaleenlaub", "flowering_azalea_leaves": "Blühendes Azaleenlaub", "big_dripleaf": "Großes Tropfblatt",
    "small_dripleaf": "Kleines Tropfblatt", "hanging_roots": "Hängewurzeln", "mangrove_roots": "Mangrovenwurzeln",
    "muddy_mangrove_roots": "Schlammige Mangrovenwurzeln", "mangrove_propagule": "Mangroven-Keimling",
    "pumpkin": "Kürbis", "carved_pumpkin": "Geschnitzter Kürbis", "jack_o_lantern": "Kürbislaterne", "melon": "Melone",
    "wheat": "Weizen", "carrots": "Karotten", "potatoes": "Kartoffeln", "beetroots": "Rote Bete",
    "nether_wart": "Netherwarze", "cocoa": "Kakao", "bee_nest": "Bienennest", "beehive": "Bienenstock",
    "turtle_egg": "Schildkrötenei", "sniffer_egg": "Schnüffler-Ei", "frogspawn": "Froschlaich",
    "ochre_froglight": "Ockernes Froschlicht", "verdant_froglight": "Grünes Froschlicht",
    "pearlescent_froglight": "Perlmutternes Froschlicht", "sculk": "Sculk", "sculk_vein": "Sculk-Ader",
    "sculk_sensor": "Sculk-Sensor", "calibrated_sculk_sensor": "Kalibrierter Sculk-Sensor",
    "sculk_catalyst": "Sculk-Katalysator", "sculk_shrieker": "Sculk-Kreischer", "bamboo_block": "Bambusblock",
    "stripped_bamboo_block": "Geschälter Bambusblock", "bamboo_mosaic": "Bambusmosaik", "creaking_heart": "Knarzherz",
    "crafting_table": "Werkbank", "furnace": "Ofen", "blast_furnace": "Schmelzofen", "smoker": "Räucherofen",
    "chest": "Truhe", "trapped_chest": "Redstone-Truhe", "ender_chest": "Endertruhe", "barrel": "Fass",
    "shulker_box": "Shulker-Kiste", "hopper": "Trichter", "dropper": "Spender", "dispenser": "Werfer",
    "crafter": "Werker", "anvil": "Amboss", "chipped_anvil": "Angeschlagener Amboss", "damaged_anvil": "Beschädigter Amboss",
    "grindstone": "Schleifstein", "smithing_table": "Schmiedetisch", "stonecutter": "Steinsäge", "loom": "Webstuhl",
    "cartography_table": "Kartentisch", "fletching_table": "Bognertisch", "composter": "Komposter", "lectern": "Lesepult",
    "enchanting_table": "Zaubertisch", "brewing_stand": "Braustand", "cauldron": "Kessel", "beacon": "Leuchtfeuer",
    "conduit": "Aquisator", "bell": "Glocke", "jukebox": "Plattenspieler", "note_block": "Notenblock",
    "campfire": "Lagerfeuer", "soul_campfire": "Seelenlagerfeuer", "torch": "Fackel", "soul_torch": "Seelenfackel",
    "copper_torch": "Kupferfackel", "redstone_torch": "Redstone-Fackel", "lantern": "Laterne", "soul_lantern": "Seelenlaterne",
    "candle": "Kerze", "cake": "Kuchen", "flower_pot": "Blumentopf", "decorated_pot": "Verzierter Krug",
    "tnt": "TNT", "redstone_wire": "Redstone-Leitung", "redstone_lamp": "Redstone-Lampe", "repeater": "Redstone-Verstärker",
    "comparator": "Redstone-Komparator", "observer": "Beobachter", "piston": "Kolben", "sticky_piston": "Klebriger Kolben",
    "lever": "Hebel", "stone_button": "Steinknopf", "stone_pressure_plate": "Steindruckplatte",
    "polished_blackstone_button": "Polierter Schwarzsteinknopf",
    "polished_blackstone_pressure_plate": "Polierte Schwarzsteindruckplatte",
    "light_weighted_pressure_plate": "Feinwägeplatte", "heavy_weighted_pressure_plate": "Grobwägeplatte",
    "tripwire_hook": "Haken", "daylight_detector": "Tageslichtsensor", "target": "Zielblock",
    "lightning_rod": "Blitzableiter", "rail": "Schiene", "powered_rail": "Antriebsschiene",
    "detector_rail": "Sensorschiene", "activator_rail": "Aktivierungsschiene",
    "skeleton_skull": "Skelettschädel", "wither_skeleton_skull": "Witherskelettschädel", "zombie_head": "Zombiekopf",
    "creeper_head": "Creeperkopf", "player_head": "Spielerkopf", "dragon_head": "Drachenkopf", "piglin_head": "Piglinkopf",
    "infested_stone": "Befallener Stein", "infested_cobblestone": "Befallener Bruchstein",
    "infested_stone_bricks": "Befallene Steinziegel", "infested_mossy_stone_bricks": "Befallene bemooste Steinziegel",
    "infested_cracked_stone_bricks": "Befallene rissige Steinziegel",
    "infested_chiseled_stone_bricks": "Befallene gemeißelte Steinziegel", "infested_deepslate": "Befallener Tiefenschiefer",
    "cracked_deepslate_bricks": "Rissige Tiefenschieferziegel", "cracked_deepslate_tiles": "Rissige Tiefenschieferfliesen",
    "cracked_polished_blackstone_bricks": "Rissige polierte Schwarzsteinziegel",
    "chiseled_tuff_bricks": "Gemeißelte Tuffsteinziegel", "chiseled_resin_bricks": "Gemeißelte Harzziegel",
    "small_amethyst_bud": "Kleine Amethystknospe", "medium_amethyst_bud": "Mittlere Amethystknospe",
    "large_amethyst_bud": "Große Amethystknospe", "melon_stem": "Melonenstängel", "pumpkin_stem": "Kürbisstängel",
    "cave_vines": "Höhlenranken", "open_eyeblossom": "Offene Augenblüte", "closed_eyeblossom": "Geschlossene Augenblüte",
    "firefly_bush": "Glühwürmchenbusch", "short_dry_grass": "Kurzes trockenes Gras", "tall_dry_grass": "Hohes trockenes Gras",
    "water_cauldron": "Wasserkessel", "lava_cauldron": "Lavakessel", "powder_snow_cauldron": "Pulverschneekessel",
    "test_block": "Testblock", "test_instance_block": "Testinstanzblock", "candle_cake": "Kuchen mit Kerze",
    "petrified_oak_slab": "Versteinerte Eichenholzstufe",
    "heavy_core": "Schwerer Kern", "dried_ghast": "Getrockneter Ghast", "tube_coral_block": "Orgelkorallenblock",
    "brain_coral_block": "Hirnkorallenblock", "bubble_coral_block": "Blasenkorallenblock",
    "fire_coral_block": "Feuerkorallenblock", "horn_coral_block": "Geweihkorallenblock",
}

# ---- Deutsche Namen: Kupfer und Korallen ----
COPPER_STATES = {"waxed": "gewachst", "exposed": "angelaufen", "weathered": "verwittert", "oxidized": "oxidiert"}
COPPER_PARTS = {
    "copper": ("", "Kupferblock", "m"), "copper_block": ("", "Kupferblock", "m"),
    "cut_copper": ("geschnitten", "Kupferblock", "m"), "cut_copper_stairs": ("geschnitten", "Kupfertreppe", "f"),
    "cut_copper_slab": ("geschnitten", "Kupferstufe", "f"), "double_cut_copper_slab": ("geschnitten", "Kupferstufe", "f"),
    "chiseled_copper": ("gemeißelt", "Kupferblock", "m"), "copper_grate": ("", "Kupferrost", "m"),
    "copper_bulb": ("", "Kupferbirne", "f"), "copper_door": ("", "Kupfertür", "f"), "copper_trapdoor": ("", "Kupferfalltür", "f"),
    "copper_bars": ("", "Kupfergitter", "n"), "copper_chain": ("", "Kupferkette", "f"), "copper_chest": ("", "Kupfertruhe", "f"),
    "copper_lantern": ("", "Kupferlaterne", "f"), "copper_golem_statue": ("", "Kupfergolemstatue", "f"),
    "lightning_rod": ("", "Blitzableiter", "m"),
}
CORALS = {"tube": "Orgel", "brain": "Hirn", "bubble": "Blasen", "fire": "Feuer", "horn": "Geweih"}


def copper_name(name):
    words, rest = [], name
    for state in ("waxed", "exposed", "weathered", "oxidized"):
        if rest.startswith(state + "_"):
            words.append(COPPER_STATES[state])
            rest = rest[len(state) + 1:]
    if rest not in COPPER_PARTS or not words:
        return None
    extra, noun, g = COPPER_PARTS[rest]
    if extra:
        words.append(extra)
    text = " ".join(w + ENDING[g] for w in words) + " " + noun
    return text[0].upper() + text[1:]


def coral_name(name):
    m = re.match(r"(dead_)?(tube|brain|bubble|fire|horn)_coral(_fan|_block)?$", name)
    if not m:
        return None
    stem = CORALS[m.group(2)] + "koralle"
    noun, g = {None: (stem, "f"), "_fan": (stem + "nfächer", "m"), "_block": (stem + "nblock", "m")}[m.group(3)]
    return ("Abgestorben" + ENDING[g] + " " if m.group(1) else "") + noun


# ---- Kategorien ----
CATEGORIES = {
    "building": {"de": "Deko & Sonstiges", "en": "Decoration & other"},
    "wood": {"de": "Holz", "en": "Wood"},
    "stone": {"de": "Stein & Ziegel", "en": "Stone & bricks"},
    "colored": {"de": "Farbige Blöcke", "en": "Coloured blocks"},
    "copper": {"de": "Kupfer", "en": "Copper"},
    "redstone": {"de": "Redstone & Schienen", "en": "Redstone & rails"},
}
NATURE = re.compile(r"(leaves|sapling|flower|tulip|orchid|coral|mushroom|fungus|vine|grass|fern|moss|kelp|bush|roots|"
                    r"dripleaf|azalea|petals|lichen|pumpkin|melon|cactus|bamboo$|sugar_cane|reeds|lily|rose|peony|lilac|"
                    r"dandelion|poppy|allium|bluet|daisy|eyeblossom|sprouts|sculk|egg|frog|nest|beehive|dripstone|ice|snow|"
                    r"dirt|mud$|sand$|gravel|clay$|podzol|mycelium|farmland|wart|cocoa|wheat|carrots|potatoes|beetroot|"
                    r"propagule|seagrass|pickle|shrub|waterlily|deadbush|^water$|^lava$|fire$|litter|creaking|hanging_moss)")
REDSTONE = re.compile(r"(redstone|piston|rail|repeater|comparator|observer|dropper|dispenser|hopper|lever|button|"
                      r"pressure_plate|tripwire|daylight|^target$|lamp|^tnt$|crafter|lightning_rod|copper_bulb)")
TECH = re.compile(r"(table|furnace|smoker|chest|barrel|shulker_box|anvil|grindstone|stonecutter|loom|composter|lectern|"
                  r"brewing|cauldron|beacon|conduit|bell$|jukebox|note_?block|campfire|shelf$|bookshelf)")
SPECIAL = re.compile(r"(^air$|barrier|^light$|^light_block|bedrock|command_block|structure|jigsaw|spawner|vault|portal|gateway|"
                     r"dragon_egg|^allow$|^deny$|border_block|test_|head$|skull$|heavy_core)")
MINERAL = re.compile(r"(_ore$|^raw_|^(diamond|emerald|gold|iron|netherite|coal|lapis|amethyst|quartz|resin)_block$|"
                     r"ancient_debris|amethyst)")
STONEISH = re.compile(r"(stone|brick|deepslate|granite|diorite|andesite|tuff|basalt|calcite|prismarine|purpur|quartz|"
                      r"obsidian|netherrack|cinnabar|sulfur|_wall$|terracotta$)")


def wood_of(name):
    for w in sorted(WOODS, key=len, reverse=True):
        if name == w or name.startswith(w + "_") or name.startswith("stripped_" + w + "_"):
            return w
    return None


def color_of(name):
    for c in sorted(COLORS, key=len, reverse=True):
        if name.startswith(c + "_"):
            return c, name[len(c) + 1:]
    return None, None


def german(name):
    if name in MANUAL:
        return MANUAL[name]
    m = re.match(r"light_block_(\d+)$", name)
    if m:
        return f"Lichtblock (Helligkeit {m.group(1)})"
    c, rest = color_of(name)
    if c:
        if rest in COLOR_NOUNS:
            noun, g = COLOR_NOUNS[rest]
            return f"{adj(c, g)} {noun}"
        if rest == "glazed_terracotta":
            return f"{adj(c, 'f')} glasierte Keramik"
        if rest == "candle_cake":
            return f"Kuchen mit {adj(c, 'm').lower()} Kerze"
    w = wood_of(name)
    if w:
        holz, baum = WOODS[w]
        rest = name[len(w) + 1:] if name.startswith(w) else None
        if rest in WOOD_PARTS:
            return holz + WOOD_PARTS[rest]
        if baum:
            if rest == "log": return baum + "stamm"
            if rest == "wood": return holz
            if rest == "leaves": return baum + "laub"
            if rest == "sapling": return baum + "setzling"
            if name == f"stripped_{w}_log": return f"Entrindeter {baum}stamm"
            if name == f"stripped_{w}_wood": return f"Entrindetes {holz}"
        elif w in ("crimson", "warped"):
            if name == f"stripped_{w}_stem": return f"Geschälter {holz}stiel"
            if name == f"stripped_{w}_hyphae": return f"Geschälte {holz}hyphen"
    special = copper_name(name) or coral_name(name)
    if special:
        return special
    for part, suffix in FAMILY_PARTS.items():
        if name.endswith("_" + part):
            base = name[: -len(part) - 1]
            if base in FAMILIES:
                a, noun = FAMILIES[base]
                return (a + " " if a else "") + noun + suffix
    return None


def category(name, old):
    if SPECIAL.search(name): return "special"
    if "copper" in name: return "copper"
    if color_of(name)[0] and not name.startswith(("red_sand", "red_nether", "red_mushroom", "brown_mushroom")): return "colored"
    if wood_of(name) or "poplar" in name: return "wood"
    if REDSTONE.search(name): return "redstone"
    if re.search(r"(_stairs|_slab|_wall|bricks?|tiles)$", name) or name.startswith("infested_"): return "stone"
    if MINERAL.search(name): return "minerals"
    if TECH.search(name): return "tech"
    if NATURE.search(name): return "nature"
    if STONEISH.search(name): return "stone"
    return "building"


# ==========================================================================
# Items (alles, was kein Block ist)
# ==========================================================================
ITEM_SKIP = [
    r"^item\.", r"_cushion$", r"^(agent|npc)_spawn_egg$", r"^hard_", r"^double_stone", r"^stone_block_slab", r"^colored_torch",
    r"^(balloon|bleach|board|chemistry_table|compound|glow_stick|ice_bomb|medicine|photo_item|portfolio|rapid_fertilizer|sparkler)$",
    r"^(banner|banner_pattern|boat|chest_boat|carpet|concrete|concrete_powder|coral|coral_block|coral_fan|coral_fan_dead|"
    r"double_plant|dye|fence|leaves2?|log2?|planks|red_flower|sapling|skull|stained_.*|wood|wooden_slab|wool|tallgrass|"
    r"monster_egg|spawn_egg|netherbrick|stonebrick|light_block|shulker_box|air)$",
]
MATERIALS = {"wooden": "Holz", "stone": "Stein", "copper": "Kupfer", "iron": "Eisen", "golden": "Gold", "diamond": "Diamant",
             "netherite": "Netherit", "leather": "Leder", "chainmail": "Ketten"}
GEAR = {"sword": "schwert", "pickaxe": "spitzhacke", "axe": "axt", "shovel": "schaufel", "hoe": "hacke", "spear": "speer",
        "helmet": "helm", "chestplate": "brustplatte", "leggings": "beinschutz", "boots": "stiefel"}
GEAR_SPECIAL = {"leather_helmet": "Lederkappe", "leather_chestplate": "Lederjacke", "leather_leggings": "Lederhose",
                "chainmail_helmet": "Kettenhaube", "chainmail_chestplate": "Kettenhemd", "chainmail_leggings": "Kettenhose",
                "turtle_helmet": "Schildkrötenpanzer"}
HORSE = {"leather": "Lederne", "copper": "Kupferne", "iron": "Eiserne", "golden": "Goldene", "diamond": "Diamantene",
         "netherite": "Netherit-"}
MOBS = {
    "allay": "Hilfsgeist", "armadillo": "Gürteltier", "axolotl": "Axolotl", "bat": "Fledermaus", "bee": "Bienen",
    "blaze": "Lohen", "bogged": "Sumpfskelett", "breeze": "Böen", "camel": "Kamel", "cat": "Katzen",
    "cave_spider": "Höhlenspinnen", "chicken": "Hühner", "cod": "Kabeljau", "cow": "Kuh", "creaking": "Knarz",
    "creeper": "Creeper", "dolphin": "Delfin", "donkey": "Esel", "drowned": "Ertrunkenen", "elder_guardian": "Großer-Wächter",
    "ender_dragon": "Enderdrachen", "enderman": "Enderman", "endermite": "Endermilben", "evoker": "Magier", "fox": "Fuchs",
    "frog": "Frosch", "ghast": "Ghast", "happy_ghast": "Glücklicher-Ghast", "glow_squid": "Leuchttintenfisch", "goat": "Ziegen",
    "guardian": "Wächter", "hoglin": "Hoglin", "horse": "Pferde", "husk": "Wüstenzombie", "iron_golem": "Eisengolem",
    "llama": "Lama", "magma_cube": "Magmawürfel", "mooshroom": "Mooshroom", "mule": "Maultier", "ocelot": "Ozelot",
    "panda": "Panda", "parrot": "Papageien", "phantom": "Phantom", "pig": "Schweine", "piglin": "Piglin",
    "piglin_brute": "Piglin-Barbaren", "pillager": "Plünderer", "polar_bear": "Eisbären", "pufferfish": "Kugelfisch",
    "rabbit": "Kaninchen", "ravager": "Verwüster", "salmon": "Lachs", "sheep": "Schaf", "shulker": "Shulker",
    "silverfish": "Silberfischchen", "skeleton": "Skelett", "skeleton_horse": "Skelettpferde", "slime": "Schleim",
    "sniffer": "Schnüffler", "snow_golem": "Schneegolem", "spider": "Spinnen", "squid": "Tintenfisch", "stray": "Eiswanderer",
    "strider": "Schreiter", "tadpole": "Kaulquappen", "trader_llama": "Händlerlama", "tropical_fish": "Tropenfisch",
    "turtle": "Schildkröten", "vex": "Plagegeist", "villager": "Dorfbewohner", "vindicator": "Diener",
    "wandering_trader": "Fahrender-Händler", "warden": "Wärter", "witch": "Hexen", "wither": "Wither",
    "wither_skeleton": "Witherskelett", "wolf": "Wolf", "zoglin": "Zoglin", "zombie": "Zombie", "zombie_horse": "Zombiepferde",
    "zombie_villager": "Zombiedorfbewohner", "zombified_piglin": "Zombie-Piglin", "zombie_pigman": "Zombie-Piglin",
    "copper_golem": "Kupfergolem", "nautilus": "Nautilus", "zombie_nautilus": "Zombie-Nautilus",
}
ITEM_MANUAL = {
    "beef": "Rohes Rindfleisch", "porkchop": "Rohes Schweinefleisch", "chicken": "Rohes Hühnchen", "mutton": "Rohes Hammelfleisch",
    "rabbit": "Rohes Kaninchen", "cooked_rabbit": "Gebratenes Kaninchen", "cod": "Roher Kabeljau", "salmon": "Roher Lachs",
    "tropical_fish": "Tropenfisch", "pufferfish": "Kugelfisch", "rotten_flesh": "Verrottetes Fleisch",
    "spider_eye": "Spinnenauge", "fermented_spider_eye": "Fermentiertes Spinnenauge", "poisonous_potato": "Giftige Kartoffel",
    "beetroot": "Rote Bete", "beetroot_soup": "Borschtsch", "beetroot_seeds": "Rote-Bete-Samen", "mushroom_stew": "Pilzsuppe",
    "rabbit_stew": "Kaninchenragout", "suspicious_stew": "Seltsame Suppe", "chorus_fruit": "Chorusfrucht",
    "popped_chorus_fruit": "Geplatzte Chorusfrucht", "dried_kelp": "Getrockneter Seetang", "glow_berries": "Leuchtbeeren",
    "glistering_melon_slice": "Glitzernde Melonenscheibe", "melon_seeds": "Melonenkerne", "pumpkin_seeds": "Kürbiskerne",
    "torchflower_seeds": "Fackelliliensamen", "pitcher_pod": "Kannenpflanzenkapsel", "cocoa_beans": "Kakaobohnen",
    "raw_iron": "Roheisen", "raw_gold": "Rohgold", "raw_copper": "Rohkupfer", "iron_nugget": "Eisenklumpen",
    "gold_nugget": "Goldklumpen", "copper_nugget": "Kupferklumpen", "netherite_scrap": "Netheritplatten",
    "echo_shard": "Echoscherbe", "prismarine_shard": "Prismarinscherbe", "prismarine_crystals": "Prismarinkristalle",
    "blaze_powder": "Lohenstaub", "breeze_rod": "Böenrute", "magma_cream": "Magmacreme", "dragon_breath": "Drachenatem",
    "ink_sac": "Tintenbeutel", "glow_ink_sac": "Leuchttintenbeutel", "honeycomb": "Honigwabe", "rabbit_foot": "Hasenpfote",
    "rabbit_hide": "Kaninchenfell", "armadillo_scute": "Gürteltier-Hornschild", "turtle_scute": "Schildkröten-Hornschild",
    "goat_horn": "Ziegenhorn", "disc_fragment_5": "Plattenbruchstück", "resin_brick": "Harzziegel",
    "nether_brick": "Netherziegel (Einzelstück)", "brush": "Pinsel", "recovery_compass": "Bergungskompass",
    "lodestone_compass": "Leitstein-Kompass", "filled_map": "Karte", "empty_map": "Leere Karte",
    "firework_star": "Feuerwerksstern", "written_book": "Beschriebenes Buch", "knowledge_book": "Buch des Wissens",
    "debug_stick": "Debug-Stab", "tipped_arrow": "Getränkter Pfeil", "splash_potion": "Wurftrank",
    "lingering_potion": "Verweiltrank", "ominous_bottle": "Unheilvolle Flasche", "trial_key": "Prüfungsschlüssel",
    "ominous_trial_key": "Unheilvoller Prüfungsschlüssel", "wolf_armor": "Wolfspanzer",
    "warped_fungus_on_a_stick": "Wirrpilzrute", "powder_snow_bucket": "Pulverschneeeimer", "cod_bucket": "Kabeljaueimer",
    "salmon_bucket": "Lachseimer", "pufferfish_bucket": "Kugelfischeimer", "tropical_fish_bucket": "Tropenfischeimer",
    "tadpole_bucket": "Kaulquappeneimer", "furnace_minecart": "Ofenlore", "hopper_minecart": "Trichterlore",
    "tnt_minecart": "TNT-Lore", "command_block_minecart": "Befehlsblocklore", "blue_egg": "Blaues Ei", "brown_egg": "Braunes Ei",
    "glow_item_frame": "Leuchtrahmen", "bamboo_raft": "Bambusfloß", "bamboo_chest_raft": "Bambustruhenfloß",
    "bundle": "Bündel",
}
ITEM_CATEGORIES = {
    "eggs": {"de": "Spawn-Eier", "en": "Spawn eggs"},
    "music": {"de": "Schallplatten", "en": "Music discs"},
    "patterns": {"de": "Farbstoffe, Scherben & Vorlagen", "en": "Dyes, sherds & templates"},
}
FOOD = re.compile(r"(^cooked_|beef|porkchop|chicken$|mutton|rabbit$|^cod$|^salmon$|tropical_fish$|pufferfish$|stew|soup|"
                  r"apple|bread|carrot$|potato|melon_slice|berries|cookie|pie|chorus_fruit|dried_kelp|honey_bottle|"
                  r"milk_bucket|rotten_flesh|spider_eye$|^beetroot$)")


def item_german(name):
    if name in ITEM_MANUAL: return ITEM_MANUAL[name]
    if name in GEAR_SPECIAL: return GEAR_SPECIAL[name]
    m = re.match(r"(.+)_spawn_egg$", name)
    if m:
        return MOBS[m.group(1)] + "-Spawn-Ei" if m.group(1) in MOBS else None
    m = re.match(r"music_disc_(.+)$", name)
    if m: return f"Schallplatte ({m.group(1).replace('_', ' ')})"
    m = re.match(r"(.+)_pottery_sherd$", name)
    if m: return f"Töpferscherbe ({m.group(1).replace('_', ' ')})"
    m = re.match(r"(.+)_armor_trim_smithing_template$", name)
    if m: return f"Schmiedevorlage ({m.group(1)})"
    if name == "netherite_upgrade_smithing_template": return "Schmiedevorlage (Netheritaufwertung)"
    m = re.match(r"(.+)_banner_pattern$", name)
    if m: return f"Bannervorlage ({m.group(1).replace('_', ' ')})"
    for mat, de in MATERIALS.items():
        if name.startswith(mat + "_"):
            rest = name[len(mat) + 1:]
            if rest in GEAR: return de + GEAR[rest]
            if rest == "horse_armor" and mat in HORSE:
                return HORSE[mat] + ("" if HORSE[mat].endswith("-") else " ") + "Pferderüstung"
            if rest == "nautilus_armor": return de + "-Nautilusrüstung"
    c, rest = color_of(name)
    if c:
        if rest == "dye": return f"{adj(c, 'm')} Farbstoff"
        if rest == "bundle": return f"{adj(c, 'n')} Bündel"
        if rest == "harness": return f"{adj(c, 'n')} Geschirr"
    w = wood_of(name)
    if w and WOODS[w][1]:
        if name == w + "_boat": return WOODS[w][0] + "boot"
        if name == w + "_chest_boat": return WOODS[w][0] + "truhenboot"
        if name == w + "_sign": return WOODS[w][0] + "schild"
    if name in ("bamboo_sign", "crimson_sign", "warped_sign"):
        return WOODS[name.split("_")[0]][0] + "schild"
    return german(name)          # z. B. comparator, repeater, sugar_cane


def item_category(name):
    if name.endswith("_spawn_egg"): return "eggs"
    if name.startswith("music_disc") or name == "disc_fragment_5": return "music"
    if re.search(r"(pottery_sherd|smithing_template|banner_pattern|_dye$)", name): return "patterns"
    if re.search(r"(helmet|chestplate|leggings|boots|_armor$|elytra|harness|saddle)", name): return "armor"
    if re.search(r"(sword|spear|^bow$|crossbow|arrow|trident|mace|shield|wind_charge|snowball)", name): return "weapons"
    if re.search(r"(pickaxe|_axe$|shovel|_hoe$|shears|fishing_rod|flint_and_steel|bucket$|compass|clock|spyglass|brush)", name):
        return "food" if name == "milk_bucket" else "tools"
    if FOOD.search(name): return "food"
    if re.search(r"(boat|raft|minecart|map|book|potion|bottle|bundle|firework|lead|name_tag|key|sign$|frame$|painting|"
                 r"armor_stand|ender_|end_crystal|totem|on_a_stick|comparator|repeater)", name): return "useful"
    if re.search(r"(seeds|pod$|cocoa|sugar_cane|egg$)", name): return "nature"
    return "materials"


def main():
    root, jv, bv = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    load = lambda p: json.loads((root / "data" / p).read_text())
    jb = {b["name"]: b["displayName"] for b in load(f"pc/{jv}/blocks.json")}
    bb = {b["name"]: b["displayName"] for b in load(f"bedrock/{bv}/blocks.json")}
    ji = {i["name"] for i in load(f"pc/{jv}/items.json")}
    bi = {i["name"] for i in load(f"bedrock/{bv}/items.json")}

    catalog = json.loads(CATALOG.read_text())
    old_entries = catalog["entries"]
    old_items = {e[0]: e for e in old_entries if (e[4] if len(e) > 4 else "i") == "i"}
    jin = {i["name"]: i["displayName"] for i in load(f"pc/{jv}/items.json")}
    bin_ = {i["name"]: i["displayName"] for i in load(f"bedrock/{bv}/items.json")}
    old_cat = {e[0]: e[3] for e in old_entries if len(e) > 4 and "b" in e[4]}

    iskip = lambda n: any(re.search(p, n) for p in ITEM_SKIP)
    j_items = {n for n in jin if n not in jb and not iskip(n)}
    b_items = {n for n in bin_ if n not in bb and not iskip(n)}
    item_ids = j_items | b_items
    items_only, istats = [], {"de": 0, "en": 0}
    for name in sorted(item_ids):
        en = jin.get(name) or bin_[name]
        if name.startswith("music_disc_"):
            en = f"Music Disc ({name[11:].replace('_', ' ')})"
        old = old_items.get(name)
        de = (old[1] if old and old[1] != old[2] else None) or item_german(name)
        istats["de" if de else "en"] += 1
        entry = [name, de or en, en, old[3] if old and old[3] in catalog["categories"] and old[3] not in ("building", "minerals", "tech", "special") else item_category(name)]
        if name not in b_items: entry += ["i", "j"]
        elif name not in j_items: entry += ["i", "b"]
        items_only.append(entry)
    skip = lambda n: n not in KEEP and any(re.search(p, n) for p in SKIP)
    out, stats = [], {"de": 0, "en": 0}

    def add(name, en, edition, is_item):
        ref = ALIAS.get(name, name) if edition == "b" else name
        de = german(name) or german(ref)
        stats["de" if de else "en"] += 1
        entry = [name, de or en, en, category(ref, old_cat), "ib" if is_item else "b"]
        if edition:
            entry.append(edition)
        out.append(entry)

    for name in sorted(set(jb) | set(bb)):
        if skip(name):
            continue
        in_j, in_b = name in jb, name in bb
        if name == "snow":                       # gleiche ID, anderer Block: Java = Schneeschicht, Bedrock = Schneeblock
            out.append(["snow", "Schnee (dünne Schicht)", "Snow (thin layer)", "nature", "ib", "j"])
            out.append(["snow", "Schneeblock", "Snow Block", "nature", "ib", "b"])
            stats["de"] += 2
        elif in_j and in_b:
            add(name, jb[name], "", name in ji or name in bi)
        elif in_j:
            add(name, jb[name], "j", name in ji)
        else:
            add(name, bb[name], "b", name in bi)

    catalog["categories"].update(ITEM_CATEGORIES)
    for key, val in CATEGORIES.items():
        catalog["categories"][key] = val
    catalog["entries"] = items_only + out
    catalog["blockSource"] = {"java": jv, "bedrock": bv, "quelle": "PrismarineJS/minecraft-data (nur IDs und englische Namen)"}

    lines = ",\n".join("    " + json.dumps(e, ensure_ascii=False) for e in catalog["entries"])
    head = {k: v for k, v in catalog.items() if k != "entries"}
    text = json.dumps(head, ensure_ascii=False, indent=2)[:-2] + ',\n  "entries": [\n' + lines + "\n  ]\n}\n"
    CATALOG.write_text(text)
    print(f"{len(out)} Blöcke geschrieben ({stats['de']} mit deutschem Namen, {stats['en']} mit englischem), "
          f"{len(items_only)} reine Items ({istats['de']} deutsch, {istats['en']} englisch).")


if __name__ == "__main__":
    main()
