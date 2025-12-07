#!/usr/bin/env python3
"""
Direct PDF generator for AstroBookBot
This script directly generates PDFs without any UI, taking parameters from the command line.
"""

import os
import sys
import argparse
from indesign_generator import generate_indesign_covers

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate InDesign PDF covers for astrology charts')
    parser.add_argument('--name', required=True, help='Person\'s name')
    parser.add_argument('--birth-info', required=True, help='Birth date and time (e.g., "January 1, 2000 - 12:00 PM")')
    parser.add_argument('--location', required=True, help='Birth location (e.g., "New York, NY, USA")')
    
    args = parser.parse_args()
    
    print(f"Generating covers for {args.name}")
    print(f"Birth info: {args.birth_info}")
    print(f"Location: {args.location}")
    
    # Call the generator function
    result = generate_indesign_covers(args.name, args.birth_info, args.location)
    
    # Print result
    if result['success']:
        print(f"\nSUCCESS: PDF covers generated successfully!")
        print(f"Output folder: {result['output_folder']}")
        
        # Check if PDFs were created
        black_pdf = os.path.join(result['output_folder'], f"{args.name}_Black_Cover.pdf")
        blue_pdf = os.path.join(result['output_folder'], f"{args.name}_Blue_Cover.pdf")
        
        print(f"Black PDF exists: {os.path.exists(black_pdf)}")
        print(f"Blue PDF exists: {os.path.exists(blue_pdf)}")
        
        return 0
    else:
        print(f"\nERROR: Failed to generate PDF covers")
        print(f"Error: {result['error']}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
