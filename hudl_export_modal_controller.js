// Hudl Instat Export Modal Controller
// This script interacts with the export modal to select metrics and download CSV

console.log("🎯 Hudl Instat Export Modal Controller");
console.log("=" * 50);

// Function to open the export modal
function openExportModal() {
    console.log("🔍 Looking for download button to open export modal...");
    
    // Find the download button/icon
    const downloadButton = document.querySelector('.styled__DownloadIcon-sc-1s49rmo-1.dMcfbw') || 
                          document.querySelector('.styled__DownloadLink-sc-1g74es8-2.dWiDJQ');
    
    if (downloadButton) {
        console.log("✅ Found download button, clicking to open modal...");
        downloadButton.click();
        
        // Wait for modal to appear
        setTimeout(() => {
            checkExportModal();
        }, 1000);
    } else {
        console.log("❌ Download button not found");
    }
}

// Function to check if export modal is open
function checkExportModal() {
    console.log("🔍 Checking for export modal...");
    
    const modal = document.querySelector('.styled__ModalWrapper-sc-1s49rmo-0.beTTEu');
    
    if (modal) {
        console.log("✅ Export modal is open!");
        console.log("📊 Modal structure found:");
        console.log("   - Title: Export");
        console.log("   - Tabs: Players | Teams");
        console.log("   - Format: CSV");
        console.log("   - Language: English");
        
        // Analyze available metrics
        analyzeAvailableMetrics();
        
        // Select play-by-play relevant metrics
        selectPlayByPlayMetrics();
        
    } else {
        console.log("❌ Export modal not found");
        console.log("💡 Try clicking the download button first");
    }
}

// Function to analyze available metrics in the modal
function analyzeAvailableMetrics() {
    console.log("\n📊 Analyzing available metrics...");
    
    const metricSections = [
        'Shifts',
        'Main statistics', 
        'Shots',
        'Puck battles',
        'Passes',
        'Recoveries and losses',
        'Entries and Breakouts',
        'Faceoffs by zones',
        'Goalie'
    ];
    
    metricSections.forEach(section => {
        const sectionElement = document.querySelector(`[data-lexic*="${section}"]`);
        if (sectionElement) {
            console.log(`✅ Found section: ${section}`);
            
            // Count checkboxes in this section
            const checkboxes = sectionElement.closest('.BlockTitle-sc-9ex20g-0')?.nextElementSibling?.querySelectorAll('input[type="checkbox"]');
            if (checkboxes) {
                console.log(`   📋 ${checkboxes.length} metrics available`);
            }
        } else {
            console.log(`❌ Section not found: ${section}`);
        }
    });
}

// Function to select play-by-play relevant metrics
function selectPlayByPlayMetrics() {
    console.log("\n🎯 Selecting play-by-play relevant metrics...");
    
    // Define play-by-play relevant metrics
    const playByPlayMetrics = [
        'All shifts',
        'Goals',
        'Assists', 
        'Shots',
        'Shots on goal',
        'Blocked shots',
        'Missed shots',
        'Passes',
        'Accurate passes',
        'Puck battles',
        'Puck battles won',
        'Puck recoveries',
        'Puck losses',
        'Entries',
        'Breakouts',
        'Faceoffs',
        'Faceoffs won',
        'Faceoffs lost'
    ];
    
    let selectedCount = 0;
    
    playByPlayMetrics.forEach(metric => {
        // Find checkbox for this metric
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            const label = checkbox.closest('label') || checkbox.parentElement;
            if (label && label.textContent.includes(metric)) {
                if (!checkbox.checked) {
                    checkbox.click();
                    console.log(`✅ Selected: ${metric}`);
                    selectedCount++;
                } else {
                    console.log(`✓ Already selected: ${metric}`);
                }
            }
        });
    });
    
    console.log(`\n📊 Selected ${selectedCount} play-by-play metrics`);
}

// Function to select all players
function selectAllPlayers() {
    console.log("\n👥 Selecting all players...");
    
    // Find all player checkboxes
    const playerCheckboxes = document.querySelectorAll('.PopupPlayerCheckbox__BlockCheckbox-sc-8e5qsi-0 input[type="checkbox"]');
    
    let selectedPlayers = 0;
    playerCheckboxes.forEach(checkbox => {
        if (!checkbox.checked) {
            checkbox.click();
            selectedPlayers++;
        }
    });
    
    console.log(`✅ Selected ${selectedPlayers} players`);
}

// Function to select all periods
function selectAllPeriods() {
    console.log("\n⏰ Selecting all periods...");
    
    const periodCheckboxes = document.querySelectorAll('.styled__CustomBlockCheckbox-sc-arhjlr-0 input[type="checkbox"]');
    
    let selectedPeriods = 0;
    periodCheckboxes.forEach(checkbox => {
        if (!checkbox.checked) {
            checkbox.click();
            selectedPeriods++;
        }
    });
    
    console.log(`✅ Selected ${selectedPeriods} periods`);
}

// Function to confirm export and download
function confirmExport() {
    console.log("\n💾 Confirming export and downloading CSV...");
    
    // Find the OK button
    const okButton = document.querySelector('.styled__Button-sc-1qmng2y-2.lbnSyW');
    
    if (okButton) {
        console.log("✅ Found OK button, clicking to start download...");
        okButton.click();
        
        // Wait for download to start
        setTimeout(() => {
            checkForDownload();
        }, 2000);
    } else {
        console.log("❌ OK button not found");
    }
}

// Function to check if download started
function checkForDownload() {
    console.log("\n🔍 Checking for download...");
    
    // Check for download links
    const downloadLinks = document.querySelectorAll('a[href*=".csv"], a[href*="download"]');
    
    if (downloadLinks.length > 0) {
        console.log(`✅ Found ${downloadLinks.length} download links:`);
        downloadLinks.forEach((link, index) => {
            console.log(`   ${index + 1}. ${link.href}`);
        });
    } else {
        console.log("📥 No download links found yet");
        console.log("💡 Check your browser's download folder");
    }
}

// Function to run complete export process
function runCompleteExport() {
    console.log("🚀 Starting complete export process...");
    
    // Step 1: Open modal
    openExportModal();
    
    // Step 2: Wait and select metrics
    setTimeout(() => {
        selectPlayByPlayMetrics();
        selectAllPlayers();
        selectAllPeriods();
        
        // Step 3: Confirm export
        setTimeout(() => {
            confirmExport();
        }, 1000);
    }, 2000);
}

// Function to get current modal state
function getModalState() {
    const modal = document.querySelector('.styled__ModalWrapper-sc-1s49rmo-0.beTTEu');
    
    if (!modal) {
        console.log("❌ Export modal is not open");
        return null;
    }
    
    const state = {
        isOpen: true,
        selectedMetrics: [],
        selectedPlayers: [],
        selectedPeriods: [],
        format: 'CSV',
        language: 'English'
    };
    
    // Get selected metrics
    const metricCheckboxes = document.querySelectorAll('.BlockCheckbox-sc-10q8fbq-0 input[type="checkbox"]:checked');
    metricCheckboxes.forEach(checkbox => {
        const label = checkbox.closest('label') || checkbox.parentElement;
        if (label) {
            state.selectedMetrics.push(label.textContent.trim());
        }
    });
    
    // Get selected players
    const playerCheckboxes = document.querySelectorAll('.PopupPlayerCheckbox__BlockCheckbox-sc-8e5qsi-0 input[type="checkbox"]:checked');
    playerCheckboxes.forEach(checkbox => {
        const label = checkbox.closest('label') || checkbox.parentElement;
        if (label) {
            state.selectedPlayers.push(label.textContent.trim());
        }
    });
    
    // Get selected periods
    const periodCheckboxes = document.querySelectorAll('.styled__CustomBlockCheckbox-sc-arhjlr-0 input[type="checkbox"]:checked');
    periodCheckboxes.forEach(checkbox => {
        const label = checkbox.closest('label') || checkbox.parentElement;
        if (label) {
            state.selectedPeriods.push(label.textContent.trim());
        }
    });
    
    console.log("📊 Current modal state:", state);
    return state;
}

// Export functions for use
window.hudlExport = {
    openModal: openExportModal,
    checkModal: checkExportModal,
    selectMetrics: selectPlayByPlayMetrics,
    selectPlayers: selectAllPlayers,
    selectPeriods: selectAllPeriods,
    confirmExport: confirmExport,
    runComplete: runCompleteExport,
    getState: getModalState
};

console.log("\n✅ Hudl Export Controller loaded!");
console.log("📋 Available functions:");
console.log("   hudlExport.openModal() - Open the export modal");
console.log("   hudlExport.checkModal() - Check if modal is open");
console.log("   hudlExport.selectMetrics() - Select play-by-play metrics");
console.log("   hudlExport.selectPlayers() - Select all players");
console.log("   hudlExport.selectPeriods() - Select all periods");
console.log("   hudlExport.confirmExport() - Confirm and download");
console.log("   hudlExport.runComplete() - Run complete export process");
console.log("   hudlExport.getState() - Get current modal state");

// Auto-run if modal is already open
if (document.querySelector('.styled__ModalWrapper-sc-1s49rmo-0.beTTEu')) {
    console.log("🎯 Export modal is already open, analyzing...");
    checkExportModal();
}
