#!/usr/bin/env python3
"""
Test script to directly call the generate_indesign_covers function
without going through the Streamlit app.
"""

import os
import sys
from indesign_generator import generate_indesign_covers

def main():
    print("Starting direct test of InDesign cover generation")
    
    # Test data
    name = "Test Direct"
    birth_info = "January 1, 2000 - 12:00 PM"
    location = "New York, NY, USA"
    
    print(f"Generating covers for {name}")
    print(f"Birth info: {birth_info}")
    print(f"Location: {location}")
    
    # Call the function
    result = generate_indesign_covers(name, birth_info, location)
    
    # Print result
    print("\nRESULT:")
    print(f"Success: {result['success']}")
    print(f"Output folder: {result.get('output_folder')}")
    print(f"Error: {result.get('error')}")
    
    # Check if PDFs were created
    if result['success'] and result.get('output_folder'):
        output_folder = result['output_folder']
        black_pdf = os.path.join(output_folder, f"{name}_Black_Cover.pdf")
        blue_pdf = os.path.join(output_folder, f"{name}_Blue_Cover.pdf")
        
        print("\nCHECKING FILES:")
        print(f"Black PDF exists: {os.path.exists(black_pdf)}")
        print(f"Blue PDF exists: {os.path.exists(blue_pdf)}")
        
        if os.path.exists(black_pdf):
            print(f"Black PDF size: {os.path.getsize(black_pdf)} bytes")
        if os.path.exists(blue_pdf):
            print(f"Blue PDF size: {os.path.getsize(blue_pdf)} bytes")

if __name__ == "__main__":
    main()
