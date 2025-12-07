#!/bin/bash
# Shell script to generate PDFs directly without using Streamlit
# This bypasses any potential issues with Streamlit's execution environment

# Default values
NAME="Test User"
BIRTH_INFO="January 1, 2000 - 12:00 PM"
LOCATION="New York, NY, USA"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      NAME="$2"
      shift 2
      ;;
    --birth-info)
      BIRTH_INFO="$2"
      shift 2
      ;;
    --location)
      LOCATION="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Display the parameters
echo "Generating PDFs with the following parameters:"
echo "Name: $NAME"
echo "Birth Info: $BIRTH_INFO"
echo "Location: $LOCATION"
echo ""

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create a Python script that will be executed
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << EOL
#!/usr/bin/env python3
import os
import sys

# Add the script directory to the Python path
sys.path.insert(0, "$SCRIPT_DIR")

# Now import the module
from indesign_generator import generate_indesign_covers

# Parameters
name = "$NAME"
birth_info = "$BIRTH_INFO"
location = "$LOCATION"

print(f"Starting PDF generation for {name}")
print(f"Birth info: {birth_info}")
print(f"Location: {location}")

# Call the generator function
result = generate_indesign_covers(name, birth_info, location)

# Print result
if result['success']:
    print(f"\nSUCCESS: PDF covers generated successfully!")
    print(f"Output folder: {result['output_folder']}")
    
    # Check if PDFs were created
    black_pdf = os.path.join(result['output_folder'], f"{name}_Black_Cover.pdf")
    blue_pdf = os.path.join(result['output_folder'], f"{name}_Blue_Cover.pdf")
    
    print(f"Black PDF exists: {os.path.exists(black_pdf)}")
    print(f"Blue PDF exists: {os.path.exists(blue_pdf)}")
    
    sys.exit(0)
else:
    print(f"\nERROR: Failed to generate PDF covers")
    print(f"Error: {result['error']}")
    sys.exit(1)
EOL

# Make the script executable
chmod +x "$TEMP_SCRIPT"

# Execute the script
echo "Executing PDF generation script..."
python3 "$TEMP_SCRIPT"

# Capture the exit code
EXIT_CODE=$?

# Clean up
rm "$TEMP_SCRIPT"

# Exit with the same code as the Python script
exit $EXIT_CODE
