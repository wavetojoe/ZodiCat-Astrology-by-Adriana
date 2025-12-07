import time
import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

# ==========================================================
# CONFIGURATION
# ==========================================================
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# ==========================================================
# DEFINING THE BOOK SEQUENCE
# ==========================================================
# We build the list exactly as the book presents it
MASTER_ORDER = []

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_ordinal(n):
    if 11 <= (n % 100) <= 13: suffix = 'th'
    else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# --- CHAPTER 1: PILLARS (Signs) ---
for sign in SIGNS: MASTER_ORDER.append(f"Ascendant in {sign}")
for sign in SIGNS: MASTER_ORDER.append(f"Sun in {sign}")
for sign in SIGNS: MASTER_ORDER.append(f"Moon in {sign}")

# --- CHAPTER 3: MOON PHASES ---
MASTER_ORDER.extend(["New Moon", "Waxing Moon", "Full Moon", "Waning Moon"])

# --- CHAPTER 4: HOUSE CUSPS (Signs on Houses) ---
for i in range(1, 13):
    h_str = get_ordinal(i)
    for sign in SIGNS:
        MASTER_ORDER.append(f"{sign} in the {h_str} House")

# --- CHAPTERS 7-22: PLANETS (House then Sign) ---
# Note: Sun/Moon/Asc in signs are already at top, but usually 
# we keep them grouped with their planet for editing sanity.
# However, to match book flow strictly, we process the rest here.

PLANETS_ORDER = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", 
    "Uranus", "Neptune", "Pluto", "Midheaven", "Lilith", "Chiron", 
    "North Node", "South Node", "Part of Fortune"
]

for planet in PLANETS_ORDER:
    # 1. House Placements
    # Asc/MC/Nodes don't usually get "In 1st House" text, but if you generated them, we sort them.
    # We'll skip Asc/MC houses as they are redundant.
    if planet not in ["Ascendant", "Midheaven"]:
        for i in range(1, 13):
            h_str = get_ordinal(i)
            MASTER_ORDER.append(f"{planet} in the {h_str} House")
    
    # 2. Sign Placements (avoiding duplicates if listed in Ch1)
    if planet not in ["Ascendant", "Sun", "Moon"]:
        for sign in SIGNS:
            MASTER_ORDER.append(f"{planet} in {sign}")

# ==========================================================
# THE SORTER SCRIPT
# ==========================================================
def main():
    print("📚 Organizing Library to match Book Order...")
    notion = Client(auth=NOTION_TOKEN)
    
    # 1. Fetch all rows (We need their Page IDs to update them)
    print("Fetching all existing rows from Notion (this may take a moment)...")
    all_pages = []
    has_more = True
    next_cursor = None
    
    while has_more:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            start_cursor=next_cursor
        )
        all_pages.extend(response["results"])
        has_more = response["has_more"]
        next_cursor = response["next_cursor"]
        
    print(f"Fetched {len(all_pages)} rows.")
    
    # 2. Create a Lookup Dictionary { "Sun in Aries": "page_id_123" }
    page_map = {}
    for page in all_pages:
        try:
            # Safely get the Title text
            props = page["properties"]["Placement"]
            if props["title"]:
                title_text = props["title"][0]["text"]["content"]
                page_map[title_text] = page["id"]
        except Exception as e:
            continue

    # 3. Update SortID based on MASTER_ORDER
    print("Updating SortIDs...")
    count = 0
    
    for index, key in enumerate(MASTER_ORDER):
        if key in page_map:
            page_id = page_map[key]
            
            # Update the row
            try:
                notion.pages.update(
                    page_id=page_id,
                    properties={
                        "SortID": {"number": index + 1}
                    }
                )
                print(f"✅ [{index+1}] Sorted: {key}")
                count += 1
                time.sleep(0.3) # Rate limiting
            except Exception as e:
                print(f"❌ Error updating {key}: {e}")
                
    print(f"\n✨ Done! Sorted {count} rows.")
    print("👉 Go to Notion, click the 'SortID' column header, and choose 'Sort Ascending'.")

if __name__ == "__main__":
    main()