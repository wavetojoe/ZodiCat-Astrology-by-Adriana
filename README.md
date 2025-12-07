# AstroBookBot PDF Cover Generator

This project includes functionality to generate custom InDesign covers for astrology birth chart reports.

## PDF Generation Issue and Solution

There appears to be an issue with generating PDF covers through the Streamlit interface. The buttons in the Streamlit app that attempt to generate PDFs cause the app to reset without completing the PDF generation.

### Working Solution: Use the Shell Script

A shell script has been created that successfully generates the PDF covers. To use it:

1. Open Terminal
2. Navigate to the project directory:
   ```
   cd /Users/joejoseph/Desktop/ASTROLOGYBOOKBOT
   ```
3. Run the script with your desired parameters:
   ```
   ./generate_pdfs.sh --name "Your Name" --birth-info "January 1, 2000 - 12:00 PM" --location "New York, NY, USA"
   ```

The script will generate two PDF covers (black and blue) and save them to a folder on your desktop named after the person (e.g., `Your_Name_Covers`).

### Technical Details

The issue appears to be related to how Streamlit handles external processes and UI updates. The InDesign integration works correctly when run from a shell script or standalone Python script, but not when triggered from within the Streamlit app.

Possible causes:
1. Streamlit's rerun mechanism interrupts the InDesign process
2. The UI updates during PDF generation interfere with the process
3. There may be environment or permission issues when running through Streamlit

### Future Improvements

To integrate this functionality back into the Streamlit app, consider:
1. Creating a separate microservice for PDF generation
2. Using a message queue to handle the PDF generation asynchronously
3. Implementing a webhook or callback mechanism to notify when PDFs are ready

## Template Information

The InDesign template is located at:
```
/Users/joejoseph/Desktop/ASTROLOGYBOOKBOT/INDESIGN FILES/Cover - AstroBookGenerator.indt
```

This template contains placeholders for:
- `{{NAME}}` - The person's name
- `{{BIRTH_INFO}}` - Birth date and time
- `{{LOCATION}}` - Birth location
