# --- MODULE 2: THE LIBRARIAN + MODULE 1: THE ASTROLOGER + STATS ---

from notion_client import Client
import swisseph as se
import pytz
import os 
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ==========================================================
# 1. EPHEMERIS SETUP
# ==========================================================
script_folder = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(script_folder, 'ephe') + os.path.sep
se.set_ephe_path(ephe_path)

# ==========================================================
# 2. CONFIGURATION
# ==========================================================
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Weighting System
PLANET_POINTS = {
    "Sun": 4, "Moon": 4, "Ascendant": 4, "Midheaven": 1,
    "Mercury": 2, "Venus": 2, "Mars": 2,
    "Jupiter": 1, "Saturn": 1, "Uranus": 1, "Neptune": 1, "Pluto": 1,
    "North Node": 0, "South Node": 0, "Lilith": 0, "Chiron": 0, "Part of Fortune": 0
}

PLANETS = {
    se.SUN: "Sun", se.MOON: "Moon", se.MERCURY: "Mercury", se.VENUS: "Venus",
    se.MARS: "Mars", se.JUPITER: "Jupiter", se.SATURN: "Saturn", se.URANUS: "Uranus",
    se.NEPTUNE: "Neptune", se.PLUTO: "Pluto", se.TRUE_NODE: "North Node",
    se.MEAN_APOG: "Lilith", se.CHIRON: "Chiron"
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Mapping Signs
SIGN_DATA = {
    "Aries":       ("Hot", "Dry", "Choleric", "Fire", "Cardinal", "Yang"),
    "Taurus":      ("Cold", "Dry", "Melancholic", "Earth", "Fixed", "Yin"),
    "Gemini":      ("Hot", "Wet", "Sanguine", "Air", "Mutable", "Yang"),
    "Cancer":      ("Cold", "Wet", "Phlegmatic", "Water", "Cardinal", "Yin"),
    "Leo":         ("Hot", "Dry", "Choleric", "Fire", "Fixed", "Yang"),
    "Virgo":       ("Cold", "Dry", "Melancholic", "Earth", "Mutable", "Yin"),
    "Libra":       ("Hot", "Wet", "Sanguine", "Air", "Cardinal", "Yang"),
    "Scorpio":     ("Cold", "Wet", "Phlegmatic", "Water", "Fixed", "Yin"),
    "Sagittarius": ("Hot", "Dry", "Choleric", "Fire", "Mutable", "Yang"),
    "Capricorn":   ("Cold", "Dry", "Melancholic", "Earth", "Cardinal", "Yin"),
    "Aquarius":    ("Hot", "Wet", "Sanguine", "Air", "Fixed", "Yang"),
    "Pisces":      ("Cold", "Wet", "Phlegmatic", "Water", "Mutable", "Yin")
}

def get_sign_name(lon):
    return ZODIAC_SIGNS[int(lon // 30)]

def normalize_degree(degree):
    return degree % 360

def get_ordinal(n):
    if 11 <= (n % 100) <= 13: suffix = 'th'
    else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def get_aspect(lon1, lon2):
    diff = abs(lon1 - lon2)
    if diff > 180: diff = 360 - diff 
    if diff <= 8: return "Conjunction"
    elif 172 <= diff <= 180: return "Opposition"
    elif 82 <= diff <= 98: return "Square"
    elif 112 <= diff <= 128: return "Trine"
    elif 54 <= diff <= 66: return "Sextile"
    return None

def calculate_houses_safe(jd_utc, lat, lon):
    for hsys in [b'P', 'P', 80]: 
        try:
            cusps, ascmc = se.houses(float(jd_utc), float(lat), float(lon), hsys)
            return cusps, ascmc
        except Exception:
            continue 
    raise ValueError("Could not calculate Houses.")

def get_house_number(planet_lon, cusps, apply_rule=False):
    planet_lon = normalize_degree(planet_lon)
    start_idx = 1 if len(cusps) == 13 else 0
    for i in range(12):
        curr_ptr = start_idx + i
        next_ptr = start_idx + i + 1
        if next_ptr >= len(cusps): next_ptr = start_idx   
        cusp_curr = normalize_degree(cusps[curr_ptr])
        cusp_next = normalize_degree(cusps[next_ptr])
        
        in_this_house = False
        if cusp_next < cusp_curr:
            if planet_lon >= cusp_curr or planet_lon < cusp_next: in_this_house = True
        else:
            if cusp_curr <= planet_lon < cusp_next: in_this_house = True
            
        if in_this_house:
            if not apply_rule: return float(i + 1)
            dist_to_next = normalize_degree(cusp_next - planet_lon)
            if dist_to_next <= 5.0:
                next_house = 1 if (i + 1) == 12 else (i + 2)
                return float(next_house)
            else: return float(i + 1)
    return 0.0

def get_moon_phase(sun_lon, moon_lon):
    diff = normalize_degree(moon_lon - sun_lon)
    if diff >= 345 or diff < 15: return "New Moon"
    elif 165 <= diff < 195: return "Full Moon"
    elif 15 <= diff < 165: return "Waxing Moon"
    else: return "Waning Moon"

def get_astrology_data(client_data):
    data = { 
        "placements": {}, 
        "degrees": {}, 
        "house_positions_geom": {}, 
        "house_positions_eff": {},
        "cusps": [], 
        "moon_phase": "" 
    }
    
    local_tz = pytz.timezone('Europe/Lisbon')
    dt_local = local_tz.localize(datetime(
        client_data["year"], client_data["month"], client_data["day"],
        client_data["hour"], client_data["minute"], 0
    ))
    dt_utc = dt_local.astimezone(pytz.utc)
    jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                       dt_utc.hour + dt_utc.minute/60.0)

    print(f"...Calculating Chart for {client_data['name']}...")
    cusps, ascmc = calculate_houses_safe(jd_utc, client_data["latitude"], client_data["longitude"])
    data["cusps"] = cusps
    
    # Angles
    data["placements"]["Ascendant"] = get_sign_name(ascmc[0])
    data["degrees"]["Ascendant"] = ascmc[0]
    data["placements"]["Midheaven"] = get_sign_name(ascmc[1])
    data["degrees"]["Midheaven"] = ascmc[1]
    # Midheaven House (Effective)
    mc_eff = get_house_number(ascmc[1], cusps, apply_rule=True)
    data["house_positions_eff"]["Midheaven"] = mc_eff
    
    sun_lon = 0
    moon_lon = 0

    print("\n--- Planet Positions (Debug) ---")
    for planet_id, name in PLANETS.items():
        try:
            result = se.calc_ut(jd_utc, planet_id)
            lon_val = result[0][0]
            data["degrees"][name] = lon_val
            data["placements"][name] = get_sign_name(lon_val)
            
            h_geom = get_house_number(lon_val, cusps, apply_rule=False)
            data["house_positions_geom"][name] = h_geom
            
            h_eff = get_house_number(lon_val, cusps, apply_rule=True)
            data["house_positions_eff"][name] = h_eff
            
            if h_geom != h_eff:
                print(f"  > {name}: Geom House {int(h_geom)} -> Effective House {int(h_eff)} (Rule Applied)")
            else:
                print(f"  > {name}: House {int(h_geom)}")
            
            if name == "Sun": sun_lon = lon_val
            if name == "Moon": moon_lon = lon_val
        except se.Error:
            data["placements"][name] = "Error"
            data["house_positions_geom"][name] = 0.0
            data["house_positions_eff"][name] = 0.0

    data["moon_phase"] = get_moon_phase(sun_lon, moon_lon)

    # South Node Calculation
    if "North Node" in data["degrees"]:
        nn_deg = data["degrees"]["North Node"]
        sn_deg = normalize_degree(nn_deg + 180)
        data["degrees"]["South Node"] = sn_deg
        data["placements"]["South Node"] = get_sign_name(sn_deg)
        data["house_positions_eff"]["South Node"] = get_house_number(sn_deg, cusps, apply_rule=True)

    # Part of Fortune
    sun_house = get_house_number(sun_lon, cusps, apply_rule=False)
    is_day_chart = True if sun_house >= 7.0 else False

    if is_day_chart:
        pof_lon = normalize_degree(ascmc[0] + moon_lon - sun_lon)
    else:
        pof_lon = normalize_degree(ascmc[0] + sun_lon - moon_lon)
            
    data["placements"]["Part of Fortune"] = get_sign_name(pof_lon)
    data["degrees"]["Part of Fortune"] = pof_lon
    
    pof_geom = get_house_number(pof_lon, cusps, apply_rule=False)
    pof_eff = get_house_number(pof_lon, cusps, apply_rule=True)
    data["house_positions_geom"]["Part of Fortune"] = pof_geom
    data["house_positions_eff"]["Part of Fortune"] = pof_eff
    
    return data

# --- STATS LOGIC ---

def get_label(pct, name_high, name_low):
    if 45 <= pct <= 55: return "Balanced"
    if pct > 55:
        if pct >= 70: return f"Dominant {name_high}"
        else: return f"Prominent {name_high}"
    else:
        low_pct = 100 - pct
        if low_pct >= 70: return f"Dominant {name_low}"
        else: return f"Prominent {name_low}"

def calculate_hemisphere_stats(house_data):
    sup_score = 0
    total_score = 0
    for planet, house_float in house_data.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or house_float == 0.0: continue
        total_score += points
        if house_float >= 7.0: sup_score += points
            
    if total_score > 0:
        sup_pct = int(round((sup_score / total_score) * 100))
        inf_pct = 100 - sup_pct
    else:
        sup_pct, inf_pct = 0, 0
    
    status = get_label(sup_pct, "Superior", "Inferior")
    return { "Superior": sup_pct, "Inferior": inf_pct, "Status": status }

def calculate_east_west_stats(house_data):
    east_score = 0
    total_score = 0
    east_houses = [10, 11, 12, 1, 2, 3]
    for planet, house_float in house_data.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or house_float == 0.0: continue
        total_score += points
        if int(house_float) in east_houses: east_score += points
            
    if total_score > 0:
        east_pct = int(round((east_score / total_score) * 100))
        west_pct = 100 - east_pct
    else:
        east_pct, west_pct = 0, 0
        
    status = get_label(east_pct, "Eastern", "Western")
    return { "East": east_pct, "West": west_pct, "Status": status }

def calculate_primitive_stats(placements):
    scores = {"Hot": 0, "Cold": 0, "Wet": 0, "Dry": 0}
    total_score = 0
    for planet, sign in placements.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or sign == "Error": continue
        temp, moist, _, _, _, _ = SIGN_DATA.get(sign, (None, None, None, None, None, None))
        if temp:
            total_score += points
            scores[temp] += points
            scores[moist] += points
    
    if total_score > 0:
        hot_pct = int(round((scores["Hot"] / total_score) * 100))
        cold_pct = 100 - hot_pct
        wet_pct = int(round((scores["Wet"] / total_score) * 100))
        dry_pct = 100 - wet_pct
    else:
        hot_pct, cold_pct, wet_pct, dry_pct = 0, 0, 0, 0
        
    temp_winner = "Hot" if hot_pct >= 50 else "Cold"
    moist_winner = "Wet" if wet_pct >= 50 else "Dry"
    combined_status = f"{temp_winner} & {moist_winner}"
    
    return {
        "Temperature": {"Hot": hot_pct, "Cold": cold_pct, "Status": get_label(hot_pct, "Hot", "Cold")},
        "Moisture": {"Wet": wet_pct, "Dry": dry_pct, "Status": get_label(wet_pct, "Wet", "Dry")},
        "Status": combined_status
    }

def calculate_temperament_stats(placements):
    scores = {"Choleric": 0, "Melancholic": 0, "Sanguine": 0, "Phlegmatic": 0}
    total_score = 0
    for planet, sign in placements.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or sign == "Error": continue
        _, _, temp_name, _, _, _ = SIGN_DATA.get(sign, (None, None, None, None, None, None))
        if temp_name:
            total_score += points
            scores[temp_name] += points
            
    stats = {}
    if total_score > 0:
        for temp, score in scores.items():
            stats[temp] = int(round((score / total_score) * 100))
    else:
        stats = {k: 0 for k in scores}
    return { "Breakdown": stats, "Primary": max(stats, key=stats.get) }

def calculate_element_stats(placements):
    scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    total_score = 0
    for planet, sign in placements.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or sign == "Error": continue
        _, _, _, element_name, _, _ = SIGN_DATA.get(sign, (None, None, None, None, None, None))
        if element_name:
            total_score += points
            scores[element_name] += points
            
    stats = {}
    if total_score > 0:
        for el, score in scores.items():
            stats[el] = int(round((score / total_score) * 100))
    else:
        stats = {k: 0 for k in scores}
    return { "Breakdown": stats, "Primary": max(stats, key=stats.get) }

def calculate_modality_stats(placements):
    scores = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    total_score = 0
    for planet, sign in placements.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or sign == "Error": continue
        _, _, _, _, mode_name, _ = SIGN_DATA.get(sign, (None, None, None, None, None, None))
        if mode_name:
            total_score += points
            scores[mode_name] += points
            
    stats = {}
    if total_score > 0:
        stats["Cardinal"] = int(round((scores["Cardinal"] / total_score) * 100))
        stats["Fixed"] = int(round((scores["Fixed"] / total_score) * 100))
        stats["Mutable"] = 100 - (stats["Cardinal"] + stats["Fixed"])
    else:
        stats = {k: 0 for k in scores}
    return { "Breakdown": stats, "Primary": max(stats, key=stats.get) }

def calculate_polarity_stats(placements):
    scores = {"Yang": 0, "Yin": 0}
    total_score = 0
    for planet, sign in placements.items():
        points = PLANET_POINTS.get(planet, 0)
        if points == 0 or sign == "Error": continue
        _, _, _, _, _, pol_name = SIGN_DATA.get(sign, (None, None, None, None, None, None))
        if pol_name:
            total_score += points
            scores[pol_name] += points
            
    if total_score > 0:
        yang_pct = int(round((scores["Yang"] / total_score) * 100))
        yin_pct = 100 - yang_pct
    else:
        yang_pct, yin_pct = 0, 0
        
    status = get_label(yang_pct, "Yang", "Yin")
    return { "Yang": yang_pct, "Yin": yin_pct, "Status": status }

def get_summary_table_by_house(chart_data):
    table = "| Sign on Cusp | Planets in House | House |\n"
    table += "| :--- | :--- | :--- |\n"
    cusps = chart_data["cusps"]
    h_eff = chart_data["house_positions_eff"]
    start_idx = 1 if len(cusps) == 13 else 0
    for i in range(12):
        house_num = i + 1
        house_str = get_ordinal(house_num)
        cusp_degree = cusps[start_idx + i]
        cusp_sign = get_sign_name(normalize_degree(cusp_degree))
        planets_here = []
        for body, h_val in h_eff.items():
            if body in ["Ascendant", "Midheaven"]: continue
            if int(h_val) == house_num: planets_here.append(body)
        planets_str = ", ".join(planets_here)
        table += f"| {cusp_sign} | {planets_str} | {house_str} |\n"
    return table

def get_notion_content(placement_name):
    if len(NOTION_TOKEN) < 10: return "[Error: Check Token]"
    notion = Client(auth=NOTION_TOKEN)
    try:
        results = notion.databases.query(
            database_id=DATABASE_ID, 
            filter={ "property": "Placement", "title": { "equals": placement_name } }
        )
        if not results["results"]: return f"\n[No content found for: {placement_name}]"
        page = results["results"][0]
        if not page["properties"]["Description"]["rich_text"]: return f"\n[Text empty]"
        return "".join([t["plain_text"] for t in page["properties"]["Description"]["rich_text"]])
    except Exception as e:
        return f"\n[Notion API Error: {e}]"

# ==========================================================
# MAIN FLOW
# ==========================================================
if __name__ == "__main__":
    
    client_data = {
        "name": "Adriana Capeto Campos",
        "year": 1971, "month": 5, "day": 18,
        "hour": 8, "minute": 30,
        "city": "Lisbon", "latitude": 38.7223, "longitude": -9.1393
    }
    
    print("\n" + "="*50)
    print(f"🤖 Generating Full Report for: {client_data['name']}")
    print("="*50)

    try:
        chart_data = get_astrology_data(client_data)
        
        hemi_stats = calculate_hemisphere_stats(chart_data["house_positions_geom"])
        east_west_stats = calculate_east_west_stats(chart_data["house_positions_geom"])
        prim_stats = calculate_primitive_stats(chart_data["placements"])
        temp_stats = calculate_temperament_stats(chart_data["placements"])
        elem_stats = calculate_element_stats(chart_data["placements"])
        mode_stats = calculate_modality_stats(chart_data["placements"])
        pol_stats = calculate_polarity_stats(chart_data["placements"])
        
        print("\n📈 FINAL RESULTS (All 7 Charts + Moon Phase):")
        print(f"1. N/S: {hemi_stats['Status']}")
        print(f"2. E/W: {east_west_stats['Status']}")
        print(f"3. Qualities: {prim_stats['Status']}")
        print(f"4. Temperament: {temp_stats['Primary']}")
        print(f"5. Elements: {elem_stats['Primary']}")
        print(f"6. Modalities: {mode_stats['Primary']}")
        print(f"7. Polarities: {pol_stats['Status']}")
        print(f"🌑 Moon Phase: {chart_data['moon_phase']}")
        print("-" * 30)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        exit()
    
    # Formatting Helper
    sep = "-" * 30 + "\n"
    
    chapter_content = f"Chart for: {client_data['name']}\n\n"
    
    # --- SECTION: CHART DATA ---
    chapter_content += sep + "# Chart Data\n" + sep + "\n"
    chapter_content += "### Planets in Signs\n"
    for body, sign in chart_data["placements"].items():
        chapter_content += f"* **{body}:** {sign}\n"
    
    chapter_content += "\n### Planets in Houses (Effective)\n"
    for body, h_pos in chart_data["house_positions_eff"].items():
        if body in ["Ascendant", "Midheaven"] or h_pos == 0.0: continue
        ordinal_house = get_ordinal(int(h_pos))
        chapter_content += f"* **{body}:** {ordinal_house} House\n"
    chapter_content += "\n"

    # --- CHAPTER 1 ---
    chapter_content += sep + "# Chapter 1: Pillars of Personality\n" + sep + "\n"
    
    asc_sign = chart_data["placements"]["Ascendant"]
    asc_key = f"Ascendant in {asc_sign}"
    print(f"-> Fetching text for: {asc_key}...")
    chapter_content += f"## {asc_key}\n{get_notion_content(asc_key)}\n\n"
    
    sun_sign = chart_data["placements"]["Sun"]
    sun_key = f"Sun in {sun_sign}"
    print(f"-> Fetching text for: {sun_key}...")
    chapter_content += f"## {sun_key}\n{get_notion_content(sun_key)}\n\n"
    
    moon_sign = chart_data["placements"]["Moon"]
    moon_key = f"Moon in {moon_sign}"
    print(f"-> Fetching text for: {moon_key}...")
    chapter_content += f"## {moon_key}\n{get_notion_content(moon_key)}\n\n"

    # --- CHAPTER 2 ---
    chapter_content += sep + "# Chapter 2: Astrological Statistics (Pie Charts)\n" + sep + "\n"
    
    chapter_content += "## Your Superior & Inferior Hemisphere Count\n"
    chapter_content += f"Status: **{hemi_stats['Status']}**\n"
    chapter_content += f"(Superior: {hemi_stats['Superior']}% / Inferior: {hemi_stats['Inferior']}%)\n\n"
    
    chapter_content += "## Your Eastern & Western Hemisphere Count\n"
    chapter_content += f"Status: **{east_west_stats['Status']}**\n"
    chapter_content += f"(Eastern: {east_west_stats['East']}% / Western: {east_west_stats['West']}%)\n\n"
    
    chapter_content += "## Your Primitive Qualities Count\n"
    chapter_content += f"Status: **{prim_stats['Status']}**\n"
    chapter_content += f"Temperature Status: **{prim_stats['Temperature']['Status']}**\n"
    chapter_content += f"(Hot: {prim_stats['Temperature']['Hot']}% / Cold: {prim_stats['Temperature']['Cold']}%)\n"
    chapter_content += f"Moisture Status: **{prim_stats['Moisture']['Status']}**\n"
    chapter_content += f"(Wet: {prim_stats['Moisture']['Wet']}% / Dry: {prim_stats['Moisture']['Dry']}%)\n\n"

    chapter_content += "## Your Temperaments Count\n"
    chapter_content += f"Primary Temperament: **{temp_stats['Primary']}**\n"
    chapter_content += f"Choleric: {temp_stats['Breakdown']['Choleric']}%\n"
    chapter_content += f"Sanguine: {temp_stats['Breakdown']['Sanguine']}%\n"
    chapter_content += f"Melancholic: {temp_stats['Breakdown']['Melancholic']}%\n"
    chapter_content += f"Phlegmatic: {temp_stats['Breakdown']['Phlegmatic']}%\n\n"

    chapter_content += "## Your Elements Count\n"
    chapter_content += f"Primary Element: **{elem_stats['Primary']}**\n"
    chapter_content += f"Fire: {elem_stats['Breakdown']['Fire']}%\n"
    chapter_content += f"Earth: {elem_stats['Breakdown']['Earth']}%\n"
    chapter_content += f"Air: {elem_stats['Breakdown']['Air']}%\n"
    chapter_content += f"Water: {elem_stats['Breakdown']['Water']}%\n\n"

    chapter_content += "## Your Modalities Count\n"
    chapter_content += f"Primary Modality: **{mode_stats['Primary']}**\n"
    chapter_content += f"Cardinal: {mode_stats['Breakdown']['Cardinal']}%\n"
    chapter_content += f"Fixed: {mode_stats['Breakdown']['Fixed']}%\n"
    chapter_content += f"Mutable: {mode_stats['Breakdown']['Mutable']}%\n\n"

    chapter_content += "## Your Polarities Count\n"
    chapter_content += f"Status: **{pol_stats['Status']}**\n"
    chapter_content += f"(Yang: {pol_stats['Yang']}% / Yin: {pol_stats['Yin']}%)\n\n"

    # --- CHAPTER 3 ---
    moon_key = chart_data['moon_phase']
    print(f"-> Fetching text for: {moon_key}...")
    moon_text = get_notion_content(moon_key)
    chapter_content += sep + "# Chapter 3: The Moon Phase\n" + sep + "\n"
    chapter_content += f"## Your Moon Phase: {moon_key}\n"
    chapter_content += f"{moon_text}\n\n"

    # --- CHAPTER 4 ---
    chapter_content += sep + "# Chapter 4: The 12 Houses\n" + sep + "\n"
    cusps = chart_data["cusps"]
    start_idx = 1 if len(cusps) == 13 else 0
    for i in range(12):
        house_num = i + 1
        ordinal_house = get_ordinal(house_num)
        cusp_degree = cusps[start_idx + i]
        cusp_sign = get_sign_name(normalize_degree(cusp_degree))
        cusp_key = f"{cusp_sign} in the {ordinal_house} House"
        print(f"-> Fetching text for: {cusp_key}...")
        content = get_notion_content(cusp_key)
        chapter_content += f"## {cusp_key}\n{content}\n\n"

    # --- CHAPTER 5 ---
    chapter_content += sep + "# Chapter 5: Chart Summary Data\n" + sep + "\n"
    chapter_content += get_summary_table_by_house(chart_data)
    chapter_content += "\n\n"

    # --- CHAPTER 6 ---
    chapter_content += sep + "# Chapter 6: The Ascendant\n" + sep + "\n"
    chapter_content += f"## {asc_key}\n{get_notion_content(asc_key)}\n\n"

    # --- CHAPTER 7: SUN ---
    chapter_content += sep + "# Chapter 7: The Sun\n" + sep + "\n"
    sun_h = chart_data["house_positions_eff"]["Sun"]
    sun_h_str = get_ordinal(int(sun_h))
    sun_house_key = f"Sun in the {sun_h_str} House"
    print(f"-> Fetching text for: {sun_house_key}...")
    chapter_content += f"## {sun_house_key}\n{get_notion_content(sun_house_key)}\n\n"
    
    print(f"-> Fetching text for: {sun_key}...")
    chapter_content += f"## {sun_key}\n{get_notion_content(sun_key)}\n\n"
    
    chapter_content += "## Sun Aspects\n"
    sun_deg = chart_data["degrees"]["Sun"]
    found_aspect = False
    for planet, deg in chart_data["degrees"].items():
        if planet == "Sun" or planet in ["Part of Fortune"]: continue
        aspect_name = get_aspect(sun_deg, deg)
        if aspect_name:
            aspect_key = f"Sun {aspect_name} {planet}"
            print(f"-> Fetching text for: {aspect_key}...")
            aspect_text = get_notion_content(aspect_key)
            chapter_content += f"### {aspect_key}\n{aspect_text}\n\n"
            found_aspect = True
    if not found_aspect: chapter_content += "No major aspects to the Sun found.\n\n"

    # --- CHAPTER 8: MOON ---
    chapter_content += sep + "# Chapter 8: The Moon\n" + sep + "\n"
    moon_h = chart_data["house_positions_eff"]["Moon"]
    moon_h_str = get_ordinal(int(moon_h))
    moon_house_key = f"Moon in the {moon_h_str} House"
    print(f"-> Fetching text for: {moon_house_key}...")
    chapter_content += f"## {moon_house_key}\n{get_notion_content(moon_house_key)}\n\n"
    
    moon_sign_key = f"Moon in {chart_data['placements']['Moon']}"
    print(f"-> Fetching text for: {moon_sign_key}...")
    chapter_content += f"## {moon_sign_key}\n{get_notion_content(moon_sign_key)}\n\n"
    
    chapter_content += "## Moon Aspects\n"
    moon_deg = chart_data["degrees"]["Moon"]
    found_moon_aspect = False
    for planet, deg in chart_data["degrees"].items():
        if planet == "Moon" or planet in ["Part of Fortune"]: continue
        aspect_name = get_aspect(moon_deg, deg)
        if aspect_name:
            aspect_key = f"Moon {aspect_name} {planet}"
            print(f"-> Fetching text for: {aspect_key}...")
            aspect_text = get_notion_content(aspect_key)
            chapter_content += f"### {aspect_key}\n{aspect_text}\n\n"
            found_moon_aspect = True
    if not found_moon_aspect: chapter_content += "No major aspects to the Moon found.\n\n"

    # --- CHAPTERS 9-22: REMAINING BODIES LOOP ---
    # List of bodies to process in order
    ordered_bodies = [
        "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
        "Midheaven", "Lilith", "Chiron", "North Node", "South Node", "Part of Fortune"
    ]
    
    start_chapter = 9
    
    for i, body in enumerate(ordered_bodies):
        chapter_num = start_chapter + i
        chapter_content += sep + f"# Chapter {chapter_num}: {body}\n" + sep + "\n"
        
        # 1. Body in House (Effective)
        h_val = chart_data["house_positions_eff"].get(body, 0.0)
        if h_val > 0:
            h_str = get_ordinal(int(h_val))
            house_key = f"{body} in the {h_str} House"
            print(f"-> Fetching text for: {house_key}...")
            chapter_content += f"## {house_key}\n{get_notion_content(house_key)}\n\n"
        
        # 2. Body in Sign
        sign = chart_data["placements"].get(body, "Unknown")
        sign_key = f"{body} in {sign}"
        print(f"-> Fetching text for: {sign_key}...")
        chapter_content += f"## {sign_key}\n{get_notion_content(sign_key)}\n\n"
        
        # 3. Body Aspects
        if body in chart_data["degrees"]:
            chapter_content += f"## {body} Aspects\n"
            body_deg = chart_data["degrees"][body]
            found_body_aspect = False
            
            for other_planet, other_deg in chart_data["degrees"].items():
                # Skip self and redundant aspects
                if other_planet == body: continue
                
                aspect_name = get_aspect(body_deg, other_deg)
                if aspect_name:
                    aspect_key = f"{body} {aspect_name} {other_planet}"
                    print(f"-> Fetching text for: {aspect_key}...")
                    aspect_text = get_notion_content(aspect_key)
                    chapter_content += f"### {aspect_key}\n{aspect_text}\n\n"
                    found_body_aspect = True
                    
            if not found_body_aspect:
                chapter_content += f"No major aspects to {body} found.\n\n"

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{client_data['name'].replace(' ', '_')}_{timestamp}_Full_Report.txt"
    
    with open(filename, "w") as f:
        f.write(chapter_content)
    print(f"\n[Saved to {filename}]")