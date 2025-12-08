#!/usr/bin/env python3
"""
Standalone utility script to regenerate all pie charts.
This script contains a copy of the generate_pie_chart function from APP_MAIN.py
to avoid dependencies on streamlit.
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

# Define paths
current_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(current_dir, "assets", "pie_charts")

# Define font paths - use system fonts if custom fonts not available
try:
    FONT_REGULAR = os.path.join(current_dir, "INDESIGN FILES", "Document fonts", "ArsenicaTrial-Regular.ttf")
    if not os.path.exists(FONT_REGULAR):
        FONT_REGULAR = None  # Will use default system font
except:
    FONT_REGULAR = None

def generate_pie_chart(stats_dict, filename, title):
    """Generate a pie chart with optimized appearance and save it to the specified file.
    
    This function creates a pie chart with the following features:
    - Large size that fills most of the image height
    - No white dividing lines between segments
    - Properly positioned percentage labels with small font size
    - Reduced legend font size
    - Overall image dimensions of 160mm x 100mm x 300dpi
    """
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

    # Set exact dimensions: 160mm × 100mm at 300 DPI
    width_mm = 160  # Figure width in mm
    height_mm = 100  # Figure height in mm
    
    # Convert mm to inches for figsize
    width_inches = width_mm / 25.4  # 160mm = 6.3 inches
    height_inches = height_mm / 25.4  # 100mm = 3.94 inches
    
    # Create figure with exact dimensions
    fig = plt.figure(figsize=(width_inches, height_inches), dpi=300)
    
    # Create axes that take up almost the entire figure
    # The position is [left, bottom, width, height] in figure coordinates (0-1)
    # Using the full figure area for a much larger pie chart
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    
    # Set white background
    fig.patch.set_facecolor('white')
    
    # Make the pie chart fill almost the entire height of the image
    # Using a much larger radius to create a pie chart that fills most of the image
    # This creates a pie chart that's approximately 95mm in height (95% of image height)
    radius_fraction = 0.8
    
    # For a donut chart, set the width_fraction to create a hole in the center
    # This creates a ring with inner radius of 60% of the outer radius (twice as large hole)
    width_fraction = 0.6
    
    # Create a donut chart by specifying wedgeprops with width parameter
    # Remove the white dividing lines by setting edgecolor to None and linewidth to 0
    wedges, texts = ax.pie(sizes, 
                   startangle=90, 
                   colors=chart_colors, 
                   wedgeprops={'edgecolor': None, 'linewidth': 0, 'width': 1-width_fraction},
                   center=(0, 0),
                   radius=radius_fraction)
    
    # Add percentage annotations manually with improved positioning
    total = sum(sizes)
    for i, wedge in enumerate(wedges):
        percent = int(round(sizes[i] / total * 100))
        
        # Calculate the angle at the center of the wedge in radians
        # We use the average of the start and end angles
        angle = (wedge.theta1 + wedge.theta2) / 2
        angle_rad = np.radians(angle)
        
        # Calculate the position for the text at exactly 50% from inner to outer radius
        # Get the wedge size in degrees (not used for positioning but kept for reference)
        wedge_size = wedge.theta2 - wedge.theta1
        
        # Calculate the inner and outer radius of the donut
        inner_radius = radius_fraction * width_fraction
        outer_radius = radius_fraction
        
        # Position all labels at exactly 40% from inner to outer radius
        radius_factor = inner_radius + (outer_radius - inner_radius) * 0.4
            
        # Convert to cartesian coordinates
        x = radius_factor * np.cos(angle_rad)
        y = radius_factor * np.sin(angle_rad)
        
        # Add the text with the percentage - small font size (8pt)
        ax.text(x, y, f"{percent}%", 
                ha='center', va='center', 
                fontsize=8)
    
    # Apply custom font to the text elements if available
    if FONT_REGULAR:
        legend_font = fm.FontProperties(fname=FONT_REGULAR, size=8)  # Reduced font size (8pt)
    
    # Create a more compact legend with color squares
    legend_elements = []
    
    # Create legend elements with just the labels (no percentages)
    for l, c in zip(labels, chart_colors):
        # Create a patch for the color with just the label
        legend_elements.append(plt.Rectangle((0, 0), 0.8, 0.8, fc=c, label=l))
    
    # Position legend in bottom right with reduced font size
    legend_font = fm.FontProperties(fname=FONT_REGULAR, size=8) if FONT_REGULAR else None
    
    # Position the legend at the bottom right of the 160mm x 100mm image
    legend = ax.legend(handles=legend_elements, 
                      bbox_to_anchor=(0.99, 0.01),
                      loc='lower right',
                      frameon=False,
                      prop=legend_font,
                      ncol=1,
                      labelspacing=0.3,
                      handlelength=1.0,
                      handletextpad=0.5,
                      borderaxespad=0.5)
                      
    # Save the figure with exact dimensions
    save_path = os.path.join(assets_dir, filename)
    plt.savefig(save_path, bbox_inches=None, transparent=False, facecolor='white', dpi=300)
    plt.close()
    print(f"Generated chart: {save_path}")
    return save_path

def get_sample_data(chart_type):
    """Return sample data for different chart types"""
    if chart_type == "modalities":
        return {"Cardinal": 33, "Fixed": 42, "Mutable": 25}
    elif chart_type == "elements":
        return {"Fire": 8, "Earth": 17, "Air": 33, "Water": 42}
    elif chart_type == "polarities":
        return {"Yang": 58, "Yin": 42}
    elif chart_type == "superior_inferior":
        return {"Superior": 67, "Inferior": 33}
    elif chart_type == "primitive_qualities":
        return {"Hot & Dry": 10, "Hot & Wet": 32, "Cold & Dry": 14, "Cold & Wet": 44}
    elif chart_type == "temperaments":
        return {"Choleric": 10, "Sanguine": 32, "Melancholic": 14, "Phlegmatic": 44}
    elif chart_type == "eastern_western":
        return {"Eastern": 25, "Western": 75}
    else:
        # Default sample data
        return {"A": 25, "B": 30, "C": 45}

def main():
    """Regenerate all pie charts using the updated generate_pie_chart function"""
    # List of pie charts to update
    pie_charts = [
        "modalities.png",
        "elements.png",
        "polarities.png",
        "superior_inferior.png",
        "eastern_western.png",
        "temperaments.png",
        "primitive_qualities.png"
    ]
    
    # Process each pie chart
    for chart_name in pie_charts:
        # Get the base name without extension
        base_name = os.path.splitext(chart_name)[0]
        
        # Get appropriate sample data for this chart type
        stats = get_sample_data(base_name)
        
        # Generate the chart with the updated settings
        output_path = generate_pie_chart(stats, chart_name, base_name.upper())
        
        if output_path:
            print(f"Successfully regenerated {chart_name}")
        else:
            print(f"Failed to regenerate {chart_name}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
