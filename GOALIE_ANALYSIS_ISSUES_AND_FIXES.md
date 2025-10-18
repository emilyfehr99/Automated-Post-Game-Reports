# Goalie Analysis Issues and Fixes

## Main Issues Identified

### 1. **Wrong Action Column for Shots**
- **Problem**: Your R code was looking for `action == "Shots"` but the dataset uses `action == "Shots against"`
- **Impact**: This caused zeros in all shot-related metrics
- **Fix**: Changed all references from `"Shots"` to `"Shots against"`

### 2. **Missing Action Types**
- **Problem**: The dataset doesn't contain:
  - `"Power play shots"`
  - `"Short-handed shots"` 
  - `"Passes to the slot"`
- **Impact**: These metrics will return empty results (not zeros, but no data)
- **Fix**: Added warnings and handled missing data gracefully

### 3. **Duration Issues**
- **Problem**: All entries have duration = 12 (constant)
- **Impact**: GAA and shot rate calculations may be misleading
- **Fix**: Added warnings about constant duration

### 4. **Coordinate Analysis**
- **Problem**: No shots found in slot area (|pos_x| < 30, |pos_y| < 15)
- **Impact**: High-danger shot metrics return zero
- **Fix**: Adjusted slot definition or noted data limitations

## Data Structure Analysis

### Goalies Found:
- **Gaulton Andrew** (Bonnyville Pontiacs)
- **Madgett Sam** (Lloydminster Bobcats) 
- **Kirkwood Kannen** (Lloydminster Bobcats)
- **Mainberger Kasen** (Bonnyville Pontiacs)

### Action Frequencies:
- Shots against: 70
- Saves: 63
- Goals against: 7
- Passes: 17
- Accurate passes: 13

### Key Findings:
- **Total saves**: 63
- **Total goals against**: 7
- **Overall save percentage**: 90.15%
- **Best performer**: Kirkwood Kannen (95.24% save percentage)

## Corrected R Code

The main changes in `goalie_analysis_corrected.R`:

1. **Changed all `action == "Shots"` to `action == "Shots against"`**
2. **Added proper error handling for missing action types**
3. **Updated shot location analysis to use correct action**
4. **Added warnings for data limitations**
5. **Improved debugging output**

## Python Alternative

I also created `goalie_analysis_fixed.py` which:
- Identifies the same issues
- Provides corrected analysis
- Creates visualizations
- Generates a comprehensive report

## Recommendations

1. **Use the corrected R script** for your analysis
2. **Verify the action labels** in your data collection system
3. **Consider adding missing action types** if needed for complete analysis
4. **Review duration calculation** - constant duration suggests time units may need adjustment
5. **Check coordinate system** - no shots in slot area may indicate coordinate scaling issues

## Files Created

- `goalie_analysis_corrected.R` - Fixed R script
- `goalie_analysis_fixed.py` - Python analysis with visualizations
- `goalie_analysis_debug.py` - Debug script to identify issues
- `goalie_analysis_results.png` - Visualization output

The corrected R script should now provide meaningful results instead of zeros!
