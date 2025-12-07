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
# DATA LISTS
# ==========================================================
PLANETS = [
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", 
    "Uranus", "Neptune", "Pluto", "North Node", "South Node", 
    "Lilith", "Chiron", "Part of Fortune", "Ascendant", "Midheaven"
]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

MOON_PHASES = [
    "New Moon", "Waxing Moon", "Full Moon", "Waning Moon"
]

# ==========================================================
# THE ARCHITECT SCRIPT
# ==========================================================
def create_row(client, title_text):
    """Creates a single row in the database if it doesn't exist."""
    try:
        # 1. Check if it exists first
        query = client.databases.query(
            database_id=DATABASE_ID,
            filter={"property": "Placement", "title": {"equals": title_text}}
        )
        
        if len(query["results"]) > 0:
            print(f"⚠️  Skipping: '{title_text}' (Already exists)")
            return

        # 2. Create the row
        client.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Placement": {
                    "title": [{"text": {"content": title_text}}]
                }
            }
        )
        print(f"✅ Created: '{title_text}'")
        
        # Rate limit pause
        time.sleep(0.3) 

    except Exception as e:
        print(f"❌ Error creating '{title_text}': {e}")

def main():
    print("🏗️  Starting The Architect...")
    print("Connecting to Notion...")
    
    # Initialize Client
    notion = Client(auth=NOTION_TOKEN)
    
    print("\n--- 1. Generating Planets in Signs ---")
    for planet in PLANETS:
        for sign in SIGNS:
            key = f"{planet} in {sign}"
            create_row(notion, key)

    print("\n--- 2. Generating Planets in Houses ---")
    def get_ordinal(n):
        if 11 <= (n % 100) <= 13: suffix = 'th'
        else: suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    for planet in PLANETS:
        if planet in ["Ascendant", "Midheaven"]: continue
        for i in range(1, 13):
            house_str = get_ordinal(i)
            key = f"{planet} in the {house_str} House"
            create_row(notion, key)

    print("\n--- 3. Generating House Cusps (Signs on Houses) ---")
    for i in range(1, 13):
        house_str = get_ordinal(i)
        for sign in SIGNS:
            key = f"{sign} in the {house_str} House"
            create_row(notion, key)

    print("\n--- 4. Generating Moon Phases ---")
    for phase in MOON_PHASES:
        create_row(notion, phase)

    print("\n✨ Database Population Complete!")

if __name__ == "__main__":
    main()