#!/usr/bin/env python3
"""
Lloydminster Bobcats Data Collector
Collects player data for just the Bobcats team
"""

import sqlite3
import json
import logging
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from hudl_complete_metrics_scraper import HudlCompleteMetricsScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_bobcats_data():
    """Collect Lloydminster Bobcats player data"""
    try:
        logger.info("🏒 Collecting Lloydminster Bobcats data...")
        
        # Initialize scraper
        scraper = HudlCompleteMetricsScraper()
        scraper.setup_driver()
        
        # Authenticate
        username = "chaserochon777@gmail.com"
        password = "357Chaser!468"
        
        if not scraper.login(username, password):
            logger.error("❌ Authentication failed")
            return False
        
        logger.info("✅ Authentication successful")
        
        # Connect to database
        conn = sqlite3.connect('ajhl_comprehensive.db')
        cursor = conn.cursor()
        
        # Clear old Bobcats data
        cursor.execute("DELETE FROM players WHERE team_id = '21479'")
        cursor.execute("DELETE FROM teams WHERE team_id = '21479'")
        conn.commit()
        
        # Insert Bobcats team data
        cursor.execute("""
            INSERT INTO teams (team_id, team_name, city, province, hudl_team_id, is_active, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "21479",
            "Lloydminster Bobcats",
            "Lloydminster",
            "AB",
            "21479",
            True,
            datetime.now().isoformat()
        ))
        
        # Get players for Bobcats using the working method
        players = scraper.get_team_players("21479")
        
        # If we got players, try to get ALL 135+ metrics
        if players:
            logger.info("📜 COMPREHENSIVE APPROACH: Attempting to get ALL 135+ metrics...")
            
            # PHASE 1: Look for filter buttons or view options
            logger.info("🔍 PHASE 1: Looking for filter/view options...")
            try:
                # Look for filter buttons
                filter_selectors = [
                    "button[class*='filter']", "button[class*='Filter']", "[class*='filter']", "[class*='Filter']",
                    "button[class*='view']", "button[class*='View']", "[class*='view']", "[class*='View']",
                    "button[class*='option']", "button[class*='Option']", "[class*='option']", "[class*='Option']",
                    "button[class*='setting']", "button[class*='Setting']", "[class*='setting']", "[class*='Setting']",
                    "button[class*='advanced']", "button[class*='Advanced']", "[class*='advanced']", "[class*='Advanced']",
                    "button[class*='comprehensive']", "button[class*='Comprehensive']", "[class*='comprehensive']", "[class*='Comprehensive']",
                    "button[class*='all']", "button[class*='All']", "[class*='all']", "[class*='All']",
                    "button[class*='more']", "button[class*='More']", "[class*='more']", "[class*='More']",
                    "button[class*='metric']", "button[class*='Metric']", "[class*='metric']", "[class*='Metric']",
                    "button[class*='stat']", "button[class*='Stat']", "[class*='stat']", "[class*='Stat']"
                ]
                
                for selector in filter_selectors:
                    try:
                        elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            logger.info(f"📊 Found {len(elements)} elements with selector: {selector}")
                            for i, element in enumerate(elements):
                                try:
                                    element_text = element.text.strip()
                                    if element_text and len(element_text) > 0:
                                        logger.info(f"  Element {i+1}: '{element_text}'")
                                        # Click on elements that might show more metrics
                                        if any(word in element_text.lower() for word in ['all', 'more', 'advanced', 'comprehensive', 'full', 'detailed', 'metric', 'stat', 'filter', 'view', 'option']):
                                            logger.info(f"📊 Clicking promising element: '{element_text}'")
                                            element.click()
                                            time.sleep(2)
                                            break
                                except Exception as e:
                                    logger.debug(f"Error with element {i+1}: {e}")
                    except Exception as e:
                        logger.debug(f"Error with selector {selector}: {e}")
                
                # Look for tabs that might contain more metrics
                tab_selectors = [
                    "[role='tab']", "[class*='tab']", "[class*='Tab']",
                    "li[class*='tab']", "li[class*='Tab']",
                    "a[class*='tab']", "a[class*='Tab']"
                ]
                
                for selector in tab_selectors:
                    try:
                        tabs = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                        if tabs:
                            logger.info(f"📊 Found {len(tabs)} tabs with selector: {selector}")
                            for i, tab in enumerate(tabs):
                                try:
                                    tab_text = tab.text.strip()
                                    if tab_text and len(tab_text) > 0:
                                        logger.info(f"  Tab {i+1}: '{tab_text}'")
                                        # Click on tabs that might show more metrics
                                        if any(word in tab_text.lower() for word in ['advanced', 'detailed', 'comprehensive', 'all', 'more', 'metric', 'stat', 'full']):
                                            logger.info(f"📊 Clicking promising tab: '{tab_text}'")
                                            tab.click()
                                            time.sleep(2)
                                            break
                                except Exception as e:
                                    logger.debug(f"Error with tab {i+1}: {e}")
                    except Exception as e:
                        logger.debug(f"Error with tab selector {selector}: {e}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Filter/view interaction failed: {e}")
            
            # PHASE 2: Look for Box Score modal with Select All functionality
            logger.info("🔍 PHASE 2: Looking for Box Score modal with Select All functionality...")
            try:
                # Look for Box Score modal specifically
                box_score_selectors = [
                    "h2[class*='Title']",  # Look for "Box score" title
                    "[class*='Popup__PopupOverlay']",  # Modal overlay
                    "[class*='Checkboxes__Checkbox']",  # Select all checkbox
                    "span[data-lexic='4239']",  # "Select all" text
                    "h2:contains('Box score')",  # Box score title
                    "span:contains('Select all')",  # Select all text
                    "span:contains('Choose parameters')"  # Choose parameters text
                ]
                
                box_score_found = False
                for selector in box_score_selectors:
                    try:
                        elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            logger.info(f"📊 Found {len(elements)} Box Score elements with selector: {selector}")
                            for i, element in enumerate(elements):
                                try:
                                    element_text = element.text.strip()
                                    element_title = element.get_attribute('title') or ''
                                    logger.info(f"  Box Score {i+1}: text='{element_text}', title='{element_title}'")
                                    
                                    if any(word in (element_text + element_title).lower() for word in ['box score', 'select all', 'choose parameters']):
                                        logger.info(f"📊 Found Box Score modal element: '{element_text or element_title}'")
                                        box_score_found = True
                                        break
                                except Exception as e:
                                    logger.debug(f"Error with Box Score element {i+1}: {e}")
                            if box_score_found:
                                break
                    except Exception as e:
                        logger.debug(f"Error with Box Score selector {selector}: {e}")
                
                if not box_score_found:
                    # Try to find and click a button that opens the Box Score modal
                    logger.info("🔍 Looking for button to open Box Score modal...")
                    modal_trigger_selectors = [
                        "button:contains('Box score')", "button:contains('BOX SCORE')", "button:contains('Box Score')",
                        "a:contains('Box score')", "a:contains('BOX SCORE')", "a:contains('Box Score')",
                        "span:contains('Box score')", "span:contains('BOX SCORE')", "span:contains('Box Score')",
                        "div:contains('Box score')", "div:contains('BOX SCORE')", "div:contains('Box Score')",
                        "button[class*='export']", "button[class*='Export']", "[class*='export']", "[class*='Export']",
                        "button[class*='download']", "button[class*='Download']", "[class*='download']", "[class*='Download']",
                        "button[class*='box']", "button[class*='Box']", "[class*='box']", "[class*='Box']",
                        "button[class*='score']", "button[class*='Score']", "[class*='score']", "[class*='Score']",
                        "button[class*='parameter']", "button[class*='Parameter']", "[class*='parameter']", "[class*='Parameter']",
                        "button[class*='setting']", "button[class*='Setting']", "[class*='setting']", "[class*='Setting']",
                        "button[class*='option']", "button[class*='Option']", "[class*='option']", "[class*='Option']"
                    ]
                    
                    for selector in modal_trigger_selectors:
                        try:
                            buttons = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                            if buttons:
                                logger.info(f"📊 Found {len(buttons)} modal trigger elements with selector: {selector}")
                                for i, button in enumerate(buttons):
                                    try:
                                        button_text = button.text.strip()
                                        button_title = button.get_attribute('title') or ''
                                        button_aria = button.get_attribute('aria-label') or ''
                                        logger.info(f"  Modal Trigger {i+1}: text='{button_text}', title='{button_title}', aria='{button_aria}'")
                                        
                                        if any(word in (button_text + button_title + button_aria).lower() for word in ['export', 'download', 'box', 'score', 'parameter', 'setting', 'option', 'csv', 'excel', 'data']):
                                            logger.info(f"📊 Clicking modal trigger button: '{button_text or button_title or button_aria}'")
                                            button.click()
                                            time.sleep(3)
                                            
                                            # Check if Box Score modal appeared
                                            box_score_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "h2:contains('Box score'), span:contains('Select all'), [class*='Popup__PopupOverlay']")
                                            if box_score_elements:
                                                logger.info("✅ Box Score modal opened!")
                                                box_score_found = True
                                                break
                                    except Exception as e:
                                        logger.debug(f"Error with modal trigger button {i+1}: {e}")
                                if box_score_found:
                                    break
                        except Exception as e:
                            logger.debug(f"Error with modal trigger selector {selector}: {e}")
                    
                    # Also try XPath selectors for Box Score
                    if not box_score_found:
                        logger.info("🔍 Trying XPath selectors for Box Score...")
                        xpath_selectors = [
                            "//button[contains(text(), 'Box score')]",
                            "//button[contains(text(), 'BOX SCORE')]",
                            "//button[contains(text(), 'Box Score')]",
                            "//a[contains(text(), 'Box score')]",
                            "//a[contains(text(), 'BOX SCORE')]",
                            "//a[contains(text(), 'Box Score')]",
                            "//span[contains(text(), 'Box score')]",
                            "//span[contains(text(), 'BOX SCORE')]",
                            "//span[contains(text(), 'Box Score')]",
                            "//div[contains(text(), 'Box score')]",
                            "//div[contains(text(), 'BOX SCORE')]",
                            "//div[contains(text(), 'Box Score')]"
                        ]
                        
                        for xpath in xpath_selectors:
                            try:
                                elements = scraper.driver.find_elements(By.XPATH, xpath)
                                if elements:
                                    logger.info(f"📊 Found {len(elements)} Box Score elements with XPath: {xpath}")
                                    for i, element in enumerate(elements):
                                        try:
                                            element_text = element.text.strip()
                                            logger.info(f"  XPath Element {i+1}: text='{element_text}'")
                                            
                                            if 'box score' in element_text.lower():
                                                logger.info(f"📊 Clicking Box Score element: '{element_text}'")
                                                element.click()
                                                time.sleep(3)
                                                
                                                # Check if Box Score modal appeared
                                                box_score_elements = scraper.driver.find_elements(By.CSS_SELECTOR, "h2:contains('Box score'), span:contains('Select all'), [class*='Popup__PopupOverlay']")
                                                if box_score_elements:
                                                    logger.info("✅ Box Score modal opened!")
                                                    box_score_found = True
                                                    break
                                        except Exception as e:
                                            logger.debug(f"Error with XPath element {i+1}: {e}")
                                    if box_score_found:
                                        break
                            except Exception as e:
                                logger.debug(f"Error with XPath selector {xpath}: {e}")
                
                if box_score_found:
                    logger.info("🎉 Box Score modal found! Attempting to select all metrics...")
                    
                    # Wait for modal to fully load
                    time.sleep(2)
                    
                    # Look for "Select all" checkbox
                    select_all_selectors = [
                        "span[data-lexic='4239']",  # "Select all" text
                        "span:contains('Select all')",  # Select all text
                        "[class*='Checkboxes__Checkbox']",  # Checkbox class
                        "input[type='checkbox']",  # Checkbox input
                        "[role='checkbox']"  # Checkbox role
                    ]
                    
                    select_all_clicked = False
                    for selector in select_all_selectors:
                        try:
                            select_all_elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                            if select_all_elements:
                                logger.info(f"📊 Found {len(select_all_elements)} Select All elements with selector: {selector}")
                                for i, element in enumerate(select_all_elements):
                                    try:
                                        element_text = element.text.strip()
                                        logger.info(f"  Select All {i+1}: text='{element_text}'")
                                        
                                        if 'select all' in element_text.lower() or selector == "span[data-lexic='4239']":
                                            logger.info(f"📊 Clicking Select All: '{element_text}'")
                                            element.click()
                                            time.sleep(1)
                                            select_all_clicked = True
                                            break
                                    except Exception as e:
                                        logger.debug(f"Error with Select All element {i+1}: {e}")
                                if select_all_clicked:
                                    break
                        except Exception as e:
                            logger.debug(f"Error with Select All selector {selector}: {e}")
                    
                    if select_all_clicked:
                        logger.info("✅ Select All clicked! Looking for Apply/OK button...")
                        
                        # Look for Apply/OK button
                        apply_selectors = [
                            "button[class*='apply']", "button[class*='Apply']", "[class*='apply']", "[class*='Apply']",
                            "button[class*='ok']", "button[class*='OK']", "[class*='ok']", "[class*='OK']",
                            "button[class*='submit']", "button[class*='Submit']", "[class*='submit']", "[class*='Submit']",
                            "button[class*='confirm']", "button[class*='Confirm']", "[class*='confirm']", "[class*='Confirm']",
                            "button[class*='close']", "button[class*='Close']", "[class*='close']", "[class*='Close']",
                            "button[type='submit']", "input[type='submit']", "button[class*='btn']", "button[class*='Btn']"
                        ]
                        
                        apply_clicked = False
                        for selector in apply_selectors:
                            try:
                                apply_buttons = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                                if apply_buttons:
                                    logger.info(f"📊 Found {len(apply_buttons)} Apply buttons with selector: {selector}")
                                    for i, button in enumerate(apply_buttons):
                                        try:
                                            button_text = button.text.strip()
                                            button_title = button.get_attribute('title') or ''
                                            logger.info(f"  Apply {i+1}: text='{button_text}', title='{button_title}'")
                                            
                                            if any(word in (button_text + button_title).lower() for word in ['apply', 'ok', 'submit', 'confirm', 'close', 'done', 'finish']):
                                                logger.info(f"📊 Clicking Apply button: '{button_text or button_title}'")
                                                button.click()
                                                time.sleep(2)
                                                apply_clicked = True
                                                break
                                        except Exception as e:
                                            logger.debug(f"Error with Apply button {i+1}: {e}")
                                    if apply_clicked:
                                        break
                            except Exception as e:
                                logger.debug(f"Error with Apply selector {selector}: {e}")
                        
                        if apply_clicked:
                            logger.info("✅ Apply button clicked! Modal should be closed and all metrics selected.")
                        else:
                            logger.warning("⚠️ Apply button not found, trying to close modal...")
                            # Try to close modal with escape key or close button
                            try:
                                scraper.driver.find_element(By.CSS_SELECTOR, "button[class*='PopupCloseButton'], button[class*='close']").click()
                                time.sleep(1)
                            except:
                                scraper.driver.execute_script("document.body.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));")
                                time.sleep(1)
                    else:
                        logger.warning("⚠️ Select All checkbox not found")
                else:
                    logger.warning("⚠️ Box Score modal not found")
                    
            except Exception as e:
                logger.warning(f"⚠️ Box Score modal interaction failed: {e}")
            
            # PHASE 3: Comprehensive horizontal scrolling
            logger.info("🔍 PHASE 3: Comprehensive horizontal scrolling...")
            scroll_table_horizontally(scraper.driver)
            
            # PHASE 4: Extract ALL metrics after scrolling
            logger.info("🔍 PHASE 4: Extracting ALL metrics after scrolling...")
            all_metrics = extract_all_metrics_after_scrolling(scraper.driver)
            if all_metrics:
                logger.info(f"🎉 Found {len(all_metrics)} total metrics after scrolling!")
                for i, metric in enumerate(sorted(all_metrics), 1):
                    logger.info(f"  {i:3d}. {metric}")
            
            # PHASE 5: Try to extract more data after scrolling
            logger.info("🔍 PHASE 5: Extracting updated player data...")
            result = scraper.extract_structured_data()
            if result and 'players' in result:
                players = result['players']
                logger.info(f"✅ Found additional data! Now have {len(players)} players with {result['total_metrics']} metrics each")
        
        if players:
            logger.info(f"✅ Found {len(players)} players")
            
            # Insert player data
            for player in players:
                cursor.execute("""
                    INSERT INTO players (player_id, team_id, name, position, metrics, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    f"{player.get('name', '').lower().replace(' ', '_')}_21479",
                    "21479",
                    player.get('name', ''),
                    player.get('position', ''),
                    json.dumps(player),  # Store as JSON
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            logger.info(f"🎉 Bobcats data collection complete!")
            logger.info(f"📊 Players: {len(players)}")
            
            # Show sample players
            logger.info("📋 Sample players:")
            for i, player in enumerate(players[:5]):
                logger.info(f"   {i+1}. {player.get('name', 'Unknown')} (#{player.get('jersey_number', 'N/A')}) - {player.get('position', 'Unknown')}")
            
            if len(players) > 5:
                logger.info(f"   ... and {len(players) - 5} more players")
        
        else:
            logger.warning("⚠️ No players found for Lloydminster Bobcats")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        return False
    finally:
        if 'scraper' in locals() and scraper.driver:
            scraper.driver.quit()

def extract_metrics_at_scroll_position(driver, element):
    """Extract only actual metric names from table headers, not player data"""
    try:
        metrics_at_position = set()
        
        # Get only column headers from the table - these contain the actual metric names
        column_headers = element.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
        for header in column_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                # Filter out player names and values - only keep metric names
                if is_valid_metric_name(text):
                    metrics_at_position.add(text)
                    logger.debug(f"📊 Found metric name: '{text}'")
        
        # Get table headers (th elements) - these are the actual column headers
        table_headers = element.find_elements(By.CSS_SELECTOR, "th")
        for header in table_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    metrics_at_position.add(text)
                    logger.debug(f"📊 Found table header: '{text}'")
        
        # Look for span elements that are specifically in header cells
        header_spans = element.find_elements(By.CSS_SELECTOR, "th span, [role='columnheader'] span")
        for span in header_spans:
            text = span.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    metrics_at_position.add(text)
                    logger.debug(f"📊 Found header span: '{text}'")
        
        logger.info(f"📊 Found {len(metrics_at_position)} metric names at this position")
        return metrics_at_position
        
    except Exception as e:
        logger.error(f"❌ Error extracting metrics at scroll position: {e}")
        return set()

def is_valid_metric_name(text):
    """Check if text is a valid metric name, not player data"""
    # Comprehensive list of valid metric names from your list
    valid_metrics = {
        # Basic stats
        'PLAYER', 'Position', 'POS', 'Time on ice', 'TOI', 'Games played', 'GP', 'All shifts', 'SHIFTS',
        'Goals', 'G', 'First assist', 'A1', 'Second assist', 'A2', 'Assists', 'A', 'Points', 'P',
        '+/-', '+ / -', 'Scoring chances', 'SC', 'Penalties drawn', 'PEA', 'Penalty time', 'PEN',
        
        # Faceoffs
        'Faceoffs', 'FO', 'Faceoffs won', 'FO+', 'Faceoffs won, %', 'FO%',
        'Faceoffs in DZ', 'FOD', 'Faceoffs won in DZ', 'FOD+', 'Faceoffs won in DZ, %', 'FOD%',
        'Faceoffs in NZ', 'FON', 'Faceoffs won in NZ', 'FON+', 'Faceoffs won in NZ, %', 'FON%',
        'Faceoffs in OZ', 'FOA', 'Faceoffs won in OZ', 'FOA+', 'Faceoffs won in OZ, %', 'FOA%',
        
        # Shots and scoring
        'Hits', 'H+', 'Shots', 'S', 'Shots on goal', 'S+', 'Blocked shots', 'SBL',
        'Power play shots', 'SPP', 'Short-handed shots', 'SSH', 'Passes to the slot', 'PTTS',
        'Missed shots', 'S-', '% shots on goal', 'SOG%', 'Slapshot', 'SSL', 'Wrist shot', 'SWR',
        
        # Advanced stats
        'Puck touches', 'TC', 'Puck control time', 'PCT', 'Plus', '+', 'Minus', '-',
        'Penalties', 'PE', 'Faceoffs lost', 'FO-', 'Hits against', 'H-', 'Error leading to goal', 'SGM',
        'Dump ins', 'DI', 'Dump outs', 'DO', 'Team goals when on ice', 'TGI', "Opponent's goals when on ice", 'OGI',
        
        # Power play and penalty kill
        'Power play', 'PP', 'Successful power play', 'PP+', 'Power play time', 'PPT',
        'Short-handed', 'SH', 'Penalty killing', 'SH+', 'Short-handed time', 'SHT',
        
        # Shootouts and 1-on-1
        'Shootouts', 'SHO', 'Shootouts scored', 'SHO+', 'Shootouts missed', 'SHO-',
        '1-on-1 shots', 'S1on1', '1-on-1 goals', 'G1on1', 'Shots conversion 1 on 1, %', 'SC1v1%',
        
        # Shot types and positioning
        'Positional attack shots', 'SPA', 'Shots 5 v 5', 'S5v5', 'Counter-attack shots', 'SCA',
        'xG per shot', 'xGPS', 'xG (Expected goals)', 'xG', 'xG per goal', 'xGPG',
        'Net xG (xG player on - opp. team\'s xG)', 'NxG', 'Team xG when on ice', 'xGT',
        "Opponent's xG when on ice", 'xGOPP', 'xG conversion', 'xGC',
        
        # CORSI and Fenwick
        'CORSI', 'CORSI-', 'CORSI+', 'CORSI for, %', 'CORSI%',
        'Fenwick for', 'FF', 'Fenwick against', 'FA', 'Fenwick for, %', 'FF%',
        
        # Zone play
        'Playing in attack', 'PIA', 'Playing in defense', 'PID',
        'OZ possession', 'POZ', 'NZ possession', 'PNZ', 'DZ possession', 'PDZ',
        
        # Puck battles
        'Puck battles', 'C', 'Puck battles won', 'C+', 'Puck battles won, %', 'C%',
        'Puck battles in DZ', 'CD', 'Puck battles in NZ', 'CNZ', 'Puck battles in OZ', 'CO',
        
        # Defensive play
        'Shots blocking', 'BL', 'Dekes', 'DKS', 'Dekes successful', 'DKS+',
        'Dekes unsuccessful', 'DKS-', 'Dekes successful, %', 'DKS%',
        
        # Passing
        'Passes', 'P', 'Accurate passes', 'P+', 'Accurate passes, %', 'P%',
        'Pre-shots passes', 'PSP', 'Pass receptions', 'PRP',
        
        # Scoring chances
        'Scoring chances - total', 'SC', 'Scoring chances - scored', 'SC+',
        'Scoring chances missed', 'SC-', 'Scoring chances saved', 'SC OG', 'Scoring Chances, %', 'SC%',
        
        # Slot shots
        'Inner slot shots - total', 'SCIS', 'Inner slot shots - scored', 'SCIS+',
        'Inner slot shots - missed', 'SCIS-', 'Inner slot shots - saved', 'SCISOG', 'Inner slot shots, %', 'SCIS%',
        'Outer slot shots - total', 'SCOS', 'Outer slot shots - scored', 'SCOS+',
        'Outer slot shots - missed', 'SCOS-', 'Outer slot shots - saved', 'SCOSOG', 'Outer slot shots, %', 'SCOS%',
        'Blocked shots from the slot', 'SBLIS', 'Blocked shots outside of the slot', 'SBLOS',
        
        # Takeaways and retrievals
        'Takeaways', 'TA', 'Puck retrievals after shots', 'PRS', "Opponent's dump-in retrievals", 'ODIR',
        'Takeaways in DZ', 'TAO', 'Loose puck recovery', 'LPR', 'Takeaways in NZ', 'TAC',
        'Takeaways in OZ', 'TAA', 'EV DZ retrievals', 'DZRT',
        
        # Puck losses
        'Puck losses', 'GA', 'Puck losses in DZ', 'GAO', 'EV OZ retrievals', 'OZRT',
        'Puck losses in NZ', 'GAC', 'Power play retrievals', 'PPRT', 'Penalty kill retrievals', 'PKRT',
        'Puck losses in OZ', 'GAA',
        
        # Entries and breakouts
        'Entries', 'EN', 'Entries via pass', 'ENP', 'Entries via dump in', 'END',
        'Entries via stickhandling', 'ENS', 'Breakouts', 'BR', 'Breakouts via pass', 'BRP',
        'Breakouts via dump out', 'BRD', 'Breakouts via stickhandling', 'BRS'
    }
    
    # Check if it's a known metric
    if text in valid_metrics:
        return True
    
    # Check if it looks like a metric (short codes, percentages, etc.)
    if (len(text) <= 5 and 
        (text.endswith('%') or text.endswith('+') or text.endswith('-') or 
         text.isupper() or text.replace('+', '').replace('-', '').replace('%', '').isalpha())):
        return True
    
    # Check if it's a percentage
    if text.endswith('%') and len(text) <= 10:
        return True
    
    # Check if it's a time format (MM:SS)
    if ':' in text and len(text) <= 6:
        return True
    
    # Check if it's a decimal number (likely a stat value)
    try:
        float(text)
        return False  # Numbers are not metric names
    except ValueError:
        pass
    
    # Check if it's a player name (contains common name patterns)
    if (len(text) > 5 and 
        any(char.islower() for char in text) and 
        not text.endswith('%') and not text.endswith('+') and not text.endswith('-') and
        not text.isupper() and not any(word in text.lower() for word in ['shots', 'goals', 'passes', 'faceoffs', 'hits', 'penalties', 'scoring', 'puck', 'zone', 'power', 'short', 'shootout', 'corsi', 'fenwick', 'battles', 'dekes', 'blocked', 'takeaways', 'retrievals', 'losses', 'entries', 'breakouts'])):
        return False  # Likely a player name
    
    return False

def extract_all_metrics_after_scrolling(driver):
    """Extract ALL metric names from the entire DOM, not just visible ones"""
    try:
        logger.info("📊 Extracting ALL metric names from entire DOM...")
        
        all_metrics = set()
        
        # Get ALL column headers from the entire DOM
        column_headers = driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
        logger.info(f"📊 Found {len(column_headers)} column headers in DOM")
        for header in column_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    all_metrics.add(text)
                    logger.debug(f"📊 Found column header: '{text}'")
        
        # Get ALL table headers (th elements) from the entire DOM
        table_headers = driver.find_elements(By.CSS_SELECTOR, "th")
        logger.info(f"📊 Found {len(table_headers)} table headers in DOM")
        for header in table_headers:
            text = header.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    all_metrics.add(text)
                    logger.debug(f"📊 Found table header: '{text}'")
        
        # Look for ALL span elements that might contain metric names
        all_spans = driver.find_elements(By.CSS_SELECTOR, "span")
        logger.info(f"📊 Found {len(all_spans)} span elements in DOM")
        for span in all_spans:
            text = span.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    all_metrics.add(text)
                    logger.debug(f"📊 Found span: '{text}'")
        
        # Look for ALL div elements that might contain metric names
        all_divs = driver.find_elements(By.CSS_SELECTOR, "div")
        logger.info(f"📊 Found {len(all_divs)} div elements in DOM")
        for div in all_divs:
            text = div.text.strip()
            if text and len(text) > 1 and text not in ['', 'PLAYER', 'POS', 'TOI']:
                if is_valid_metric_name(text):
                    all_metrics.add(text)
                    logger.debug(f"📊 Found div: '{text}'")
        
        # Look for data attributes that might contain metric names
        data_elements = driver.find_elements(By.CSS_SELECTOR, "[data-lexic], [data-metric], [data-field], [data-column]")
        logger.info(f"📊 Found {len(data_elements)} data elements in DOM")
        for element in data_elements:
            for attr in ['data-lexic', 'data-metric', 'data-field', 'data-column']:
                value = element.get_attribute(attr)
                if value and is_valid_metric_name(value):
                    all_metrics.add(value)
                    logger.debug(f"📊 Found data attribute {attr}: '{value}'")
        
        # Look for aria-label attributes
        aria_elements = driver.find_elements(By.CSS_SELECTOR, "[aria-label]")
        logger.info(f"📊 Found {len(aria_elements)} aria-label elements in DOM")
        for element in aria_elements:
            text = element.get_attribute('aria-label')
            if text and is_valid_metric_name(text):
                all_metrics.add(text)
                logger.debug(f"📊 Found aria-label: '{text}'")
        
        # Look for title attributes
        title_elements = driver.find_elements(By.CSS_SELECTOR, "[title]")
        logger.info(f"📊 Found {len(title_elements)} title elements in DOM")
        for element in title_elements:
            text = element.get_attribute('title')
            if text and is_valid_metric_name(text):
                all_metrics.add(text)
                logger.debug(f"📊 Found title: '{text}'")
        
        logger.info(f"📊 Total unique metric names found: {len(all_metrics)}")
        return sorted(list(all_metrics))
        
    except Exception as e:
        logger.error(f"❌ Error extracting all metrics: {e}")
        return None

def scroll_table_horizontally(driver):
    """Enhanced scroll using specific scroll attributes from jsviewer.js.txt analysis"""
    try:
        logger.info("📜 Enhanced scrolling using TableScrollWrapper and scroll state management...")
        
        # Method 1: Find TableScrollWrapper components
        wrapper_selectors = [
            "div[class*='TableScrollWrapper']",
            "div[class*='Table__TableScrollWrapper']", 
            "div[class*='TableContainers__TableScrollWrapper']",
            "div[class*='table-scroll']",
            "div[class*='scroll-wrapper']"
        ]
        
        wrappers_found = []
        for selector in wrapper_selectors:
            try:
                wrappers = driver.find_elements(By.CSS_SELECTOR, selector)
                if wrappers:
                    logger.info(f"✅ Found {len(wrappers)} TableScrollWrapper(s) with selector: {selector}")
                    wrappers_found.extend(wrappers)
            except Exception as e:
                logger.debug(f"Selector {selector} failed: {e}")
                continue
        
        # Method 2: Find tables with columnheader elements
        tables_with_headers = driver.find_elements(By.CSS_SELECTOR, 
            "table, div[role='table'], div[class*='table']")
        
        logger.info(f"📊 Found {len(tables_with_headers)} potential tables")
        
        # Process all found elements
        all_elements = wrappers_found + tables_with_headers
        
        # Collect all metrics from all scroll methods
        all_metrics_from_scrolling = set()
        
        for i, element in enumerate(all_elements):
            try:
                logger.info(f"📊 Processing element {i+1}/{len(all_elements)}")
                
                # Get scroll state
                scroll_state = driver.execute_script("""
                    return {
                        scrollLeft: arguments[0].scrollLeft,
                        scrollTop: arguments[0].scrollTop,
                        scrollWidth: arguments[0].scrollWidth,
                        scrollHeight: arguments[0].scrollHeight,
                        clientWidth: arguments[0].clientWidth,
                        clientHeight: arguments[0].clientHeight,
                        hasHorizontalScroll: arguments[0].scrollWidth > arguments[0].clientWidth,
                        hasVerticalScroll: arguments[0].scrollHeight > arguments[0].clientHeight
                    };
                """, element)
                
                logger.info(f"📊 Scroll State: {scroll_state}")
                
                if scroll_state and scroll_state['hasHorizontalScroll']:
                    logger.info(f"✅ Element {i+1} has horizontal scroll!")
                    
                    # Method A: State management scroll (with data extraction)
                    logger.info("🔄 Trying state management scroll with data extraction...")
                    metrics_from_state = scroll_with_state_management(driver, element, scroll_state)
                    if metrics_from_state:
                        all_metrics_from_scrolling.update(metrics_from_state)
                        logger.info(f"📊 State scroll found {len(metrics_from_state)} metrics")
                    
                    # Method B: Debounced scroll
                    logger.info("🔄 Trying debounced scroll...")
                    scroll_with_debouncing(driver, element, scroll_state)
                    
                    # Method C: Animation scroll
                    logger.info("🔄 Trying animation scroll...")
                    scroll_with_animation(driver, element, scroll_state)
                    
                    # Method D: Resize triggers scroll
                    logger.info("🔄 Trying resize triggers scroll...")
                    scroll_with_resize_triggers(driver, element, scroll_state)
                    
                else:
                    logger.info(f"⚠️ Element {i+1} has no horizontal scroll")
                    
            except Exception as e:
                logger.error(f"❌ Error processing element {i+1}: {e}")
                continue
        
        # Log all metrics found during scrolling
        if all_metrics_from_scrolling:
            logger.info(f"🎉 COMPREHENSIVE METRICS FOUND DURING SCROLLING: {len(all_metrics_from_scrolling)}")
            logger.info("=" * 80)
            for i, metric in enumerate(sorted(all_metrics_from_scrolling), 1):
                logger.info(f"  {i:3d}. {metric}")
            logger.info("=" * 80)
        
        logger.info("✅ Enhanced horizontal scrolling complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced horizontal scrolling: {e}")

def scroll_with_state_management(driver, element, scroll_state):
    """Comprehensive scrolling through entire table width to find ALL metrics"""
    try:
        scroll_width = scroll_state['scrollWidth']
        client_width = scroll_state['clientWidth']
        max_scroll = scroll_width - client_width
        
        logger.info(f"📊 COMPREHENSIVE SCROLL: max={max_scroll}, client_width={client_width}")
        
        # Use very small steps to ensure we don't miss any columns
        step_size = 25  # Even smaller steps for maximum coverage
        current_offset = 0
        
        # Collect all metrics during scrolling
        all_metrics_during_scroll = set()
        
        # Phase 1: Forward scroll with comprehensive coverage
        logger.info("🔄 PHASE 1: Forward comprehensive scroll...")
        while current_offset < max_scroll:
            # Set scroll position
            driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, current_offset)
            time.sleep(0.2)  # Wait for content to load
            
            logger.info(f"📜 Scroll to {current_offset}/{max_scroll} ({(current_offset/max_scroll)*100:.1f}%)")
            
            # Extract metrics at this scroll position
            metrics_at_position = extract_metrics_at_scroll_position(driver, element)
            if metrics_at_position:
                all_metrics_during_scroll.update(metrics_at_position)
                logger.info(f"📊 Found {len(metrics_at_position)} metrics at position {current_offset}")
            
            current_offset += step_size
            time.sleep(0.1)  # Short wait time
        
        # Phase 2: Backward scroll to catch any missed metrics
        logger.info("🔄 PHASE 2: Backward comprehensive scroll...")
        current_offset = max_scroll
        while current_offset > 0:
            current_offset -= step_size
            driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, current_offset)
            time.sleep(0.1)
            
            metrics_at_position = extract_metrics_at_scroll_position(driver, element)
            if metrics_at_position:
                all_metrics_during_scroll.update(metrics_at_position)
                logger.info(f"📊 Found {len(metrics_at_position)} metrics at position {current_offset}")
        
        # Phase 3: Ultra-fine scroll with even smaller steps
        logger.info("🔄 PHASE 3: Ultra-fine scroll (step size 10px)...")
        ultra_fine_step = 10
        current_offset = 0
        while current_offset < max_scroll:
            driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, current_offset)
            time.sleep(0.1)
            
            metrics_at_position = extract_metrics_at_scroll_position(driver, element)
            if metrics_at_position:
                all_metrics_during_scroll.update(metrics_at_position)
                logger.info(f"📊 Ultra-fine: Found {len(metrics_at_position)} metrics at position {current_offset}")
            
            current_offset += ultra_fine_step
        
        # Phase 4: Check for dynamic content loading
        logger.info("🔄 PHASE 4: Dynamic content check...")
        driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, max_scroll)
        time.sleep(2)  # Wait longer for dynamic content
        
        # Check if there are more columns by looking for more scrollable content
        new_scroll_state = driver.execute_script("""
            return {
                scrollLeft: arguments[0].scrollLeft,
                scrollTop: arguments[0].scrollTop,
                scrollWidth: arguments[0].scrollWidth,
                scrollHeight: arguments[0].scrollHeight,
                clientWidth: arguments[0].clientWidth,
                clientHeight: arguments[0].clientHeight,
                hasHorizontalScroll: arguments[0].scrollWidth > arguments[0].clientWidth,
                hasVerticalScroll: arguments[0].scrollHeight > arguments[0].clientHeight
            };
        """, element)
        
        if new_scroll_state['scrollWidth'] > scroll_width:
            logger.info(f"📊 DYNAMIC CONTENT FOUND! New width: {new_scroll_state['scrollWidth']} (was {scroll_width})")
            # Continue scrolling with the new width
            new_max_scroll = new_scroll_state['scrollWidth'] - new_scroll_state['clientWidth']
            logger.info(f"📊 New max scroll: {new_max_scroll}")
            
            # Scroll through the newly discovered content
            current_offset = max_scroll
            while current_offset < new_max_scroll:
                current_offset += step_size
                driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, current_offset)
                time.sleep(0.2)
                
                metrics_at_position = extract_metrics_at_scroll_position(driver, element)
                if metrics_at_position:
                    all_metrics_during_scroll.update(metrics_at_position)
                    logger.info(f"📊 Dynamic: Found {len(metrics_at_position)} metrics at position {current_offset}")
        
        # Phase 5: Edge case scrolling - try scrolling beyond the calculated max
        logger.info("🔄 PHASE 5: Edge case scrolling...")
        edge_scroll_positions = [
            max_scroll + 50,
            max_scroll + 100,
            max_scroll + 200,
            max_scroll * 1.1,  # 10% beyond calculated max
            max_scroll * 1.2,  # 20% beyond calculated max
        ]
        
        for edge_pos in edge_scroll_positions:
            try:
                driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, int(edge_pos))
                time.sleep(0.3)
                
                metrics_at_position = extract_metrics_at_scroll_position(driver, element)
                if metrics_at_position:
                    all_metrics_during_scroll.update(metrics_at_position)
                    logger.info(f"📊 Edge case: Found {len(metrics_at_position)} metrics at position {edge_pos}")
            except Exception as e:
                logger.debug(f"Edge scroll failed at {edge_pos}: {e}")
        
        # Phase 6: Try different scroll methods
        logger.info("🔄 PHASE 6: Alternative scroll methods...")
        
        # Method 1: Smooth scroll
        try:
            driver.execute_script("arguments[0].scrollTo({left: 0, behavior: 'smooth'});", element)
            time.sleep(1)
            driver.execute_script("arguments[0].scrollTo({left: arguments[1], behavior: 'smooth'});", element, max_scroll)
            time.sleep(2)
            
            metrics_at_position = extract_metrics_at_scroll_position(driver, element)
            if metrics_at_position:
                all_metrics_during_scroll.update(metrics_at_position)
                logger.info(f"📊 Smooth scroll: Found {len(metrics_at_position)} metrics")
        except Exception as e:
            logger.debug(f"Smooth scroll failed: {e}")
        
        # Method 2: Scroll by element width
        try:
            driver.execute_script("arguments[0].scrollLeft = 0;", element)
            time.sleep(0.5)
            
            # Get all column headers and scroll to each one
            headers = driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
            for i, header in enumerate(headers):
                try:
                    # Scroll to make this header visible
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'start'});", header)
                    time.sleep(0.2)
                    
                    metrics_at_position = extract_metrics_at_scroll_position(driver, element)
                    if metrics_at_position:
                        all_metrics_during_scroll.update(metrics_at_position)
                        logger.info(f"📊 Header scroll {i+1}: Found {len(metrics_at_position)} metrics")
                except Exception as e:
                    logger.debug(f"Header scroll failed for header {i+1}: {e}")
        except Exception as e:
            logger.debug(f"Header-based scroll failed: {e}")
        
        # Reset to beginning
        driver.execute_script("arguments[0].scrollLeft = 0;", element)
        time.sleep(1)
        
        # Log comprehensive results
        if all_metrics_during_scroll:
            logger.info(f"🎉 COMPREHENSIVE SCROLL COMPLETE! Found {len(all_metrics_during_scroll)} total metrics!")
            logger.info("=" * 80)
            for i, metric in enumerate(sorted(all_metrics_during_scroll), 1):
                logger.info(f"  {i:3d}. {metric}")
            logger.info("=" * 80)
        else:
            logger.warning("⚠️ No metrics found during comprehensive scrolling")
        
        return all_metrics_during_scroll
        
    except Exception as e:
        logger.error(f"❌ Error in comprehensive state management scroll: {e}")
        return set()

def scroll_with_debouncing(driver, element, scroll_state):
    """Scroll using debounced approach"""
    try:
        scroll_width = scroll_state['scrollWidth']
        client_width = scroll_state['clientWidth']
        max_scroll = scroll_width - client_width
        
        # Debounced scroll function
        def debounced_scroll(offset):
            driver.execute_script("arguments[0].scrollLeft = arguments[1];", element, offset)
            time.sleep(0.1)  # Debounce delay
        
        # Scroll in smaller steps with debouncing
        step_size = client_width // 8
        current_offset = 0
        
        while current_offset < max_scroll:
            debounced_scroll(current_offset)
            current_offset += step_size
            time.sleep(0.2)  # Additional debounce
        
        # Reset
        debounced_scroll(0)
        time.sleep(1)
        
    except Exception as e:
        logger.error(f"❌ Error in debounced scroll: {e}")

def scroll_with_animation(driver, element, scroll_state):
    """Scroll using animation approach"""
    try:
        scroll_width = scroll_state['scrollWidth']
        client_width = scroll_state['clientWidth']
        max_scroll = scroll_width - client_width
        
        # Scroll with animation
        step_size = client_width // 6
        current_offset = 0
        
        while current_offset < max_scroll:
            # Smooth scroll with animation
            driver.execute_script("""
                arguments[0].scrollTo({
                    left: arguments[1],
                    behavior: 'smooth'
                });
            """, element, current_offset)
            
            time.sleep(1.5)  # Wait for animation
            current_offset += step_size
        
        # Reset with animation
        driver.execute_script("""
            arguments[0].scrollTo({
                left: 0,
                behavior: 'smooth'
            });
        """, element)
        
        time.sleep(2)
        
    except Exception as e:
        logger.error(f"❌ Error in animation scroll: {e}")

def scroll_with_resize_triggers(driver, element, scroll_state):
    """Scroll using resize triggers approach"""
    try:
        scroll_width = scroll_state['scrollWidth']
        client_width = scroll_state['clientWidth']
        max_scroll = scroll_width - client_width
        
        # Set up resize triggers
        driver.execute_script("""
            if (!arguments[0].__resizeTriggers) {
                arguments[0].__resizeTriggers = document.createElement('div');
                arguments[0].__resizeTriggers.className = 'resize-triggers';
                
                var expandTrigger = document.createElement('div');
                expandTrigger.className = 'expand-trigger';
                expandTrigger.appendChild(document.createElement('div'));
                
                var contractTrigger = document.createElement('div');
                contractTrigger.className = 'contract-trigger';
                
                arguments[0].__resizeTriggers.appendChild(expandTrigger);
                arguments[0].__resizeTriggers.appendChild(contractTrigger);
                arguments[0].appendChild(arguments[0].__resizeTriggers);
            }
        """, element)
        
        # Scroll with resize trigger monitoring
        step_size = client_width // 5
        current_offset = 0
        
        while current_offset < max_scroll:
            # Scroll and monitor resize
            driver.execute_script("""
                arguments[0].scrollLeft = arguments[1];
                // Trigger resize event
                if (arguments[0].__resizeTriggers) {
                    arguments[0].__resizeTriggers.dispatchEvent(new Event('resize'));
                }
            """, element, current_offset)
            
            time.sleep(1)
            current_offset += step_size
        
        # Reset
        driver.execute_script("arguments[0].scrollLeft = 0;", element)
        time.sleep(1)
        
    except Exception as e:
        logger.error(f"❌ Error in resize triggers scroll: {e}")

def horizontal_scroll_for_all_metrics(driver):
    """Horizontal scroll to load ALL 135+ metrics from the table"""
    try:
        logger.info("📜 Starting horizontal scroll for all metrics...")
        
        # Find table containers with horizontal scrolling
        table_containers = driver.find_elements(By.CSS_SELECTOR, 
            "div[style*='overflow:auto'], div[style*='overflow-x:auto'], .table, table")
        
        logger.info(f"📊 Found {len(table_containers)} potential table containers")
        
        for i, container in enumerate(table_containers):
            try:
                logger.info(f"📊 Processing container {i+1}/{len(table_containers)}")
                
                # Check if this container has horizontal scroll
                has_horizontal_scroll = driver.execute_script("""
                    return arguments[0].scrollWidth > arguments[0].clientWidth;
                """, container)
                
                if has_horizontal_scroll:
                    logger.info(f"✅ Container {i+1} has horizontal scroll!")
                    
                    # Get scroll dimensions
                    scroll_width = driver.execute_script("return arguments[0].scrollWidth;", container)
                    client_width = driver.execute_script("return arguments[0].clientWidth;", container)
                    
                    logger.info(f"📊 Scroll width: {scroll_width}, Client width: {client_width}")
                    
                    # Scroll horizontally in steps
                    scroll_step = client_width // 4  # Scroll in quarters
                    current_scroll = 0
                    
                    while current_scroll < scroll_width:
                        # Scroll to current position
                        driver.execute_script("arguments[0].scrollLeft = arguments[1];", container, current_scroll)
                        time.sleep(1)  # Wait for content to load
                        
                        logger.info(f"📜 Scrolled to position {current_scroll}/{scroll_width}")
                        
                        # Move to next position
                        current_scroll += scroll_step
                    
                    # Scroll back to beginning
                    driver.execute_script("arguments[0].scrollLeft = 0;", container)
                    time.sleep(1)
                    
                    logger.info(f"✅ Completed horizontal scrolling for container {i+1}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing container {i+1}: {e}")
                continue
        
        # Also try to scroll any table elements specifically
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        for i, table in enumerate(tables):
            try:
                logger.info(f"📊 Processing table {i+1}/{len(tables)}")
                
                # Check if table has horizontal scroll
                has_horizontal_scroll = driver.execute_script("""
                    return arguments[0].scrollWidth > arguments[0].clientWidth;
                """, table)
                
                if has_horizontal_scroll:
                    logger.info(f"✅ Table {i+1} has horizontal scroll!")
                    
                    # Scroll through the table
                    scroll_width = driver.execute_script("return arguments[0].scrollWidth;", table)
                    client_width = driver.execute_script("return arguments[0].clientWidth;", table)
                    
                    scroll_step = client_width // 4
                    current_scroll = 0
                    
                    while current_scroll < scroll_width:
                        driver.execute_script("arguments[0].scrollLeft = arguments[1];", table, current_scroll)
                        time.sleep(1)
                        current_scroll += scroll_step
                        
                    # Reset scroll position
                    driver.execute_script("arguments[0].scrollLeft = 0;", table)
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"❌ Error processing table {i+1}: {e}")
                continue
        
        logger.info("✅ Horizontal scrolling complete!")
        
    except Exception as e:
        logger.error(f"❌ Error in horizontal scrolling: {e}")

def scroll_to_load_all_data(driver):
    """Scroll through the page to load all dynamic content"""
    try:
        # Get initial page height
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll down multiple times to trigger lazy loading
        for i in range(20):  # Scroll 20 times
            logger.info(f"📜 Scroll {i+1}/20...")
            
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Scroll back up a bit to trigger more loading
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000);")
            time.sleep(1)
            
            # Check if new content loaded
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info("📜 No new content loaded, continuing...")
            else:
                logger.info(f"📜 New content loaded! Height: {last_height} -> {new_height}")
                last_height = new_height
            
            # Try to find and click "Load More" or similar buttons
            try:
                load_more_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More') or contains(text(), 'View All')]")
                for button in load_more_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        time.sleep(2)
                        logger.info("📜 Clicked load more button")
            except:
                pass
            
            # Try to find horizontal scroll elements and scroll them
            try:
                horizontal_scrolls = driver.find_elements(By.CSS_SELECTOR, "[style*='overflow-x: auto'], [style*='overflow-x: scroll']")
                for scroll_element in horizontal_scrolls:
                    driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth;", scroll_element)
                    time.sleep(0.5)
            except:
                pass
        
        # Final scroll to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        logger.info("✅ Scrolling complete!")
        
    except Exception as e:
        logger.error(f"❌ Scrolling error: {e}")

if __name__ == "__main__":
    collect_bobcats_data()
