# 🏒 Manual Data Extraction Guide for All Three Zones

Since the data is embedded in a Tableau iframe, here are several approaches to extract Sidney Crosby's data:

## **Method 1: Browser Developer Tools**

### **Step 1: Access the Player Data**
1. Go to `https://www.allthreezones.com/player-cards.html`
2. Login with your credentials
3. Navigate to the player card for Sidney Crosby

### **Step 2: Extract Data from Tableau**
1. **Right-click** on the Tableau visualization
2. Select **"Inspect Element"**
3. Look for the **iframe** element containing the Tableau data
4. **Right-click** on the iframe and select **"Inspect Frame"**

### **Step 3: Find the Data**
1. In the iframe's developer tools, look for:
   - **JavaScript variables** containing player data
   - **JSON data** in script tags
   - **Network requests** to Tableau's API
   - **DOM elements** with player statistics

### **Step 4: Copy the Data**
1. Find the data structure containing Crosby's stats
2. **Copy** the JSON or JavaScript object
3. **Save** it to a file for processing

## **Method 2: Network Tab Analysis**

### **Step 1: Open Network Tab**
1. Open **Developer Tools** (F12)
2. Go to the **Network** tab
3. **Refresh** the page

### **Step 2: Find Tableau API Calls**
1. Look for requests to:
   - `tableau.com`
   - `public.tableau.com`
   - Any URLs containing `viz` or `embed`

### **Step 3: Extract API Data**
1. **Click** on the Tableau API requests
2. Go to the **Response** tab
3. **Copy** the JSON/XML response data

## **Method 3: Console Extraction**

### **Step 1: Access Console**
1. Open **Developer Tools** (F12)
2. Go to the **Console** tab

### **Step 2: Execute JavaScript**
```javascript
// Find all iframes
const iframes = document.querySelectorAll('iframe');
console.log('Found iframes:', iframes.length);

// Look for Tableau iframes
const tableauIframes = Array.from(iframes).filter(iframe => 
  iframe.src && iframe.src.includes('tableau')
);
console.log('Tableau iframes:', tableauIframes);

// Access iframe content (if same origin)
if (tableauIframes.length > 0) {
  const iframe = tableauIframes[0];
  try {
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
    console.log('Iframe content:', iframeDoc.body.innerHTML);
  } catch (e) {
    console.log('Cannot access iframe content (cross-origin):', e);
  }
}
```

### **Step 3: Extract Player Data**
```javascript
// Look for player data in the page
const playerElements = document.querySelectorAll('*');
const crosbyElements = Array.from(playerElements).filter(el => 
  el.textContent && el.textContent.toLowerCase().includes('crosby')
);
console.log('Crosby elements:', crosbyElements);

// Extract text content
crosbyElements.forEach((el, i) => {
  console.log(`Element ${i}:`, el.textContent.trim());
});
```

## **Method 4: Selenium Automation**

### **Prerequisites:**
```bash
# Install Selenium
pip install selenium

# Install ChromeDriver
brew install chromedriver  # On macOS
```

### **Run the Selenium Script:**
```bash
python3 selenium_tableau_extractor.py
```

This will:
1. **Open a real browser**
2. **Login** to All Three Zones
3. **Navigate** to the player cards
4. **Find** Tableau iframes
5. **Extract** data from the iframes
6. **Save** the data to files

## **Method 5: API Integration**

Once you have the data structure, we can integrate it with the API:

### **Step 1: Create Data Parser**
```python
def parse_crosby_data(json_data):
    """Parse Crosby's data from extracted JSON"""
    player_data = {
        'name': 'Sidney Crosby',
        'team': 'PIT',
        'position': 'C',
        'stats': {}
    }
    
    # Extract statistics from the JSON data
    # This will depend on the actual data structure
    
    return player_data
```

### **Step 2: Update API Endpoint**
```python
@app.get("/players/{player_name}")
async def get_player(player_name: str):
    """Get specific player data"""
    if player_name.lower() == "sidney crosby":
        # Return the parsed data
        return parse_crosby_data(extracted_data)
    else:
        return {"error": "Player not found"}
```

## **Method 6: Manual Copy-Paste**

### **Step 1: Navigate to Crosby's Card**
1. Go to the player cards page
2. Find Sidney Crosby in the dropdown
3. View his player card

### **Step 2: Copy Statistics**
1. **Manually copy** each statistic:
   - Shots/60: 0.81
   - Shot Assists/60: 0.53
   - Total Shot Contributions/60: 1.08
   - etc.

### **Step 3: Create JSON Structure**
```json
{
  "name": "Sidney Crosby",
  "team": "PIT",
  "position": "C",
  "year": "2024-25",
  "stats": {
    "general_offense": {
      "shots_per_60": 0.81,
      "shot_assists_per_60": 0.53,
      "total_shot_contributions_per_60": 1.08
    },
    "passing": {
      "high_danger_assists_per_60": 1.54
    },
    "offense_types": {
      "cycle_forecheck_offense_per_60": 1.03,
      "rush_offense_per_60": 0.46
    }
  }
}
```

## **🎯 Recommended Approach**

For your use case, I recommend:

1. **Start with Method 4 (Selenium)** - It's the most automated
2. **Use Method 1 (Developer Tools)** - To understand the data structure
3. **Combine with Method 5 (API Integration)** - To make it accessible via API

This will give you the best of both worlds: automated extraction and API access for searching Sidney Crosby's data! 🏒 