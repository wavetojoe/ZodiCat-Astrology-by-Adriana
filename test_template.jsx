// Test script to verify InDesign template can be opened
// This script attempts to open the template file and logs the result

function main() {
    try {
        // Create a log file on desktop
        var desktop = Folder.desktop;
        var logFile = new File(desktop + "/indesign_template_test_log.txt");
        logFile.open("w");
        logFile.write("InDesign template test run at: " + new Date().toString() + "\n");
        
        // Define template path
        var templatePath = "/Users/joejoseph/Desktop/ASTROLOGYBOOKBOT/INDESIGN FILES/Cover - AstroBookGenerator.indt";
        logFile.write("Template path: " + templatePath + "\n");
        
        // Check if template exists
        var templateFile = new File(templatePath);
        if (templateFile.exists) {
            logFile.write("Template file exists\n");
            
            // Try to open the template
            try {
                var doc = app.open(templateFile);
                logFile.write("Template opened successfully\n");
                
                // Get document info
                logFile.write("Document name: " + doc.name + "\n");
                logFile.write("Number of pages: " + doc.pages.length + "\n");
                
                // Close without saving
                doc.close(SaveOptions.NO);
                logFile.write("Document closed\n");
            } catch (openError) {
                logFile.write("Error opening template: " + openError + "\n");
            }
        } else {
            logFile.write("Template file does not exist\n");
        }
        
        logFile.close();
        alert("InDesign template test completed!\nLog file created on desktop.");
        
        return true;
    } catch (e) {
        alert("Error: " + e);
        return false;
    }
}

// Run the script
main();
