// Test script to verify PDF export functionality
// This script attempts to open the template and export a PDF

function main() {
    try {
        // Create a log file on desktop
        var desktop = Folder.desktop;
        var logFile = new File(desktop + "/indesign_pdf_test_log.txt");
        logFile.open("w");
        logFile.write("InDesign PDF export test run at: " + new Date().toString() + "\n");
        
        // Define template path
        var templatePath = "/Users/joejoseph/Desktop/ASTROLOGYBOOKBOT/INDESIGN FILES/Cover - AstroBookGenerator.indt";
        logFile.write("Template path: " + templatePath + "\n");
        
        // Define output path
        var outputPath = desktop + "/test_export.pdf";
        logFile.write("Output path: " + outputPath + "\n");
        
        // Check if template exists
        var templateFile = new File(templatePath);
        if (templateFile.exists) {
            logFile.write("Template file exists\n");
            
            // Try to open the template
            try {
                var doc = app.open(templateFile);
                logFile.write("Template opened successfully\n");
                
                // Try to export as PDF
                try {
                    // Create PDF export preferences
                    var pdfExportPrefs = app.pdfExportPreferences;
                    
                    // Store original settings
                    var originalPageRange = pdfExportPrefs.pageRange;
                    
                    // Set to export only page 1
                    pdfExportPrefs.pageRange = "1";
                    logFile.write("Set to export page 1\n");
                    
                    // Set output path
                    var outputFile = new File(outputPath);
                    
                    // Export the PDF
                    logFile.write("Attempting to export PDF...\n");
                    doc.exportFile(ExportFormat.pdfType, outputFile, false, "[High Quality Print]");
                    logFile.write("PDF exported successfully\n");
                    
                    // Restore original settings
                    pdfExportPrefs.pageRange = originalPageRange;
                } catch (exportError) {
                    logFile.write("Error exporting PDF: " + exportError + "\n");
                }
                
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
        alert("InDesign PDF export test completed!\nLog file created on desktop.");
        
        return true;
    } catch (e) {
        alert("Error: " + e);
        return false;
    }
}

// Run the script
main();
