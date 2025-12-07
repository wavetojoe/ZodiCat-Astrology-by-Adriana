// Simple InDesign test script
// This script will display an alert and create a log file on the desktop

function main() {
    try {
        // Create a log file on desktop
        var desktop = Folder.desktop;
        var logFile = new File(desktop + "/indesign_test_log.txt");
        logFile.open("w");
        logFile.write("InDesign script test run at: " + new Date().toString());
        logFile.write("\nInDesign version: " + app.version);
        logFile.close();
        
        // Show alert
        alert("InDesign test script executed successfully!\nLog file created on desktop.");
        
        return true;
    } catch (e) {
        alert("Error: " + e);
        return false;
    }
}

// Run the script
main();
