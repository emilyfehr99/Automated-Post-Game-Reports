// Hudl Instat Download Button Checker
// Run this in the browser console on the Hudl Instat page

console.log("🔍 Checking Hudl Instat Download Button...");

// Find the specific download button you identified
const downloadButton = document.querySelector('.styled__DownloadIcon-sc-1s49rmo-1.dMcfbw');

if (downloadButton) {
    console.log("✅ Found the download button!");
    
    // Get the parent element (likely the actual button)
    const parentButton = downloadButton.closest('button, a, [role="button"]');
    
    if (parentButton) {
        console.log("📊 Download Button Details:");
        console.log("   Element:", parentButton);
        console.log("   Tag:", parentButton.tagName);
        console.log("   Text:", parentButton.textContent?.trim());
        console.log("   Title:", parentButton.title);
        console.log("   Class:", parentButton.className);
        console.log("   ID:", parentButton.id);
        console.log("   Visible:", parentButton.offsetParent !== null);
        console.log("   Enabled:", !parentButton.disabled);
        
        // Check for data attributes
        const dataAttributes = {};
        Array.from(parentButton.attributes).forEach(attr => {
            if (attr.name.startsWith('data-')) {
                dataAttributes[attr.name] = attr.value;
            }
        });
        console.log("   Data Attributes:", dataAttributes);
        
        // Check for click handlers
        console.log("   Has Click Handler:", parentButton.onclick !== null);
        
        // Get the context (what section this button is in)
        const section = parentButton.closest('.section, .tab, .panel, .container, .content');
        if (section) {
            console.log("   Section Class:", section.className);
            console.log("   Section Text:", section.textContent?.substring(0, 100) + "...");
        }
        
    } else {
        console.log("❌ Could not find parent button element");
    }
} else {
    console.log("❌ Download button not found with that class");
}

// Find all download-related buttons and icons
console.log("\n🔍 Finding all download-related elements...");

const allDownloadElements = document.querySelectorAll('[class*="download"], [class*="Download"], [class*="export"], [class*="Export"]');

console.log(`📊 Found ${allDownloadElements.length} download-related elements:`);

allDownloadElements.forEach((element, index) => {
    const parent = element.closest('button, a, [role="button"]');
    if (parent) {
        console.log(`\n${index + 1}. Download Element:`);
        console.log(`   Text: "${parent.textContent?.trim()}"`);
        console.log(`   Title: "${parent.title}"`);
        console.log(`   Class: "${parent.className}"`);
        console.log(`   Visible: ${parent.offsetParent !== null}`);
        console.log(`   Enabled: ${!parent.disabled}`);
        
        // Check if it's in a play-by-play or events section
        const section = parent.closest('.section, .tab, .panel, .container, .content');
        if (section) {
            const sectionText = section.textContent?.toLowerCase() || '';
            const isPlayByPlay = sectionText.includes('play') || 
                                sectionText.includes('event') || 
                                sectionText.includes('timeline') ||
                                sectionText.includes('sequence');
            console.log(`   In Play-by-Play Section: ${isPlayByPlay}`);
        }
    }
});

// Find all buttons with download/export text
console.log("\n🔍 Finding all buttons with download/export text...");

const allButtons = document.querySelectorAll('button, a, [role="button"]');
const exportButtons = [];

allButtons.forEach(button => {
    const text = button.textContent?.toLowerCase() || '';
    const title = button.title?.toLowerCase() || '';
    
    if (text.includes('download') || text.includes('export') || 
        text.includes('csv') || title.includes('download') || 
        title.includes('export')) {
        exportButtons.push(button);
    }
});

console.log(`📊 Found ${exportButtons.length} buttons with download/export text:`);

exportButtons.forEach((button, index) => {
    console.log(`\n${index + 1}. Export Button:`);
    console.log(`   Text: "${button.textContent?.trim()}"`);
    console.log(`   Title: "${button.title}"`);
    console.log(`   Class: "${button.className}"`);
    console.log(`   Visible: ${button.offsetParent !== null}`);
    console.log(`   Enabled: ${!button.disabled}`);
    
    // Check if it's in a play-by-play section
    const section = button.closest('.section, .tab, .panel, .container, .content');
    if (section) {
        const sectionText = section.textContent?.toLowerCase() || '';
        const isPlayByPlay = sectionText.includes('play') || 
                            sectionText.includes('event') || 
                            sectionText.includes('timeline') ||
                            sectionText.includes('sequence');
        console.log(`   In Play-by-Play Section: ${isPlayByPlay}`);
    }
});

// Test clicking the download button
console.log("\n🧪 Testing download button click...");

if (downloadButton) {
    const parentButton = downloadButton.closest('button, a, [role="button"]');
    if (parentButton && !parentButton.disabled) {
        console.log("🖱️  Clicking download button...");
        try {
            parentButton.click();
            console.log("✅ Click successful - check for download or popup");
        } catch (error) {
            console.log("❌ Click failed:", error);
        }
    } else {
        console.log("⚠️  Download button not clickable");
    }
} else {
    console.log("❌ No download button found to test");
}

// Look for any download links or forms that might be generated
setTimeout(() => {
    console.log("\n🔍 Checking for generated download links...");
    
    const downloadLinks = document.querySelectorAll('a[href*=".csv"], a[href*="download"], a[href*="export"]');
    if (downloadLinks.length > 0) {
        console.log(`📥 Found ${downloadLinks.length} download links:`);
        downloadLinks.forEach((link, index) => {
            console.log(`   ${index + 1}. ${link.href}`);
        });
    } else {
        console.log("📥 No download links found");
    }
}, 2000);

console.log("\n✅ Download button analysis complete!");
