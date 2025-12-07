// Create InDesign Template for Astrology Chart Covers
// This script creates a template with placeholders for name, birth info, and location

// Main function
function main() {
    // Document properties
    var docWidth = 612; // 8.5 inches in points
    var docHeight = 792; // 11 inches in points
    var margins = 36; // 0.5 inches in points
    var bleed = 9; // 0.125 inches in points
    
    // Create a new document
    var doc = app.documents.add({
        documentPreferences: {
            pageWidth: docWidth,
            pageHeight: docHeight,
            pagesPerDocument: 2,
            facingPages: false,
            bleedTop: bleed,
            bleedBottom: bleed,
            bleedInside: bleed,
            bleedOutside: bleed
        }
    });
    
    // Set up margins
    doc.marginPreferences.top = margins;
    doc.marginPreferences.bottom = margins;
    doc.marginPreferences.left = margins;
    doc.marginPreferences.right = margins;
    
    // Get references to pages
    var blackPage = doc.pages[0]; // First page (black cover)
    var bluePage = doc.pages[1]; // Second page (blue cover)
    
    // Create black cover (page 1)
    createCoverPage(blackPage, [0, 0, 0], [255, 255, 255], [255, 215, 0]);
    
    // Create blue cover (page 2)
    createCoverPage(bluePage, [0, 0, 128], [255, 255, 255], [255, 215, 0]);
    
    // Save the template
    var saveDialog = File.saveDialog("Save template as", "InDesign Template:*.indt");
    if (saveDialog != null) {
        var saveFile = new File(saveDialog);
        doc.save(saveFile, true, "AstrologyChartTemplate", true);
        alert("Template saved successfully!");
    }
}

// Function to create a cover page with specified colors
function createCoverPage(page, bgColor, textColor, accentColor) {
    // Create background rectangle
    var bgRect = page.rectangles.add({
        geometricBounds: [0, 0, page.bounds[2], page.bounds[3]],
        fillColor: createColor("Cover BG", bgColor[0], bgColor[1], bgColor[2])
    });
    bgRect.sendToBack();
    
    // Create decorative elements (stars)
    createStarField(page, accentColor);
    
    // Text area bounds (within margins)
    var contentTop = page.marginPreferences.top;
    var contentLeft = page.marginPreferences.left;
    var contentBottom = page.bounds[2] - page.marginPreferences.bottom;
    var contentRight = page.bounds[3] - page.marginPreferences.right;
    var contentWidth = contentRight - contentLeft;
    var contentHeight = contentBottom - contentTop;
    
    // Create text frames
    
    // Name text frame (top third)
    var nameFrame = page.textFrames.add({
        geometricBounds: [
            contentTop + contentHeight * 0.2,
            contentLeft,
            contentTop + contentHeight * 0.4,
            contentRight
        ]
    });
    nameFrame.contents = "{{NAME}}";
    
    // Birth info text frame (middle)
    var birthFrame = page.textFrames.add({
        geometricBounds: [
            contentTop + contentHeight * 0.45,
            contentLeft,
            contentTop + contentHeight * 0.55,
            contentRight
        ]
    });
    birthFrame.contents = "{{BIRTH_INFO}}";
    
    // Location text frame (lower middle)
    var locationFrame = page.textFrames.add({
        geometricBounds: [
            contentTop + contentHeight * 0.6,
            contentLeft,
            contentTop + contentHeight * 0.7,
            contentRight
        ]
    });
    locationFrame.contents = "{{LOCATION}}";
    
    // Apply text formatting
    formatText(nameFrame, textColor, 36, "center", true);
    formatText(birthFrame, accentColor, 18, "center", false);
    formatText(locationFrame, textColor, 14, "center", false);
    
    // Add "Astrology Birth Chart" text at bottom
    var titleFrame = page.textFrames.add({
        geometricBounds: [
            contentBottom - 50,
            contentLeft,
            contentBottom,
            contentRight
        ]
    });
    titleFrame.contents = "Astrology Birth Chart";
    formatText(titleFrame, textColor, 16, "center", true);
}

// Function to format text
function formatText(textFrame, color, fontSize, alignment, isBold) {
    textFrame.texts[0].fillColor = createColor("Text Color", color[0], color[1], color[2]);
    textFrame.texts[0].pointSize = fontSize;
    
    if (alignment === "center") {
        textFrame.texts[0].justification = Justification.CENTER_ALIGN;
    } else if (alignment === "right") {
        textFrame.texts[0].justification = Justification.RIGHT_ALIGN;
    }
    
    if (isBold) {
        textFrame.texts[0].fontStyle = "Bold";
    }
}

// Function to create a color
function createColor(name, r, g, b) {
    var colorName = name + " [" + r + "," + g + "," + b + "]";
    var newColor;
    
    try {
        newColor = app.activeDocument.colors.itemByName(colorName);
        newColor.name; // Will throw error if color doesn't exist
    } catch (e) {
        newColor = app.activeDocument.colors.add({
            name: colorName,
            model: ColorModel.PROCESS,
            colorValue: [0, 0, 0, 0] // CMYK starting value
        });
        
        // Convert RGB to CMYK (simple conversion)
        var c = 1 - (r / 255);
        var m = 1 - (g / 255);
        var y = 1 - (b / 255);
        var k = Math.min(c, m, y);
        
        if (k == 1) {
            c = m = y = 0;
        } else {
            c = (c - k) / (1 - k);
            m = (m - k) / (1 - k);
            y = (y - k) / (1 - k);
        }
        
        newColor.colorValue = [c * 100, m * 100, y * 100, k * 100];
    }
    
    return newColor;
}

// Function to create decorative star field
function createStarField(page, starColor) {
    var starCount = 50;
    var bounds = page.bounds;
    var width = bounds[3] - bounds[1];
    var height = bounds[2] - bounds[0];
    var color = createColor("Star Color", starColor[0], starColor[1], starColor[2]);
    
    for (var i = 0; i < starCount; i++) {
        var x = Math.random() * width;
        var y = Math.random() * height;
        var size = Math.random() * 3 + 1;
        
        var star = page.ovals.add({
            geometricBounds: [y, x, y + size, x + size],
            fillColor: color,
            strokeColor: "None"
        });
    }
}

// Run the script
main();
