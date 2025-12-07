# InDesign Integration for AstroBookGenerator

This feature allows you to generate custom InDesign covers for astrology birth chart reports. The system creates two PDF covers - one with a black background and one with a blue background.

## Setup Instructions

### 1. Create an InDesign Template

You have two options:

#### Option A: Create the template manually
Follow the instructions in `indesign_template_instructions.md` to create your template in InDesign.

#### Option B: Use the provided script
1. Open Adobe InDesign
2. Go to File > Scripts > Scripts Panel
3. Right-click in the Scripts Panel and select "Reveal in Finder" (Mac) or "Reveal in Explorer" (Windows)
4. Copy `create_indesign_template.jsx` to the Scripts Panel folder
5. Back in InDesign, double-click the script in the Scripts Panel
6. Follow the prompts to save your template

### 2. Update the Template Path

1. Open `indesign_generator.py` in a text editor
2. Find this line (around line 60):
   ```python
   template_path = "/path/to/your/template.indt"
   ```
3. Replace with the actual path to your template file, for example:
   ```python
   template_path = "/Users/joejoseph/Desktop/AstroBookGenerator/AstrologyChartTemplate.indt"
   ```

## Using the Feature

1. Run the astrology chart generator application (`gui_ready.py`)
2. Enter birth information and generate a chart
3. In the results dialog, click the "Generate InDesign Cover" button
4. The system will:
   - Create a folder on your desktop with the person's name
   - Open your InDesign template
   - Replace placeholder text with actual data
   - Export two PDFs (black and blue covers)
   - Save them to the folder

## Placeholder Text

The script replaces the following placeholders in your InDesign document:

- `{{NAME}}` - The person's name
- `{{BIRTH_INFO}}` - Birth date and time formatted as "May 10, 2005 - 6:04 AM"
- `{{LOCATION}}` - Birth location formatted as "City, State, Country"

## Troubleshooting

### InDesign Not Found
If the script cannot find InDesign, you may need to update the paths in `indesign_generator.py`. Look for the `_run_indesign_script` function and update the InDesign paths for your system.

### Template Path Issues
Make sure the template path is correct and uses the proper format for your operating system:
- Mac: `/Users/username/path/to/template.indt`
- Windows: `C:\\Users\\username\\path\\to\\template.indt` (note the double backslashes)

### Placeholder Text Not Replaced
Ensure that your template uses the exact placeholder text format: `{{NAME}}`, `{{BIRTH_INFO}}`, and `{{LOCATION}}`.
