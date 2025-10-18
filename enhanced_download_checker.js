// Enhanced Hudl Instat Download Button Checker
// Run this in the browser console on the Hudl Instat page

console.log("🔍 Enhanced Download Button Analysis...");

// Find the specific download button you identified
const downloadButton = document.querySelector('.styled__DownloadIcon-sc-1s49rmo-1.dMcfbw');
const downloadLink = document.querySelector('.styled__DownloadLink-sc-1g74es8-2.dWiDJQ');

console.log("📊 Download Elements Found:");
console.log("   Icon:", downloadButton ? "✅ Found" : "❌ Not found");
console.log("   Link:", downloadLink ? "✅ Found" : "❌ Not found");

if (downloadLink) {
    console.log("\n🔍 Download Link Details:");
    console.log("   Element:", downloadLink);
    console.log("   Tag:", downloadLink.tagName);
    console.log("   Text:", downloadLink.textContent?.trim());
    console.log("   Title:", downloadLink.title);
    console.log("   Class:", downloadLink.className);
    console.log("   ID:", downloadLink.id);
    console.log("   Href:", downloadLink.href);
    console.log("   Visible:", downloadLink.offsetParent !== null);
    console.log("   Display:", window.getComputedStyle(downloadLink).display);
    console.log("   Visibility:", window.getComputedStyle(downloadLink).visibility);
    console.log("   Opacity:", window.getComputedStyle(downloadLink).opacity);
    
    // Check parent elements
    let parent = downloadLink.parentElement;
    let level = 0;
    while (parent && level < 5) {
        console.log(`   Parent ${level + 1}:`, parent.tagName, parent.className);
        console.log(`     Display: ${window.getComputedStyle(parent).display}`);
        console.log(`     Visibility: ${window.getComputedStyle(parent).visibility}`);
        console.log(`     Opacity: ${window.getComputedStyle(parent).opacity}`);
        parent = parent.parentElement;
        level++;
    }
}

// Find ALL download-related elements with different selectors
console.log("\n🔍 Finding ALL download-related elements...");

const downloadSelectors = [
    '[class*="download"]',
    '[class*="Download"]',
    '[class*="export"]',
    '[class*="Export"]',
    '[class*="csv"]',
    '[class*="CSV"]',
    '[class*="play"]',
    '[class*="Play"]',
    '[class*="event"]',
    '[class*="Event"]',
    '[class*="timeline"]',
    '[class*="Timeline"]',
    'a[href*=".csv"]',
    'a[href*="download"]',
    'a[href*="export"]',
    'button[title*="download"]',
    'button[title*="export"]',
    'button[title*="csv"]'
];

const allDownloadElements = [];
downloadSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => allDownloadElements.push(el));
});

console.log(`📊 Found ${allDownloadElements.length} download-related elements:`);

allDownloadElements.forEach((element, index) => {
    const parent = element.closest('button, a, [role="button"]') || element;
    const isVisible = parent.offsetParent !== null;
    const display = window.getComputedStyle(parent).display;
    const visibility = window.getComputedStyle(parent).visibility;
    const opacity = window.getComputedStyle(parent).opacity;
    
    console.log(`\n${index + 1}. Element:`);
    console.log(`   Tag: ${parent.tagName}`);
    console.log(`   Text: "${parent.textContent?.trim()}"`);
    console.log(`   Title: "${parent.title}"`);
    console.log(`   Class: "${parent.className}"`);
    console.log(`   Href: "${parent.href || 'N/A'}"`);
    console.log(`   Visible: ${isVisible}`);
    console.log(`   Display: ${display}`);
    console.log(`   Visibility: ${visibility}`);
    console.log(`   Opacity: ${opacity}`);
    console.log(`   Enabled: ${!parent.disabled}`);
    
    // Check if it's in a play-by-play section
    const section = parent.closest('.section, .tab, .panel, .container, .content, .game, .match');
    if (section) {
        const sectionText = section.textContent?.toLowerCase() || '';
        const isPlayByPlay = sectionText.includes('play') || 
                            sectionText.includes('event') || 
                            sectionText.includes('timeline') ||
                            sectionText.includes('sequence') ||
                            sectionText.includes('game') ||
                            sectionText.includes('match');
        console.log(`   In Play-by-Play Section: ${isPlayByPlay}`);
        console.log(`   Section Text: "${sectionText.substring(0, 100)}..."`);
    }
});

// Look for hidden elements that might become visible
console.log("\n🔍 Looking for hidden elements that might become visible...");

const hiddenElements = document.querySelectorAll('[style*="display: none"], [style*="visibility: hidden"], [style*="opacity: 0"]');
console.log(`📊 Found ${hiddenElements.length} hidden elements`);

hiddenElements.forEach((element, index) => {
    if (element.className.includes('download') || element.className.includes('export') || 
        element.textContent?.toLowerCase().includes('download') ||
        element.textContent?.toLowerCase().includes('export')) {
        console.log(`\n${index + 1}. Hidden Download Element:`);
        console.log(`   Tag: ${element.tagName}`);
        console.log(`   Text: "${element.textContent?.trim()}"`);
        console.log(`   Class: "${element.className}"`);
        console.log(`   Style: "${element.style.cssText}"`);
    }
});

// Look for elements that might be conditionally shown
console.log("\n🔍 Looking for conditionally visible elements...");

const conditionalSelectors = [
    '[class*="show"]',
    '[class*="active"]',
    '[class*="selected"]',
    '[class*="open"]',
    '[class*="expanded"]'
];

conditionalSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
        const downloadElements = element.querySelectorAll('[class*="download"], [class*="export"]');
        if (downloadElements.length > 0) {
            console.log(`\n📁 Found download elements in ${selector} section:`);
            downloadElements.forEach((el, index) => {
                console.log(`   ${index + 1}. ${el.tagName} - "${el.textContent?.trim()}" - ${el.className}`);
            });
        }
    });
});

// Try to make the download link visible and clickable
console.log("\n🧪 Attempting to make download link visible...");

if (downloadLink) {
    // Try different approaches to make it visible
    const approaches = [
        () => {
            downloadLink.style.display = 'block';
            downloadLink.style.visibility = 'visible';
            downloadLink.style.opacity = '1';
        },
        () => {
            downloadLink.style.display = 'inline-block';
            downloadLink.style.visibility = 'visible';
            downloadLink.style.opacity = '1';
        },
        () => {
            downloadLink.removeAttribute('style');
        }
    ];
    
    approaches.forEach((approach, index) => {
        try {
            approach();
            console.log(`   Approach ${index + 1}: Applied`);
            console.log(`   Now visible: ${downloadLink.offsetParent !== null}`);
            console.log(`   Display: ${window.getComputedStyle(downloadLink).display}`);
            
            if (downloadLink.offsetParent !== null) {
                console.log("   ✅ Successfully made visible!");
                console.log("   🖱️  Attempting to click...");
                try {
                    downloadLink.click();
                    console.log("   ✅ Click successful!");
                } catch (error) {
                    console.log("   ❌ Click failed:", error);
                }
            }
        } catch (error) {
            console.log(`   ❌ Approach ${index + 1} failed:`, error);
        }
    });
}

// Look for any JavaScript functions that might control visibility
console.log("\n🔍 Looking for JavaScript functions that might control download visibility...");

// Check for common function names
const functionNames = [
    'showDownload',
    'toggleDownload',
    'enableDownload',
    'activateDownload',
    'openDownload',
    'displayDownload'
];

functionNames.forEach(funcName => {
    if (window[funcName]) {
        console.log(`   Found function: ${funcName}`);
        try {
            window[funcName]();
            console.log(`   ✅ Called ${funcName}() successfully`);
        } catch (error) {
            console.log(`   ❌ Error calling ${funcName}():`, error);
        }
    }
});

// Look for any click handlers on parent elements
console.log("\n🔍 Looking for click handlers on parent elements...");

if (downloadLink) {
    let parent = downloadLink.parentElement;
    let level = 0;
    while (parent && level < 5) {
        if (parent.onclick) {
            console.log(`   Parent ${level + 1} has onclick handler:`, parent.onclick.toString());
        }
        if (parent.addEventListener) {
            console.log(`   Parent ${level + 1} has event listeners`);
        }
        parent = parent.parentElement;
        level++;
    }
}

console.log("\n✅ Enhanced download button analysis complete!");
