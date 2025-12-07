import streamlit as st
import swisseph as se
import pytz
import os 
from dotenv import load_dotenv
import traceback
import time
from datetime import datetime
from notion_client import Client
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt

load_dotenv()
import certifi
import ssl
import numpy as np
from indesign_generator import generate_indesign_covers

# ==========================================================
# 1. PAGE CONFIG & CUSTOM STYLING
# ==========================================================
st.set_page_config(page_title="Zodicat Astrology by Adriana", page_icon="🔮", layout="centered")

# --- CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
        /* 1. FORCE DARK MODE BACKGROUNDS */
        .stApp {
            background-color: #9370db75;
            color: #FAFAFA;
        }
        [data-testid="stHeader"] {
            background-color: #9370db75;
        }
        
        /* 2. FRAME BORDER FIX (The "Specific" Option) */
        /* We target the border wrapper inside the main container */
        section[data-testid="stMain"] div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #FFFFFF !important;  /* Force White */
            border-width: 3px !important;      /* Force 3px */
            border-style: solid !important;
            border-radius: 20px !important;
            padding: 20px !important;          /* Reduced from 30px to 20px */
            background-color: #262730;         /* Card Background */
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2); /* Glow to verify visibility */
        }
        
        /* 3. BUTTON STYLING */
        div.stButton > button {
            background-color: #9370DB !important; /* Lavender */
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            height: 3em !important;
            width: 100%;
            margin-top: 10px;
        }
        div.stButton > button:hover {
            background-color: #8A2BE2 !important;
            transform: scale(1.02);
            box-shadow: 0 0 10px #9370DB;
        }
        
        /* 4. TEXT COLORS */
        p {
            color: #E0E0E0 !important;
            font-size: 14px !important;
        }
        
        /* Styling for all input labels - using even more specific selectors */
        div[data-testid="stTextInput"] label p, 
        div[data-testid="stNumberInput"] label p, 
        div[data-testid="stSelectbox"] label p, 
        div[data-testid="stDateInput"] label p,
        .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label,
        .stTextInput label p, .stNumberInput label p, .stSelectbox label p, .stDateInput label p {
            color: #9370DB !important;
            font-weight: bold !important;
            font-size: 14px !important;
        }
        
        /* Override any other styles that might be affecting labels */
        label, label p {
            color: #9370DB !important;
            font-weight: bold !important;
        }
        h1 { color: #FFFFFF !important; } /* Title size is now controlled inline */
        h2, h3 { color: #FFFFFF !important; }

        /* 5. HIDE HEADER/FOOTER */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 6. SUCCESS BOX STYLING */
        div[data-testid="stAlert"] {
            background-color: #148c17 !important; /* Green Background */
            color: #FFFFFF !important;            /* White Text */
            border: 0px solid #FFFFFF !important; /* White Border */
            border-radius: 10px !important;
            /* CENTERING MAGIC */
            display: flex !important;
            justify-content: center !important;   /* Centers content horizontally */
            align-items: center !important;       /* Centers content vertically */
        }
        
        /* 7. PROGRESS BAR STYLING */
        /* Target the progress bar fill */
        div[data-testid="stProgressBar"] > div > div {
            background-color: #9370DB !important; /* Match button color */
        }
        /* Target the progress bar track */
        div[data-testid="stProgressBar"] > div {
            background-color: rgba(147, 112, 219, 0.2) !important; /* Lighter version for track */
        }
        /* Target the progress bar text */
        div[data-testid="stProgressBar"] ~ div[data-testid="stMarkdownContainer"] p {
            color: #9370DB !important;
            font-weight: bold !important;
        }
        /* Change the icon color to white */
        div[data-testid="stAlert"] svg {
            fill: #FFFFFF !important;
        }
        
        /* Fix for the lighter green area in success messages */
        div[data-testid="stAlert"] > div {
            background-color: #148c17 !important;
        }
        
        /* Ensure all child elements have the same background color */
        div[data-testid="stAlert"] * {
            background-color: #148c17 !important;
        }
            /* 7. BOTTOM BUTTONS STYLING */
        /* Style for download button */
        div.stDownloadButton > button {
            background-color: #9370DB !important; /* Match the purple color of other buttons */
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            font-size: 16px !important;
            height: 3em !important;
            width: 100%;
            transition: all 0.3s ease;
        }
        div.stDownloadButton > button:hover {
            background-color: #8A2BE2 !important; /* Darker purple on hover */
            transform: scale(1.02);
            box-shadow: 0 0 10px #9370DB;
        }
        
        /* Style for post-generation buttons to match download button */
        /* Target all secondary buttons in the results area */
        button[data-testid="baseButton-secondary"] {
            background-color: #9370DB !important;
            color: white !important;
            height: 3em !important;
            border: none !important;
            font-weight: bold !important;
        }
        button[data-testid="baseButton-secondary"]:hover {
            background-color: #8A2BE2 !important;
            transform: scale(1.02);
            box-shadow: 0 0 10px #9370DB;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. SETUP & CONSTANTS
# ==========================================================
script_folder = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(script_folder, 'ephe') + os.path.sep
se.set_ephe_path(ephe_path)

assets_dir = os.path.join(script_folder, "assets", "pie_charts")
os.makedirs(assets_dir, exist_ok=True)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent="astro_book_bot_v2", ssl_context=ctx)

PLANET_POINTS = {
    "Sun": 4, "Moon": 4, "Ascendant": 4, "Midheaven": 1,
    "Mercury": 2, "Venus": 2, "Mars": 2,
    "Jupiter": 1, "Saturn": 1, "Uranus": 1, "Neptune": 1, "Pluto": 1,
    "North Node": 0, "Lilith": 0, "Chiron": 0, "Part of Fortune": 0
}

PLANETS = {
    se.SUN: "Sun", se.MOON: "Moon", se.MERCURY: "Mercury", se.VENUS: "Venus",
    se.MARS: "Mars", se.JUPITER: "Jupiter", se.SATURN: "Saturn", se.URANUS: "Uranus",
    se.NEPTUNE: "Neptune", se.PLUTO: "Pluto", 
    se.TRUE_NODE: "North Node", # <--- Changed to TRUE NODE (Standard)
    se.MEAN_APOG: "Lilith", se.CHIRON: "Chiron"
}

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

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

COUNTRIES = [
    "Afghanistan","Albania","Algeria","Andorra","Angola","Antigua and Barbuda","Argentina","Armenia",
    "Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium",
    "Belize","Benin","Bhutan","Bolivia","Bosnia and Herzegovina","Botswana","Brazil","Brunei","Bulgaria",
    "Burkina Faso","Burundi","Cabo Verde","Cambodia","Cameroon","Canada","Central African Republic","Chad",
    "Chile","China","Colombia","Comoros","Congo (Republic)","Congo (Democratic Republic)","Costa Rica",
    "Côte d'Ivoire","Croatia","Cuba","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic",
    "Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Eswatini","Ethiopia","Fiji",
    "Finland","France","Gabon","Gambia","Georgia","Germany","Ghana","Greece","Grenada","Guatemala","Guinea",
    "Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland",
    "Israel","Italy","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kiribati","Kuwait","Kyrgyzstan","Laos",
    "Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Madagascar","Malawi",
    "Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia",
    "Moldova","Monaco","Mongolia","Montenegro","Morocco","Mozambique","Myanmar","Namibia","Nauru","Nepal",
    "Netherlands","New Zealand","Nicaragua","Niger","Nigeria","North Macedonia","Norway","Oman","Pakistan","Palau",
    "Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Qatar","Romania","Russia",
    "Rwanda","Saint Kitts and Nevis","Saint Lucia","Saint Vincent and the Grenadines","Samoa","San Marino",
    "Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia",
    "Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","Sudan",
    "Suriname","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor-Leste","Togo",
    "Tonga","Trinidad and Tobago","Tunisia","Turkey","Turkmenistan","Tuvalu","Uganda","Ukraine","United Arab Emirates",
    "United Kingdom","United States","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Yemen",
    "Zambia","Zimbabwe"
]

# ==========================================================
# 3. HELPERS & LOGIC
# ==========================================================
def get_sign_name(lon): return ZODIAC_SIGNS[int(lon // 30)]
def normalize_degree(degree): return degree % 360
def get_ordinal(n):
    if 11 <= (n % 100) <= 13: suffix = 'th'
    else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def get_5_degree_note(chart_data):
    """Compares Geometric vs Effective houses to generate the explanatory footnote."""
    moved_list = []
    
    geom = chart_data["house_positions_geom"]
    eff = chart_data["house_positions_eff"]
    
    for body, h_val in geom.items():
        # Skip angles or empty data
        if body in ["Ascendant", "Midheaven", "Part of Fortune"] or h_val == 0.0: continue
        
        # Compare integers (e.g. Geom=6 vs Eff=7)
        if int(geom[body]) != int(eff[body]):
            # Get the ORIGINAL (Geometric) house for the explanation
            h_str = get_ordinal(int(geom[body]))
            moved_list.append(f"{body} is in the {h_str} House")
            
    if not moved_list:
        return ""
        
    # Grammar: Join with commas and 'and'
    if len(moved_list) > 1:
        joined_str = ", ".join(moved_list[:-1]) + " and " + moved_list[-1]
    else:
        joined_str = moved_list[0]
        
    return f"*{joined_str}, but because they are at less than 5º from the next house, they are considered to have their major influence and effects in the house that follows."

def get_5_degree_note(chart_data):
    """Compares Geometric vs Effective houses to generate the explanatory footnote."""
    moved_list = []
    
    geom = chart_data["house_positions_geom"]
    eff = chart_data["house_positions_eff"]
    
    for body, h_val in geom.items():
        # Skip angles or empty data
        if body in ["Ascendant", "Midheaven", "Part of Fortune"] or h_val == 0.0: continue
        
        # Compare integers (e.g. Geom=6 vs Eff=7)
        if int(geom[body]) != int(eff[body]):
            # Get the ORIGINAL (Geometric) house for the explanation
            h_str = get_ordinal(int(geom[body]))
            moved_list.append(f"{body} is in the {h_str} House")
            
    if not moved_list:
        return ""
        
    # Grammar: Join with commas and 'and'
    if len(moved_list) > 1:
        joined_str = ", ".join(moved_list[:-1]) + " and " + moved_list[-1]
    else:
        joined_str = moved_list[0]
        
    return f"*{joined_str}, but because they are at less than 5º from the next house, they are considered to have their major influence and effects in the house that follows."

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
        try: return se.houses(float(jd_utc), float(lat), float(lon), hsys)
        except: continue 
    return None, None

def get_house_number(planet_lon, cusps, apply_rule=False):
    planet_lon = normalize_degree(planet_lon)
    start_idx = 1 if len(cusps) == 13 else 0
    for i in range(12):
        curr_ptr, next_ptr = start_idx + i, start_idx + i + 1
        if next_ptr >= len(cusps): next_ptr = start_idx
        cusp_curr, cusp_next = normalize_degree(cusps[curr_ptr]), normalize_degree(cusps[next_ptr])
        in_house = False
        if cusp_next < cusp_curr:
            if planet_lon >= cusp_curr or planet_lon < cusp_next: in_house = True
        else:
            if cusp_curr <= planet_lon < cusp_next: in_house = True   
        if in_house:
            if not apply_rule: return float(i + 1)
            if normalize_degree(cusp_next - planet_lon) <= 5.0:
                return float(1 if (i + 1) == 12 else (i + 2))
            return float(i + 1)
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
        "moon_phase": "",
        "retrograde": {} 
    }
    
    # --- 1. TIMEZONE FIX ---
    try:
        # We use the timezonefinder library to get the exact timezone name from coordinates
        from timezonefinder import TimezoneFinder
        tf = TimezoneFinder()
        
        # Get timezone string (e.g., 'Europe/Lisbon' or 'America/New_York')
        tz_str = tf.timezone_at(lng=client_data["longitude"], lat=client_data["latitude"])
        if not tz_str: tz_str = "UTC"
        
        # Create the timezone object
        local_tz = pytz.timezone(tz_str)
        
        # Combine Date and Time into a "Naive" Datetime (No timezone info yet)
        naive_dt = datetime.combine(client_data["date"], client_data["time"])
        
        # Localize it (Stamp it with the detected timezone)
        local_dt = local_tz.localize(naive_dt)
        
        # Convert to UTC (Universal Time) for the Swiss Ephemeris
        # Correct: convert the localized datetime to UTC (call astimezone on the datetime)
        try:
            dt_utc = local_dt.astimezone(pytz.utc)
        except Exception:
            # Fallback: if conversion fails for any reason, fall back to treating local_dt as UTC-ish
            dt_utc = local_dt
        
        # Calculate Julian Day using the UTC time
        jd_utc = se.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                           dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)
        
        # Debug print to terminal to verify
        print(f"DEBUG: Location: {client_data['latitude']}, {client_data['longitude']}")
        print(f"DEBUG: Detected Timezone: {tz_str}")
        print(f"DEBUG: Local Time: {local_dt} -> UTC Time: {dt_utc}")
        
    except Exception as e:
        print(f"Timezone Error: {e}")
        # Fallback to naive calculation if library fails
        jd_utc = se.julday(client_data["date"].year, client_data["date"].month, client_data["date"].day, 
                           client_data["time"].hour + client_data["time"].minute/60.0)

    # --- 2. CALCULATE CHART ---
    cusps, ascmc = calculate_houses_safe(jd_utc, client_data["latitude"], client_data["longitude"])
    data["cusps"] = cusps
    
    # Angles
    data["placements"]["Ascendant"] = get_sign_name(ascmc[0])
    data["degrees"]["Ascendant"] = ascmc[0]
    data["placements"]["Midheaven"] = get_sign_name(ascmc[1])
    data["degrees"]["Midheaven"] = ascmc[1]
    data["house_positions_eff"]["Midheaven"] = get_house_number(ascmc[1], cusps, apply_rule=True)
    data["house_positions_geom"]["Midheaven"] = get_house_number(ascmc[1], cusps, apply_rule=False)
    
    sun_lon, moon_lon = 0, 0

    # Planets
    for planet_id, name in PLANETS.items():
        try:
            result = se.calc_ut(jd_utc, planet_id)
            lon_val = result[0][0]
            # Check for retrograde motion (negative speed)
            speed = result[0][3]  # Index 3 contains the speed
            data["retrograde"][name] = speed < 0
            
            data["degrees"][name] = lon_val
            data["placements"][name] = get_sign_name(lon_val)
            
            # Calculate BOTH Geometric and Effective
            data["house_positions_geom"][name] = get_house_number(lon_val, cusps, apply_rule=False)
            data["house_positions_eff"][name] = get_house_number(lon_val, cusps, apply_rule=True)
            
            if name == "Sun": sun_lon = lon_val
            if name == "Moon": moon_lon = lon_val
        except: pass

    data["moon_phase"] = get_moon_phase(sun_lon, moon_lon)
    
    # South Node
    if "North Node" in data["degrees"]:
        sn_deg = normalize_degree(data["degrees"]["North Node"] + 180)
        data["degrees"]["South Node"] = sn_deg
        data["placements"]["South Node"] = get_sign_name(sn_deg)
        data["house_positions_eff"]["South Node"] = get_house_number(sn_deg, cusps, apply_rule=True)
        data["house_positions_geom"]["South Node"] = get_house_number(sn_deg, cusps, apply_rule=False)

    # Part of Fortune
    sun_house = get_house_number(sun_lon, cusps, apply_rule=False)
    is_day = True if sun_house >= 7.0 else False
    
    if is_day:
        pof_lon = normalize_degree(ascmc[0] + moon_lon - sun_lon)
    else:
        pof_lon = normalize_degree(ascmc[0] + sun_lon - moon_lon)
            
    data["placements"]["Part of Fortune"] = get_sign_name(pof_lon)
    data["degrees"]["Part of Fortune"] = pof_lon
    data["house_positions_geom"]["Part of Fortune"] = get_house_number(pof_lon, cusps, apply_rule=False)
    data["house_positions_eff"]["Part of Fortune"] = get_house_number(pof_lon, cusps, apply_rule=True)
    
    return data

def get_label(pct, n_high, n_low):
    if 45 <= pct <= 55: return "Balanced"
    if pct > 55: return f"Dominant {n_high}" if pct >= 70 else f"Prominent {n_high}"
    else: return f"Dominant {n_low}" if (100-pct) >= 70 else f"Prominent {n_low}"

def generate_pie_chart(stats_dict, filename, title):
    labels = [k for k, v in stats_dict.items() if v > 0]
    sizes = [v for k, v in stats_dict.items() if v > 0]
    if not sizes: return None
    
    color_map = {
        "Fire": "#A9A9A9", "Earth": "#66c2a5", "Air": "#8da0cb", "Water": "#e5c494",
        "Cardinal": "#A9A9A9", "Fixed": "#8da0cb", "Mutable": "#66c2a5",
        "Yang": "#8da0cb", "Yin": "#A9A9A9",
        "Choleric": "#A9A9A9", "Melancholic": "#66c2a5", "Sanguine": "#8da0cb", "Phlegmatic": "#e5c494",
        "Superior": "#8da0cb", "Inferior": "#A9A9A9",
        "Eastern": "#A9A9A9", "Western": "#8da0cb",
        "Hot & Dry": "#A9A9A9", "Hot & Wet": "#8da0cb", "Cold & Dry": "#66c2a5", "Cold & Wet": "#e5c494"
    }
    chart_colors = [color_map.get(l, "#95a5a6") for l in labels]

    fig, ax = plt.subplots(figsize=(7, 4))
    wedges, texts = ax.pie(sizes, startangle=90, colors=chart_colors, wedgeprops=dict(width=0.5))
    ax.set_title(title, fontsize=14, loc='left', y=1.0)

    total = sum(sizes)
    legend_labels = [f'{l:<15} {int(round(s/total*100)):>3}%' for l, s in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, title="", loc="lower left", bbox_to_anchor=(1.0, 0.0), frameon=False, prop={'family': 'monospace', 'size': 10})
    
    save_path = os.path.join(assets_dir, filename)
    plt.savefig(save_path, bbox_inches='tight', transparent=True)
    plt.close()
    return f"assets/pie_charts/{filename}"

def generate_table_image(chart_data, filename="chart_summary.png"):
    """
    Generates a PNG table.
    - One row per planet (No grouping).
    - Column 2 (Planets) is CENTER aligned.
    """
    
    SYMBOLS = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        "North Node": "☊", "South Node": "☋", "Lilith": "⚸", "Chiron": "⚷",
        "Part of Fortune": "⊗", "Ascendant": "AC", "Midheaven": "MC"
    }
    
    headers = ["S I G N S", "P L A N E T S", "H O U S E"]
    table_data = []
    
    # Data Sources
    placements = chart_data["placements"]
    h_eff = chart_data["house_positions_eff"]
    h_geom = chart_data["house_positions_geom"]
    cusps = chart_data["cusps"]
    
    # 1. Determine Sort Order (Ascendant Start)
    asc_sign = placements["Ascendant"]
    try: start_index = ZODIAC_SIGNS.index(asc_sign)
    except: start_index = 0
        
    # 2. Iterate through 12 Signs
    for i in range(12):
        current_sign_idx = (start_index + i) % 12
        current_sign = ZODIAC_SIGNS[current_sign_idx]
        
        # Gather all bodies in this sign
        bodies_here = []
        
        # Check Angles first
        if placements["Ascendant"] == current_sign: 
            bodies_here.append(("Ascendant", "1"))
        if placements["Midheaven"] == current_sign: 
            mc_h = int(h_eff.get("Midheaven", 10))
            bodies_here.append(("Midheaven", str(mc_h)))
            
        # Check Planets
        for body, p_sign in placements.items():
            if body in ["Ascendant", "Midheaven"]: continue
            if p_sign == current_sign:
                h_num = int(h_eff.get(body, 0))
                bodies_here.append((body, str(h_num)))
        
        # 3. Build Rows
        if not bodies_here:
            # Empty Sign Case
            house_num = "-"
            start_cusp_idx = 1 if len(cusps) == 13 else 0
            for h in range(12):
                deg = cusps[start_cusp_idx + h]
                if get_sign_name(normalize_degree(deg)) == current_sign:
                    house_num = str(h + 1)
                    break
            table_data.append([current_sign, "EMPTY", house_num])
        
        else:
            # Sort bodies by House Number
            bodies_here.sort(key=lambda x: int(x[1]))
            
            for body, h_str in bodies_here:
                # Format Planet Name
                if body in ["Ascendant", "Midheaven"]:
                    sym = "↑" if body == "Ascendant" else "MC"
                    p_str = f"{sym} {body.upper()}"
                else:
                    # Asterisk Check
                    is_moved = int(h_geom.get(body, 0)) != int(h_eff.get(body, 0))
                    marker = "*" if is_moved else ""
                    sym = SYMBOLS.get(body, "")
                    p_str = f"{sym} {body.upper()}{marker}"
                
                # Create the row: [Aquarius, Planet Name, 1]
                table_data.append([current_sign, p_str, h_str])

    # 4. Render Plot
    row_count = len(table_data)
    fig_height = max(8, row_count * 0.6)
    
    fig, ax = plt.subplots(figsize=(8, fig_height)) 
    ax.axis('off')
    
    plt.title("", fontsize=22, weight='bold', y=1.02)

    table = ax.table(cellText=table_data, 
                     colLabels=headers, 
                     loc='center', 
                     cellLoc='center', # <--- CENTERING APPLIED HERE GLOBALLY
                     colWidths=[0.25, 0.55, 0.2])

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 2.5)

    # 5. Styling
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(1)
        
        if row == 0: # Header
            cell.set_text_props(weight='bold', fontsize=14)
            cell.set_height(0.04)
            cell.set_facecolor('white')
            cell.set_edgecolor('white')
        else:
            # Column 0 (Signs) -> Light Blue
            if col == 0:
                cell.set_facecolor('#BDD7EE')
                cell.set_text_props(fontsize=11)
            
            # Column 1 (Planets) -> White, CENTER Aligned
            elif col == 1:
                cell.set_facecolor('#FFFFFF')
                cell.set_text_props(fontsize=11, ha='center') # <--- EXPLICIT CENTER
            
            # Column 2 (Houses) -> Light Blue
            elif col == 2:
                cell.set_facecolor('#BDD7EE')
                cell.set_text_props(fontsize=14)

    save_path = os.path.join(assets_dir, filename)
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()
    return f"assets/pie_charts/{filename}"
    
    # 1. Astrological Symbols Map
    SYMBOLS = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
        "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        "North Node": "☊", "South Node": "☋", "Lilith": "⚸", "Chiron": "⚷",
        "Part of Fortune": "⊗", "Ascendant": "AC", "Midheaven": "MC"
    }

    # 2. Prepare Data Rows
    headers = ["S I G N S", "P L A N E T S", "H O U S E"]
    cell_data = []
    
    cusps = chart_data["cusps"]
    h_eff = chart_data["house_positions_eff"]
    start_idx = 1 if len(cusps) == 13 else 0
    
    for i in range(12):
        h_num = i + 1
        
        # Column 1: Sign on Cusp
        cusp_degree = cusps[start_idx + i]
        sign_name = get_sign_name(normalize_degree(cusp_degree))
        
        # Column 2: Planets in this House
        planets_here = []
        
        # Check all bodies
        for body, h_val in h_eff.items():
            # We round to int to match house number
            if int(h_val) == h_num:
                sym = SYMBOLS.get(body, "")
                # Create string like "☉ SUN"
                planets_here.append(f"{sym}  {body.upper()}")
        
        if not planets_here:
            p_str = "EMPTY"
        else:
            p_str = "\n".join(planets_here)
            
        # Column 3: House Number
        h_str = str(h_num)
        
        cell_data.append([sign_name, p_str, h_str])

    # 3. Create Plot
    # Taller figure to accommodate lists of planets
    fig, ax = plt.subplots(figsize=(6, 10)) 
    ax.axis('off')
    
    # Title
    plt.title("SIGNS, PLANETS & HOUSES POSITION", fontsize=16, weight='bold', y=1.02)

    # 4. Draw Table
    # Widths: Sign(25%), Planets(55%), House(20%)
    table = ax.table(cellText=cell_data, 
                     colLabels=headers, 
                     loc='center', 
                     cellLoc='left', 
                     colWidths=[0.25, 0.55, 0.2])

    # 5. Styling
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 3.5) # Stretches the row height

    # Apply Colors & Borders
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(1)
        
        # CENTER ALIGNMENT FOR HOUSES & SIGNS
        if col == 0 or col == 2:
            cell.get_text().set_horizontalalignment('center')
        
        # PADDING FOR PLANETS
        if col == 1:
             cell.set_text_props(fontsize=10)
             # Add a little left padding by transforming text position if needed, 
             # but usually cellLoc='left' is sufficient.

        # HEADER ROW (Row 0)
        if row == 0:
            cell.set_text_props(weight='bold', fontsize=12)
            cell.set_height(0.06)
            cell.set_facecolor('white') # Clean header
            cell.set_edgecolor('white') # Invisible border for header
            cell.get_text().set_horizontalalignment('center')
        
        # DATA ROWS
        else:
            # Column 0 (Signs) -> Light Blue
            if col == 0:
                cell.set_facecolor('#BDD7EE')
                
            # Column 1 (Planets) -> White
            elif col == 1:
                cell.set_facecolor('#FFFFFF')

            # Column 2 (Houses) -> Light Blue
            elif col == 2:
                cell.set_facecolor('#BDD7EE')
                cell.set_text_props(fontsize=14)

    # Save
    save_path = os.path.join(assets_dir, filename)
    plt.savefig(save_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    return f"assets/pie_charts/{filename}"

def calc_stats(data, method):
    score = {k:0 for k in method["keys"]}
    total = 0
    for p, h in data.items():
        pts = PLANET_POINTS.get(p, 0)
        if pts == 0 or h == 0.0: continue
        total += pts
        method["logic"](score, p, h, pts)
    
    res = {}
    if total > 0:
        for k, v in score.items(): res[k] = int(round((v/total)*100))
        current_sum = sum(list(res.values())[:-1])
        res[list(res.keys())[-1]] = 100 - current_sum
    else: res = {k:0 for k in score}
    return res

def get_notion_content(placement_name):
    if len(NOTION_TOKEN) < 10: return "[Check Token]"
    notion = Client(auth=NOTION_TOKEN)
    try:
        results = notion.databases.query(
            database_id=DATABASE_ID, filter={ "property": "Placement", "title": { "equals": placement_name } }
        )
        if not results["results"]: return f"[Missing: {placement_name}]"
        page = results["results"][0]
        if not page["properties"]["Description"]["rich_text"]: return ""
        return "".join([t["plain_text"] for t in page["properties"]["Description"]["rich_text"]])
    except Exception as e: return f"[API Error: {e}]"

def get_summary_table(chart_data):
    table = "| Sign on Cusp | Planets in House | House |\n| :--- | :--- | :--- |\n"
    cusps = chart_data["cusps"]
    h_eff = chart_data["house_positions_eff"]
    start_idx = 1 if len(cusps) == 13 else 0
    for i in range(12):
        h_num = i + 1
        cusp_s = get_sign_name(normalize_degree(cusps[start_idx + i]))
        planets = [b for b, h in h_eff.items() if b not in ["Ascendant", "Midheaven"] and int(h) == h_num]
        table += f"| {cusp_s} | {', '.join(planets)} | {get_ordinal(h_num)} |\n"
    return table
# 4. GUI INTERFACE
# ==========================================================
if 'lat' not in st.session_state: st.session_state.lat = 0.0
if 'lon' not in st.session_state: st.session_state.lon = 0.00
if 'run_engine' not in st.session_state: st.session_state.run_engine = False
if 'generate_covers' not in st.session_state: st.session_state.generate_covers = False
if 'chart_data' not in st.session_state: st.session_state.chart_data = None
if 'show_dialog' not in st.session_state: st.session_state.show_dialog = False
if 'generation_complete' not in st.session_state: st.session_state.generation_complete = False
if 'book_content' not in st.session_state: st.session_state.book_content = None
if 'book_filename' not in st.session_state: st.session_state.book_filename = None

# --- CONFIRMATION DIALOG FUNCTION ---
@st.dialog("⚠️ :violet[VERIFICATION REQUIRED]")
def show_confirmation_dialog():
    # Construct location string
    loc_str = f"{c_city}, {c_state}, {c_country}" if c_state.strip() else f"{c_city}, {c_country}"
    
    # Custom Light Red Box inside the popup
    st.markdown(f"""
        <div style="
            background-color: #FF0000; 
            color: #FFFFFF; 
            padding: 15px; 
            border-radius: 10px; 
            border: 2px solid #EF9A9A;
            margin-bottom: 15px;
            text-align: center;">
            <h3 style="color: #FFFFFF; margin:0; padding-bottom:10px;">PLEASE VERIFY</h3>
            <p style="font-size: 16px; margin: 0; color: #FFFFFF;">
                <b>Location:</b> {loc_str}<br>
                <b>Coordinates:</b> {c_lat}, {c_lon}
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Go back", use_container_width=True):
            # Just rerun to close the dialog
            st.rerun()
            
    with col2:
        if st.button("Confirm & Run", type="primary", use_container_width=True):
            # Store current chart data for potential cover generation later
            st.session_state.chart_data = {
                'name': c_name,
                'birth_date': c_date,
                'birth_time': c_time,
                'city': c_city,
                'state': c_state,
                'country': c_country,
                'lat': c_lat,
                'lon': c_lon
            }
            # Set flag to run the engine
            st.session_state.run_engine = True
            st.session_state.generation_complete = False
            # Rerun to close dialog and start processing
            st.rerun()

# --- MAIN APP CONTAINER ---
with st.container(border=True):
    
    st.markdown('<h1 style="text-align: center; font-size: 2.34rem;">Zodicat Astrology by Adriana</h1><div style="text-align: center; margin-bottom: 0px;"><span style="font-size: 4rem;">🔮</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Force label colors with direct CSS injection
    st.markdown("""
        <style>
        label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stDateInput label {
            color: #9370DB !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 1. CLIENT DETAILS
    st.subheader("1. Client Information")
    
    # 4 Columns: Name | Date | Hour | Min
    # Ratios adjusted slightly to fit the "Time" labels comfortably
    col1, col2, col3, col4 = st.columns([2, 1.5, 0.7, 0.7])
    
    with col1: 
        c_name = st.text_input("Name", "Joe Joseph")
    with col2: 
        # Note: min_value=datetime(1900, 1, 1) allows scrolling back to 1900
        c_date = st.date_input("Date of Birth", 
                               value=datetime(1968, 5, 21),
                               min_value=datetime(1900, 1, 1),
                               max_value=datetime(2100, 12, 31))
    
    # Using native labels ensures the dropdowns align perfectly with the text inputs
    with col3:
        c_hour = st.selectbox("(Hour)", range(24), index=7)
    with col4:
        c_min = st.selectbox("(Minute)", range(60), index=30)
        
    c_time = datetime.strptime(f"{c_hour}:{c_min}", "%H:%M").time()
    
    # Add some spacing between sections
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Location fields (without subtitle)
    
    # Row 1: City | State | Country
    rc1, rc2, rc3 = st.columns([1.5, 1, 1.5])
    with rc1: 
        c_city = st.text_input("City", "Jilemnice")
    with rc2: 
        c_state = st.text_input("State/Region (Optional)", "")
    with rc3: 
        c_country = st.selectbox("Country", COUNTRIES, index=COUNTRIES.index("Czech Republic"))
    
    # Row 2: Latitude | Longitude
    r2c1, r2c2 = st.columns(2)
    with r2c1: 
        c_lat = st.number_input("Latitude", value=st.session_state.lat, format="%.4f")
    with r2c2: 
        c_lon = st.number_input("Longitude", value=st.session_state.lon, format="%.4f")

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. ACTION BUTTONS (Two buttons in a row)
    b_col1, b_col2, b_col3 = st.columns([1, 1, 1])
    
    with b_col1:
        # Added unique key just in case
        find_coords_clicked = st.button("📍 Find Coordinates", type="secondary", use_container_width=True, key="btn_find_coords")

    with b_col2:
        generate_covers_clicked = st.button("📔 Generate PDF Covers", type="primary", use_container_width=True, key="btn_gen_covers_top")

    with b_col3:
        if st.button("🚀 Generate Full Book", type="primary", use_container_width=True, key="btn_launch_dialog"):
            show_confirmation_dialog()

    if find_coords_clicked:
        try:
            q = f"{c_city}, {c_state}, {c_country}" if c_state.strip() else f"{c_city}, {c_country}"
            loc = geolocator.geocode(q)
            if loc:
                st.success(f"Found: {q}")
                st.session_state.lat = loc.latitude
                st.session_state.lon = loc.longitude
                time.sleep(2)
                st.rerun()
            else: # ERROR: Custom Bright Red Box
                st.markdown("""
                    <div style="
                        background-color: #FFEBEE; 
                        color: #D50000; 
                        padding: 10px; 
                        border-radius: 5px; 
                        border: 2px solid #D50000; 
                        text-align: center; 
                        font-weight: bold;
                        margin-top: 10px;">
                        ❌ Location not found.
                    </div>
                """, unsafe_allow_html=True)
                
        except Exception as e: 
            st.error(f"Connection Error: {e}")

    if generate_covers_clicked:
        # Format data
        birth_date_str = c_date.strftime("%B %d, %Y")
        birth_time_str = c_time.strftime("%I:%M %p").lstrip('0')
        birth_info = f"{birth_date_str} - {birth_time_str}"
        location = f"{c_city}, {c_state}, {c_country}" if c_state.strip() else f"{c_city}, {c_country}"
        
        with st.spinner("Generating InDesign covers... This may take a moment."):
            try:
                result = generate_indesign_covers(c_name, birth_info, location)
                if result['success']:
                    st.success(f"✅ Covers generated! Saved to: {result['output_folder']}")
                else:
                    st.error(f"❌ Error: {result['error']}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- LOGIC EXECUTION ---
# Handle cover generation
if st.session_state.generate_covers and st.session_state.chart_data:
    # Show a progress message
    progress_container = st.empty()
    progress_container.info("Starting cover generation process...")
    
    try:
        # Get data from session state
        chart_data = st.session_state.chart_data
        name = chart_data['name']
        
        # Format birth info string
        birth_date = chart_data['birth_date']
        birth_time = chart_data['birth_time']
        birth_date_str = birth_date.strftime("%B %d, %Y")
        birth_time_str = birth_time.strftime("%I:%M %p").lstrip('0')
        birth_info = f"{birth_date_str} - {birth_time_str}"
        
        # Format location string
        city = chart_data['city']
        state = chart_data['state']
        country = chart_data['country']
        location = f"{city}, {state}, {country}" if state.strip() else f"{city}, {country}"
        
        # Check if InDesign template exists
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INDESIGN FILES", "Cover - AstroBookGenerator.indt")
        continue_processing = True
        
        if os.path.exists(template_path):
            progress_container.info("Template found. Preparing to generate covers...")
        else:
            progress_container.error(f"❌ Template not found at: {template_path}")
            st.session_state.generate_covers = False
            continue_processing = False
        
        # Only proceed if template was found
        if continue_processing:
            # Show progress indicator
            with st.spinner("Generating InDesign covers with Adobe InDesign... This may take a moment."):
                # Call the InDesign generator function
                result = generate_indesign_covers(name, birth_info, location)
                
                if result['success']:
                    st.success(f"Cover PDFs generated successfully! Files saved to: {result['output_folder']}")
                else:
                    st.error(f"Error generating covers: {result['error']}")
                    st.info("Please make sure Adobe InDesign is installed and running properly on your system.")
        
        # Reset the state
        st.session_state.generate_covers = False
        
    except Exception as e:
        st.error(f"Error generating covers: {e}\n\n{traceback.format_exc()}")
        st.info("Please check that Adobe InDesign is installed and that the template file exists in the INDESIGN FILES folder.")
        st.session_state.generate_covers = False

# Handle book generation
if st.session_state.run_engine:
    # Inject CSS for progress bar styling
    st.markdown("""
        <style>
        /* Direct styling for progress bar */
        .stProgress > div > div > div > div {
            background-color: #9370DB !important;
        }
        .stProgress p {
            color: #9370DB !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0, text="0% - Starting Engine...")
    
    try:
        # 1. CALCULATION
        progress_bar.progress(10, text="10% - Calculating Birth Chart...")
        client_in = {"name":c_name, "date":c_date, "time":c_time, "latitude":c_lat, "longitude":c_lon}
        chart = get_astrology_data(client_in)
        progress_bar.progress(30, text="30% - Calculating Statistics...")
        
        # --- STATS CALCULATIONS (Define variables here, but don't write to content yet) ---
        
        # 1. Hemisphere
        h_scores = {"Superior": 0, "Inferior": 0}
        h_tot = 0
        for p, h in chart["house_positions_geom"].items():
            pts = PLANET_POINTS.get(p, 0)
            if pts > 0 and h > 0:
                h_tot += pts
                if h >= 7: h_scores["Superior"] += pts
                else: h_scores["Inferior"] += pts
        h_stats = {}
        if h_tot > 0:
            h_stats["Superior"] = int(round((h_scores["Superior"] / h_tot) * 100))
            h_stats["Inferior"] = 100 - h_stats["Superior"]
        else: h_stats = {"Superior": 0, "Inferior": 0}
        h_stat_label = get_label(h_stats["Superior"], "Superior", "Inferior")
        h_img = generate_pie_chart(h_stats, "hemisphere.png", "YOUR SUPERIOR & INFERIOR HEMISPHERE COUNT")

        # 2. East/West
        ew_scores = {"Eastern": 0, "Western": 0}
        ew_tot = 0
        for p, h in chart["house_positions_geom"].items():
            pts = PLANET_POINTS.get(p, 0)
            if pts > 0 and h > 0:
                ew_tot += pts
                if int(h) in [10,11,12,1,2,3]: ew_scores["Eastern"] += pts
                else: ew_scores["Western"] += pts
        ew_stats = {}
        if ew_tot > 0:
            ew_stats["Eastern"] = int(round((ew_scores["Eastern"] / ew_tot) * 100))
            ew_stats["Western"] = 100 - ew_stats["Eastern"]
        else: ew_stats = {"Eastern": 0, "Western": 0}
        ew_label = get_label(ew_stats["Eastern"], "Eastern", "Western")
        ew_img = generate_pie_chart(ew_stats, "east_west.png", "YOUR EASTERN & WESTERN HEMISPHERE COUNT")

        # 3. Qualities
        q_scores = {"Hot":0, "Cold":0, "Wet":0, "Dry":0}
        tot_q = 0
        for p, sign in chart["placements"].items():
            pts = PLANET_POINTS.get(p, 0)
            if pts > 0:
                t, m, _, _, _, _ = SIGN_DATA.get(sign, (None,)*6)
                if t: 
                    q_scores[t]+=pts; q_scores[m]+=pts; tot_q+=pts
        q_stats = {k: int(round((v/tot_q)*100)) if tot_q>0 else 0 for k,v in q_scores.items()}
        q_status = f"{'Hot' if q_stats['Hot']>=50 else 'Cold'} & {'Wet' if q_stats['Wet']>=50 else 'Dry'}"
        q_label_t = get_label(q_stats["Hot"], "Hot", "Cold")
        q_label_m = get_label(q_stats["Wet"], "Wet", "Dry")
        
        pq_raw = {
            "Hot & Dry": q_stats["Hot"] * q_stats["Dry"] // 100,
            "Hot & Wet": q_stats["Hot"] * q_stats["Wet"] // 100,
            "Cold & Dry": q_stats["Cold"] * q_stats["Dry"] // 100,
            "Cold & Wet": q_stats["Cold"] * q_stats["Wet"] // 100
        }
        total_pq = sum(pq_raw.values())
        pq_stats = {k: int(round((v/total_pq)*100)) for k,v in pq_raw.items()} if total_pq > 0 else pq_raw
        pq_img = generate_pie_chart(pq_stats, "primitive_qualities.png", "YOUR PRIMITIVE QUALITIES COUNT")
        
        temp_img = generate_pie_chart({"Hot":q_stats["Hot"], "Cold":q_stats["Cold"]}, "temp.png", "TEMP")

        # 4. Temperaments
        t_score = {k:0 for k in ["Choleric","Melancholic","Sanguine","Phlegmatic"]}
        t_tot = 0
        for p, s in chart["placements"].items():
            pts = PLANET_POINTS.get(p,0)
            if pts > 0:
                t_tot += pts
                _, _, t, _, _, _ = SIGN_DATA.get(s, (None,)*6)
                if t: t_score[t] += pts
        t_stats = {k: int(round((v/t_tot)*100)) if t_tot>0 else 0 for k,v in t_score.items()}
        temp_img_file = generate_pie_chart(t_stats, "temperaments.png", "YOUR TEMPERAMENTS COUNT")
        temp_primary = max(t_stats, key=t_stats.get)

        # 5. Elements
        e_score = {k:0 for k in ["Fire","Earth","Air","Water"]}
        e_tot = 0
        for p, s in chart["placements"].items():
            pts = PLANET_POINTS.get(p,0)
            if pts > 0:
                e_tot += pts
                _, _, _, e, _, _ = SIGN_DATA.get(s, (None,)*6)
                if e: e_score[e] += pts
        elem_stats = {k: int(round((v/e_tot)*100)) if e_tot>0 else 0 for k,v in e_score.items()}
        elem_img = generate_pie_chart(elem_stats, "elements.png", "YOUR ELEMENTS COUNT")
        elem_primary = max(elem_stats, key=elem_stats.get)

        # 6. Modalities
        m_score = {k:0 for k in ["Cardinal","Fixed","Mutable"]}
        m_tot = 0
        for p, s in chart["placements"].items():
            pts = PLANET_POINTS.get(p,0)
            if pts > 0:
                m_tot += pts
                _, _, _, _, m, _ = SIGN_DATA.get(s, (None,)*6)
                if m: m_score[m] += pts
        mode_stats = {k: int(round((v/m_tot)*100)) if m_tot>0 else 0 for k,v in m_score.items()}
        mode_img = generate_pie_chart(mode_stats, "modalities.png", "YOUR MODALITIES COUNT")
        mode_primary = max(mode_stats, key=mode_stats.get)

        # 7. Polarity
        p_score = {k:0 for k in ["Yang","Yin"]}
        p_tot = 0
        for p, s in chart["placements"].items():
            pts = PLANET_POINTS.get(p,0)
            if pts > 0:
                p_tot += pts
                _, _, _, _, _, pol = SIGN_DATA.get(s, (None,)*6)
                if pol: p_score[pol] += pts
        pol_stats = {k: int(round((v/p_tot)*100)) if p_tot>0 else 0 for k,v in p_score.items()}
        pol_img = generate_pie_chart(pol_stats, "polarities.png", "YOUR POLARITIES COUNT")
        pol_label = get_label(pol_stats["Yang"], "Yang", "Yin")

        # 4. CONTENT GENERATION (Now we start writing!)
        progress_bar.progress(40, text="40% - Fetching Content from Notion...")
        sep = "-" * 30 + "\n"
        content = f"Chart for: {c_name}\n\n"
        
        # Birth Chart Summary
        birth_date = client_in["date"].strftime("%B %d, %Y")
        birth_time = client_in["time"].strftime("%I:%M %p")
        location = f"{c_city}, {c_country}"
        
        content += f"# Birth Chart Analysis for {c_name}\n"
        content += f"Born: {birth_date} at {birth_time}\n"
        content += f"Location: {location}\n\n"
        
        content += "PLANETARY POSITIONS\n"
        content += "==================================================\n"
        
        # Function to convert decimal degrees to degrees, minutes, seconds
        def decimal_to_dms(decimal_degrees):
            degrees = int(decimal_degrees)
            decimal_minutes = (decimal_degrees - degrees) * 60
            minutes = int(decimal_minutes)
            seconds = int((decimal_minutes - minutes) * 60)
            return f"{degrees}°{minutes}'{seconds}\""
        
        # Add planetary positions with degrees
        for body, sign in chart["placements"].items():
            if body in ["South Node", "Part of Fortune", "Ascendant", "Midheaven"]:
                continue
            if body in chart["degrees"]:
                # Get the sign-specific degree (0-30)
                sign_degree = chart["degrees"][body] % 30
                dms = decimal_to_dms(sign_degree)
                
                # Add retrograde marker if planet is retrograde
                retrograde_marker = " R" if chart["retrograde"].get(body, False) else ""
                content += f"{body} in {sign} {dms}{retrograde_marker}\n"
        
        # Add Ascendant separately at the end
        if "Ascendant" in chart["placements"] and "Ascendant" in chart["degrees"]:
            sign = chart["placements"]["Ascendant"]
            sign_degree = chart["degrees"]["Ascendant"] % 30
            dms = decimal_to_dms(sign_degree)
            content += f"\nAscendant in {sign} {dms}\n\n"
        
        # Original Chart Data
        content += sep + "# Chart Data\n" + sep + "\n### Planets in Signs\n"
        for b, s in chart["placements"].items(): content += f"* **{b}:** {s}\n"
        content += "\n### Planets in Houses (Effective)\n"
        for b, h in chart["house_positions_eff"].items():
            if b not in ["Ascendant", "Midheaven"] and h > 0: content += f"* **{b}:** {get_ordinal(int(h))} House\n"
        
        # Chapter 1: Pillars
        progress_bar.progress(50, text="50% - Generating Chapter 1...")
        content += "\n" + sep + "# Chapter 1: Pillars of Personality\n" + sep + "\n"
        # Define pillars order
        pillars = ["Ascendant", "Sun", "Moon"]
        
        for body in pillars:
            sign = chart['placements'][body]
            key = f"{body} in {sign}"
            
            content += f"## {key}\n"
            
            # INSERT SIGN IMAGE ONLY (e.g., assets/signs/aries.png)
            img_sign = sign.lower() + ".png"
            content += f"<<IMG: assets/signs/{img_sign}>>\n"
            
            # Insert Text from Notion
            content += f"{get_notion_content(key)}\n\n"
            
        # Chapter 2: Stats (Now we use the variables defined above)
        content += sep + "# Chapter 2: Astrological Statistics (Pie Charts)\n" + sep + "\n"
        content += "## Your Superior & Inferior Hemisphere Count\n" + f"<<IMG: {h_img}>>\n" + f"Status: **{h_stat_label}**\n(Superior: {h_stats['Superior']}% / Inferior: {h_stats['Inferior']}%)\n\n"
        content += "## Your Eastern & Western Hemisphere Count\n" + f"<<IMG: {ew_img}>>\n" + f"Status: **{ew_label}**\n(Eastern: {ew_stats['Eastern']}% / Western: {ew_stats['Western']}%)\n\n"
        content += "## Your Primitive Qualities Count\n" + f"<<IMG: {pq_img}>>\n" + f"Status: **{q_status}**\nTemperature Status: **{q_label_t}** (Hot {q_stats['Hot']}% / Cold {q_stats['Cold']}%)\n" + f"Moisture Status: **{q_label_m}** (Wet {q_stats['Wet']}% / Dry {q_stats['Dry']}%)\n\n"
        content += "## Your Temperaments Count\n" + f"<<IMG: {temp_img_file}>>\n" + f"Primary Temperament: **{temp_primary}**\n"
        for k,v in t_stats.items(): content += f"{k}: {v}%\n"
        content += "\n## Your Elements Count\n" + f"<<IMG: {elem_img}>>\n" + f"Primary Element: **{elem_primary}**\n"
        for k,v in elem_stats.items(): content += f"{k}: {v}%\n"
        content += "\n## Your Modalities Count\n" + f"<<IMG: {mode_img}>>\n" + f"Primary Modality: **{mode_primary}**\n"
        for k,v in mode_stats.items(): content += f"{k}: {v}%\n"
        content += "\n## Your Polarities Count\n" + f"<<IMG: {pol_img}>>\n" + f"Status: **{pol_label}**\n(Yang: {pol_stats['Yang']}% / Yin: {pol_stats['Yin']}%)\n\n"
        
        # Chapter 3: Moon Phase
        progress_bar.progress(60, text="60% - Generating Chapter 3...")
        m_key = chart["moon_phase"]
        content += sep + "# Chapter 3: The Moon Phase\n" + sep + "\n" + f"## Your Moon Phase: {m_key}\n{get_notion_content(m_key)}\n\n"

        # Chapter 4: Houses
        content += sep + "# Chapter 4: The 12 Houses\n" + sep + "\n"
        start = 1 if len(chart["cusps"])==13 else 0
        for i in range(12):
            d = chart["cusps"][start+i]
            s = get_sign_name(normalize_degree(d))
            key = f"{s} in the {get_ordinal(i+1)} House"
            content += f"## {key}\n{get_notion_content(key)}\n\n"
            
        # Chapter 5: Table
        progress_bar.progress(70, text="70% - Generating Summary Table...")
        table_img = generate_table_image(chart, "chart_summary.png")
        five_deg_note = get_5_degree_note(chart)
        content += sep + "# Chapter 5: Chart Summary Data\n" + sep + "\n" + f"<<IMG: {table_img}>>\n\n"
        if five_deg_note: content += f"{five_deg_note}\n\n"
        
        # Chapter 6: Ascendant
        asc_key = f"Ascendant in {chart['placements']['Ascendant']}"
        content += sep + "# Chapter 6: The Ascendant\n" + sep + "\n" + f"## {asc_key}\n{get_notion_content(asc_key)}\n\n"

        # Chapters 7-22 - Individual chapter generation with progress updates
        
        # Chapter 7: Sun
        progress_bar.progress(71, text="71% - Generating Chapter 7: Sun...")
        content += sep + "# Chapter 7: Sun\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Sun", 0.0)
        if h > 0:
            k = f"Sun in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Sun", "")
        k = f"Sun in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Sun" in chart["degrees"]:
            content += f"## Sun Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Sun" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Sun"], d2)
                if asp:
                    k_asp = f"Sun {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Sun found.\n\n"
        
        # Chapter 8: Moon
        progress_bar.progress(72, text="72% - Generating Chapter 8: Moon...")
        content += sep + "# Chapter 8: Moon\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Moon", 0.0)
        if h > 0:
            k = f"Moon in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Moon", "")
        k = f"Moon in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Moon" in chart["degrees"]:
            content += f"## Moon Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Moon" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Moon"], d2)
                if asp:
                    k_asp = f"Moon {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Moon found.\n\n"
        
        # Chapter 9: Mercury
        progress_bar.progress(73, text="73% - Generating Chapter 9: Mercury...")
        content += sep + "# Chapter 9: Mercury\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Mercury", 0.0)
        if h > 0:
            k = f"Mercury in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Mercury", "")
        k = f"Mercury in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Mercury" in chart["degrees"]:
            content += f"## Mercury Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Mercury" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Mercury"], d2)
                if asp:
                    k_asp = f"Mercury {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Mercury found.\n\n"
        
        # Chapter 10: Venus
        progress_bar.progress(74, text="74% - Generating Chapter 10: Venus...")
        content += sep + "# Chapter 10: Venus\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Venus", 0.0)
        if h > 0:
            k = f"Venus in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Venus", "")
        k = f"Venus in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Venus" in chart["degrees"]:
            content += f"## Venus Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Venus" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Venus"], d2)
                if asp:
                    k_asp = f"Venus {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Venus found.\n\n"
        
        # Chapter 11: Mars
        progress_bar.progress(76, text="76% - Generating Chapter 11: Mars...")
        content += sep + "# Chapter 11: Mars\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Mars", 0.0)
        if h > 0:
            k = f"Mars in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Mars", "")
        k = f"Mars in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Mars" in chart["degrees"]:
            content += f"## Mars Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Mars" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Mars"], d2)
                if asp:
                    k_asp = f"Mars {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Mars found.\n\n"
        
        # Chapter 12: Jupiter
        progress_bar.progress(78, text="78% - Generating Chapter 12: Jupiter...")
        content += sep + "# Chapter 12: Jupiter\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Jupiter", 0.0)
        if h > 0:
            k = f"Jupiter in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Jupiter", "")
        k = f"Jupiter in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Jupiter" in chart["degrees"]:
            content += f"## Jupiter Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Jupiter" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Jupiter"], d2)
                if asp:
                    k_asp = f"Jupiter {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Jupiter found.\n\n"
        
        # Chapter 13: Saturn
        progress_bar.progress(80, text="80% - Generating Chapter 13: Saturn...")
        content += sep + "# Chapter 13: Saturn\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Saturn", 0.0)
        if h > 0:
            k = f"Saturn in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Saturn", "")
        k = f"Saturn in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Saturn" in chart["degrees"]:
            content += f"## Saturn Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Saturn" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Saturn"], d2)
                if asp:
                    k_asp = f"Saturn {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Saturn found.\n\n"
        
        # Chapter 14: Uranus
        progress_bar.progress(82, text="82% - Generating Chapter 14: Uranus...")
        content += sep + "# Chapter 14: Uranus\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Uranus", 0.0)
        if h > 0:
            k = f"Uranus in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Uranus", "")
        k = f"Uranus in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Uranus" in chart["degrees"]:
            content += f"## Uranus Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Uranus" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Uranus"], d2)
                if asp:
                    k_asp = f"Uranus {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Uranus found.\n\n"
        
        # Chapter 15: Neptune
        progress_bar.progress(84, text="84% - Generating Chapter 15: Neptune...")
        content += sep + "# Chapter 15: Neptune\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Neptune", 0.0)
        if h > 0:
            k = f"Neptune in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Neptune", "")
        k = f"Neptune in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Neptune" in chart["degrees"]:
            content += f"## Neptune Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Neptune" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Neptune"], d2)
                if asp:
                    k_asp = f"Neptune {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Neptune found.\n\n"
        
        # Chapter 16: Pluto
        progress_bar.progress(86, text="86% - Generating Chapter 16: Pluto...")
        content += sep + "# Chapter 16: Pluto\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Pluto", 0.0)
        if h > 0:
            k = f"Pluto in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Pluto", "")
        k = f"Pluto in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Pluto" in chart["degrees"]:
            content += f"## Pluto Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Pluto" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Pluto"], d2)
                if asp:
                    k_asp = f"Pluto {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Pluto found.\n\n"
        
        # Chapter 17: Midheaven
        progress_bar.progress(88, text="88% - Generating Chapter 17: Midheaven...")
        content += sep + "# Chapter 17: Midheaven\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Midheaven", 0.0)
        if h > 0:
            k = f"Midheaven in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Midheaven", "")
        k = f"Midheaven in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Midheaven" in chart["degrees"]:
            content += f"## Midheaven Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Midheaven" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Midheaven"], d2)
                if asp:
                    k_asp = f"Midheaven {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Midheaven found.\n\n"
        
        # Chapter 18: Lilith
        progress_bar.progress(90, text="90% - Generating Chapter 18: Lilith...")
        content += sep + "# Chapter 18: Lilith\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Lilith", 0.0)
        if h > 0:
            k = f"Lilith in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Lilith", "")
        k = f"Lilith in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Lilith" in chart["degrees"]:
            content += f"## Lilith Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Lilith" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Lilith"], d2)
                if asp:
                    k_asp = f"Lilith {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Lilith found.\n\n"
        
        # Chapter 19: Chiron
        progress_bar.progress(92, text="92% - Generating Chapter 19: Chiron...")
        content += sep + "# Chapter 19: Chiron\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Chiron", 0.0)
        if h > 0:
            k = f"Chiron in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Chiron", "")
        k = f"Chiron in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "Chiron" in chart["degrees"]:
            content += f"## Chiron Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "Chiron" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["Chiron"], d2)
                if asp:
                    k_asp = f"Chiron {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to Chiron found.\n\n"
        
        # Chapter 20: North Node
        progress_bar.progress(94, text="94% - Generating Chapter 20: North Node...")
        content += sep + "# Chapter 20: North Node\n" + sep + "\n"
        h = chart["house_positions_eff"].get("North Node", 0.0)
        if h > 0:
            k = f"North Node in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("North Node", "")
        k = f"North Node in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "North Node" in chart["degrees"]:
            content += f"## North Node Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "North Node" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["North Node"], d2)
                if asp:
                    k_asp = f"North Node {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to North Node found.\n\n"
        
        # Chapter 21: South Node
        progress_bar.progress(96, text="96% - Generating Chapter 21: South Node...")
        content += sep + "# Chapter 21: South Node\n" + sep + "\n"
        h = chart["house_positions_eff"].get("South Node", 0.0)
        if h > 0:
            k = f"South Node in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("South Node", "")
        k = f"South Node in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        if "South Node" in chart["degrees"]:
            content += f"## South Node Aspects\n"
            found = False
            for p2, d2 in chart["degrees"].items():
                if p2 == "South Node" or p2 == "Part of Fortune": continue
                asp = get_aspect(chart["degrees"]["South Node"], d2)
                if asp:
                    k_asp = f"South Node {asp} {p2}"
                    content += f"### {k_asp}\n{get_notion_content(k_asp)}\n\n"
                    found = True
            if not found: content += f"No major aspects to South Node found.\n\n"
        
        # Chapter 22: Part of Fortune
        progress_bar.progress(98, text="98% - Generating Chapter 22: Part of Fortune...")
        content += sep + "# Chapter 22: Part of Fortune\n" + sep + "\n"
        h = chart["house_positions_eff"].get("Part of Fortune", 0.0)
        if h > 0:
            k = f"Part of Fortune in the {get_ordinal(int(h))} House"
            content += f"## {k}\n{get_notion_content(k)}\n\n"
        s = chart["placements"].get("Part of Fortune", "")
        k = f"Part of Fortune in {s}"
        content += f"## {k}\n{get_notion_content(k)}\n\n"
        
        progress_bar.progress(100, text="100% - Done!")
        st.success("Book Generated Successfully!")
        
        # Save to session state
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname = f"{c_name.replace(' ', '_')}_{ts}.txt"
        
        st.session_state.book_content = content
        st.session_state.book_filename = fname
        st.session_state.generation_complete = True
        
        # Reset Session State
        st.session_state.run_engine = False

    except Exception as e:
        st.error(f"Error: {e}\n\n{traceback.format_exc()}")

# --- RESULTS DISPLAY SECTION ---
if st.session_state.generation_complete:
    content = st.session_state.book_content
    fname = st.session_state.book_filename
    
    # Use saved chart data for consistency if available
    if st.session_state.chart_data:
        c_name = st.session_state.chart_data['name']
        c_date = st.session_state.chart_data['birth_date']
        c_time = st.session_state.chart_data['birth_time']
        c_city = st.session_state.chart_data['city']
        c_state = st.session_state.chart_data['state']
        c_country = st.session_state.chart_data['country']
        c_lat = st.session_state.chart_data['lat']
        c_lon = st.session_state.chart_data['lon']
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Add CSS to ensure consistent button styling
    st.markdown("""
    <style>
    /* Make all buttons have the same height and alignment */
    div.row-widget.stButton, div.row-widget.stDownloadButton {
        height: 44px !important;
        line-height: 44px !important;
    }
    
    /* Ensure all buttons have the same styling */
    div.row-widget.stButton button, div.row-widget.stDownloadButton button {
        background-color: #9370DB !important;
        color: white !important;
        height: 44px !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0 16px !important;
        line-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Hover effect */
    div.row-widget.stButton button:hover, div.row-widget.stDownloadButton button:hover {
        background-color: #8A2BE2 !important;
        box-shadow: 0 0 10px #9370DB !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a container for the buttons
    button_container = st.container()
    
    # Two-row button layout
    with button_container:
        # First row - Download button centered
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Book File",
                data=content,
                file_name=fname,
                use_container_width=True
            )
        
        # Add some vertical spacing
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Second row - Other two buttons
        col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
        
        # Generate Inside Pages button
        with col2:
            if st.button(
                "📓 Generate Inside Pages PDF",
                use_container_width=True,
                key="btn_inside_pages"
            ):
                st.info("This feature will be implemented in the next phase of the project.")
        
        # Generate Cover PDFs button
        with col3:
            if st.button(
                "📔 Generate Cover PDFs",
                use_container_width=True,
                key="btn_covers"
            ):
                # Store chart data in session state
                st.session_state.chart_data = {
                    'name': c_name,
                    'birth_date': c_date,
                    'birth_time': c_time,
                    'city': c_city,
                    'state': c_state,
                    'country': c_country,
                    'lat': c_lat,
                    'lon': c_lon
                }
                # Set flag to trigger cover generation
                st.session_state.generate_covers = True
                # Force page rerun to process the cover generation
                st.rerun()
        
    
    # Add JavaScript to scroll to bottom of page
    st.markdown("""
        <script>
            // Use setTimeout to ensure the DOM is fully loaded
            setTimeout(function() {
                window.scrollTo(0, document.body.scrollHeight);
            }, 500);
        </script>
    """, unsafe_allow_html=True)