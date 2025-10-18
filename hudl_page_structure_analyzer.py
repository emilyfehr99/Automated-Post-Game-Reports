#!/usr/bin/env python3
"""
Hudl Instat Page Structure Analyzer
Comprehensive analysis of Hudl Instat team page structure, tabs, and data sections
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HudlPageStructureAnalyzer:
    """Comprehensive analyzer for Hudl Instat team page structure"""
    
    def __init__(self, headless: bool = False, user_identifier: str = None):
        """Initialize the page structure analyzer"""
        self.base_url = "https://app.hudl.com/instat/hockey/teams"
        self.driver = None
        self.headless = headless
        self.user_identifier = user_identifier or "structure_analyzer"
        self.is_authenticated = False
        
    def setup_driver(self):
        """Setup Chrome WebDriver for detailed page analysis"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            
            # Add user-specific profile
            profile_dir = f"/tmp/hudl_profile_{self.user_identifier}"
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument(f"--profile-directory=Profile_{self.user_identifier}")
            
            # Enable logging for network requests
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized for structure analysis")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Chrome WebDriver: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate with Hudl Instat"""
        if not self.driver:
            if not self.setup_driver():
                return False
        
        try:
            # Navigate to login page
            login_url = "https://app.hudl.com/login"
            self.driver.get(login_url)
            
            # Wait for login form
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email']"))
            )
            
            # Find and fill login form
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[name='email']")
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            
            email_field.send_keys(username)
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            # Wait for redirect
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.current_url != login_url
            )
            
            if "login" not in self.driver.current_url.lower():
                self.is_authenticated = True
                logger.info("✅ Successfully authenticated with Hudl Instat")
                return True
            else:
                logger.error("❌ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def analyze_team_page_structure(self, team_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of team page structure"""
        if not self.is_authenticated:
            logger.error("❌ Must authenticate before analyzing page structure")
            return {"error": "Authentication required"}
        
        team_url = f"{self.base_url}/{team_id}"
        logger.info(f"🔍 Analyzing Hudl Instat team page structure: {team_url}")
        
        try:
            # Navigate to team page
            self.driver.get(team_url)
            
            # Wait for page to load completely
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(5)
            
            analysis = {
                "team_id": team_id,
                "url": team_url,
                "analysis_timestamp": datetime.now().isoformat(),
                "page_title": self.driver.title,
                "current_url": self.driver.current_url,
                "navigation_structure": {},
                "tabs_and_sections": {},
                "data_export_options": {},
                "api_endpoints": [],
                "page_elements": {},
                "interactive_elements": {},
                "data_tables": {},
                "forms_and_inputs": {},
                "download_options": {}
            }
            
            # Analyze navigation structure
            analysis["navigation_structure"] = self._analyze_navigation()
            
            # Analyze tabs and sections
            analysis["tabs_and_sections"] = self._analyze_tabs_and_sections()
            
            # Analyze data export options
            analysis["data_export_options"] = self._analyze_export_options()
            
            # Analyze page elements
            analysis["page_elements"] = self._analyze_page_elements()
            
            # Analyze interactive elements
            analysis["interactive_elements"] = self._analyze_interactive_elements()
            
            # Analyze data tables
            analysis["data_tables"] = self._analyze_data_tables()
            
            # Analyze forms and inputs
            analysis["forms_and_inputs"] = self._analyze_forms()
            
            # Analyze download options
            analysis["download_options"] = self._analyze_download_options()
            
            # Capture network requests
            analysis["api_endpoints"] = self._capture_network_requests()
            
            logger.info("✅ Page structure analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing page structure: {e}")
            return {"error": str(e), "team_id": team_id}
    
    def _analyze_navigation(self) -> Dict[str, Any]:
        """Analyze the main navigation structure"""
        logger.info("🧭 Analyzing navigation structure...")
        
        navigation = {
            "main_nav": [],
            "breadcrumbs": [],
            "side_nav": [],
            "tabs": [],
            "menu_items": []
        }
        
        try:
            # Main navigation
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "nav, .navbar, .navigation, .main-nav, [role='navigation']")
            
            for nav in nav_elements:
                links = nav.find_elements(By.CSS_SELECTOR, "a, button")
                for link in links:
                    if link.text.strip():
                        navigation["main_nav"].append({
                            "text": link.text.strip(),
                            "href": link.get_attribute("href"),
                            "class": link.get_attribute("class")
                        })
            
            # Breadcrumbs
            breadcrumb_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".breadcrumb, .breadcrumbs, [aria-label*='breadcrumb']")
            
            for breadcrumb in breadcrumb_elements:
                items = breadcrumb.find_elements(By.CSS_SELECTOR, "a, span")
                for item in items:
                    if item.text.strip():
                        navigation["breadcrumbs"].append({
                            "text": item.text.strip(),
                            "href": item.get_attribute("href")
                        })
            
            # Side navigation
            side_nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".sidebar, .side-nav, .side-navigation, .left-nav")
            
            for side_nav in side_nav_elements:
                links = side_nav.find_elements(By.CSS_SELECTOR, "a, button")
                for link in links:
                    if link.text.strip():
                        navigation["side_nav"].append({
                            "text": link.text.strip(),
                            "href": link.get_attribute("href"),
                            "class": link.get_attribute("class")
                        })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing navigation: {e}")
        
        return navigation
    
    def _analyze_tabs_and_sections(self) -> Dict[str, Any]:
        """Analyze all tabs and sections on the page"""
        logger.info("📑 Analyzing tabs and sections...")
        
        tabs_sections = {
            "main_tabs": [],
            "sub_tabs": [],
            "sections": [],
            "panels": [],
            "accordions": []
        }
        
        try:
            # Main tabs
            tab_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                ".tab, .tabs, [role='tab'], .nav-tabs, .tab-list")
            
            for tab_container in tab_elements:
                tabs = tab_container.find_elements(By.CSS_SELECTOR, 
                    "a, button, .tab-item, .tab-link")
                
                for tab in tabs:
                    if tab.text.strip():
                        tabs_sections["main_tabs"].append({
                            "text": tab.text.strip(),
                            "href": tab.get_attribute("href"),
                            "class": tab.get_attribute("class"),
                            "active": "active" in tab.get_attribute("class") or "selected" in tab.get_attribute("class")
                        })
            
            # Sections and panels
            section_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "section, .section, .panel, .card, .widget, .module")
            
            for section in section_elements:
                title_element = section.find_element(By.CSS_SELECTOR, 
                    "h1, h2, h3, h4, h5, h6, .title, .header, .section-title")
                
                if title_element:
                    tabs_sections["sections"].append({
                        "title": title_element.text.strip(),
                        "class": section.get_attribute("class"),
                        "id": section.get_attribute("id"),
                        "visible": section.is_displayed()
                    })
            
            # Look for specific Hudl Instat sections
            hudl_sections = [
                "Games", "Players", "Statistics", "Analytics", "Reports", 
                "Video", "Scouting", "Performance", "Team Stats", "Player Stats",
                "Game Analysis", "Tactics", "Formations", "Set Pieces"
            ]
            
            for section_name in hudl_sections:
                elements = self.driver.find_elements(By.XPATH, 
                    f"//*[contains(text(), '{section_name}') or contains(@class, '{section_name.lower()}')]")
                
                if elements:
                    tabs_sections["sections"].append({
                        "title": section_name,
                        "found": True,
                        "count": len(elements),
                        "elements": [{"text": el.text.strip(), "tag": el.tag_name} for el in elements[:3]]
                    })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing tabs and sections: {e}")
        
        return tabs_sections
    
    def _analyze_export_options(self) -> Dict[str, Any]:
        """Analyze data export and download options"""
        logger.info("📥 Analyzing export options...")
        
        export_options = {
            "download_buttons": [],
            "export_links": [],
            "csv_options": [],
            "excel_options": [],
            "pdf_options": [],
            "data_selection_forms": []
        }
        
        try:
            # Look for download/export buttons
            download_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "button[title*='download'], button[title*='export'], .download, .export, [data-testid*='download'], [data-testid*='export']")
            
            for element in download_elements:
                export_options["download_buttons"].append({
                    "text": element.text.strip(),
                    "title": element.get_attribute("title"),
                    "class": element.get_attribute("class"),
                    "data_testid": element.get_attribute("data-testid")
                })
            
            # Look for CSV/Excel/PDF specific options
            for format_type in ["csv", "excel", "pdf"]:
                elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    f"*[href*='.{format_type}'], *[data-format='{format_type}'], *[title*='{format_type}']")
                
                for element in elements:
                    export_options[f"{format_type}_options"].append({
                        "text": element.text.strip(),
                        "href": element.get_attribute("href"),
                        "title": element.get_attribute("title")
                    })
            
            # Look for data selection forms
            forms = self.driver.find_elements(By.CSS_SELECTOR, 
                "form, .form, .data-selection, .export-form")
            
            for form in forms:
                form_data = {
                    "class": form.get_attribute("class"),
                    "id": form.get_attribute("id"),
                    "inputs": [],
                    "selects": [],
                    "checkboxes": []
                }
                
                # Analyze form inputs
                inputs = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                for input_elem in inputs:
                    input_type = input_elem.get_attribute("type") or input_elem.tag_name
                    form_data[f"{input_type}s"].append({
                        "name": input_elem.get_attribute("name"),
                        "id": input_elem.get_attribute("id"),
                        "placeholder": input_elem.get_attribute("placeholder"),
                        "value": input_elem.get_attribute("value")
                    })
                
                if form_data["inputs"] or form_data["selects"] or form_data["checkboxes"]:
                    export_options["data_selection_forms"].append(form_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing export options: {e}")
        
        return export_options
    
    def _analyze_page_elements(self) -> Dict[str, Any]:
        """Analyze general page elements"""
        logger.info("🔍 Analyzing page elements...")
        
        elements = {
            "headings": [],
            "tables": [],
            "lists": [],
            "images": [],
            "buttons": [],
            "links": [],
            "forms": []
        }
        
        try:
            # Headings
            for i in range(1, 7):
                headings = self.driver.find_elements(By.CSS_SELECTOR, f"h{i}")
                for heading in headings:
                    if heading.text.strip():
                        elements["headings"].append({
                            "level": i,
                            "text": heading.text.strip(),
                            "class": heading.get_attribute("class")
                        })
            
            # Tables
            tables = self.driver.find_elements(By.CSS_SELECTOR, "table")
            for table in tables:
                rows = table.find_elements(By.CSS_SELECTOR, "tr")
                elements["tables"].append({
                    "rows": len(rows),
                    "class": table.get_attribute("class"),
                    "id": table.get_attribute("id")
                })
            
            # Buttons
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button, input[type='button'], input[type='submit']")
            for button in buttons:
                if button.text.strip():
                    elements["buttons"].append({
                        "text": button.text.strip(),
                        "class": button.get_attribute("class"),
                        "type": button.get_attribute("type")
                    })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing page elements: {e}")
        
        return elements
    
    def _analyze_interactive_elements(self) -> Dict[str, Any]:
        """Analyze interactive elements like dropdowns, modals, etc."""
        logger.info("🎛️ Analyzing interactive elements...")
        
        interactive = {
            "dropdowns": [],
            "modals": [],
            "tooltips": [],
            "accordions": [],
            "tabs": [],
            "sliders": []
        }
        
        try:
            # Dropdowns
            dropdowns = self.driver.find_elements(By.CSS_SELECTOR, 
                "select, .dropdown, .select, [role='combobox']")
            
            for dropdown in dropdowns:
                options = dropdown.find_elements(By.CSS_SELECTOR, "option")
                interactive["dropdowns"].append({
                    "tag": dropdown.tag_name,
                    "class": dropdown.get_attribute("class"),
                    "options_count": len(options),
                    "options": [opt.text.strip() for opt in options[:10]]  # First 10 options
                })
            
            # Modals
            modals = self.driver.find_elements(By.CSS_SELECTOR, 
                ".modal, .popup, .dialog, [role='dialog']")
            
            for modal in modals:
                interactive["modals"].append({
                    "class": modal.get_attribute("class"),
                    "visible": modal.is_displayed(),
                    "title": modal.find_element(By.CSS_SELECTOR, "h1, h2, h3, .title").text.strip() if modal.find_elements(By.CSS_SELECTOR, "h1, h2, h3, .title") else "No title"
                })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing interactive elements: {e}")
        
        return interactive
    
    def _analyze_data_tables(self) -> Dict[str, Any]:
        """Analyze data tables and their structure"""
        logger.info("📊 Analyzing data tables...")
        
        tables = {
            "data_tables": [],
            "sortable_tables": [],
            "filterable_tables": [],
            "pagination": []
        }
        
        try:
            # Find all tables
            table_elements = self.driver.find_elements(By.CSS_SELECTOR, "table")
            
            for table in table_elements:
                table_data = {
                    "class": table.get_attribute("class"),
                    "id": table.get_attribute("id"),
                    "rows": len(table.find_elements(By.CSS_SELECTOR, "tr")),
                    "columns": len(table.find_elements(By.CSS_SELECTOR, "th, td")),
                    "headers": [],
                    "has_sorting": False,
                    "has_filtering": False,
                    "has_pagination": False
                }
                
                # Get headers
                headers = table.find_elements(By.CSS_SELECTOR, "th")
                for header in headers:
                    table_data["headers"].append(header.text.strip())
                
                # Check for sorting
                if table.find_elements(By.CSS_SELECTOR, ".sortable, .sort, [data-sort]"):
                    table_data["has_sorting"] = True
                    tables["sortable_tables"].append(table_data)
                
                # Check for filtering
                if table.find_elements(By.CSS_SELECTOR, ".filter, input[type='search'], .search"):
                    table_data["has_filtering"] = True
                    tables["filterable_tables"].append(table_data)
                
                # Check for pagination
                if table.find_elements(By.CSS_SELECTOR, ".pagination, .pager, .page-nav"):
                    table_data["has_pagination"] = True
                    tables["pagination"].append(table_data)
                
                tables["data_tables"].append(table_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing data tables: {e}")
        
        return tables
    
    def _analyze_forms(self) -> Dict[str, Any]:
        """Analyze forms and input elements"""
        logger.info("📝 Analyzing forms...")
        
        forms = {
            "forms": [],
            "input_fields": [],
            "select_fields": [],
            "checkbox_fields": [],
            "radio_fields": []
        }
        
        try:
            # Find all forms
            form_elements = self.driver.find_elements(By.CSS_SELECTOR, "form")
            
            for form in form_elements:
                form_data = {
                    "class": form.get_attribute("class"),
                    "id": form.get_attribute("id"),
                    "action": form.get_attribute("action"),
                    "method": form.get_attribute("method"),
                    "inputs": []
                }
                
                # Analyze form inputs
                inputs = form.find_elements(By.CSS_SELECTOR, "input, select, textarea")
                for input_elem in inputs:
                    input_data = {
                        "type": input_elem.get_attribute("type") or input_elem.tag_name,
                        "name": input_elem.get_attribute("name"),
                        "id": input_elem.get_attribute("id"),
                        "placeholder": input_elem.get_attribute("placeholder"),
                        "required": input_elem.get_attribute("required") is not None
                    }
                    form_data["inputs"].append(input_data)
                
                forms["forms"].append(form_data)
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing forms: {e}")
        
        return forms
    
    def _analyze_download_options(self) -> Dict[str, Any]:
        """Analyze specific download and export options"""
        logger.info("💾 Analyzing download options...")
        
        downloads = {
            "csv_downloads": [],
            "excel_downloads": [],
            "pdf_downloads": [],
            "data_export_buttons": [],
            "bulk_download_options": []
        }
        
        try:
            # Look for specific download patterns
            download_patterns = [
                "download", "export", "csv", "excel", "pdf", "data", "report"
            ]
            
            for pattern in download_patterns:
                elements = self.driver.find_elements(By.XPATH, 
                    f"//*[contains(text(), '{pattern}') or contains(@class, '{pattern}') or contains(@title, '{pattern}')]")
                
                for element in elements:
                    if element.tag_name in ["button", "a", "input"]:
                        downloads["data_export_buttons"].append({
                            "text": element.text.strip(),
                            "tag": element.tag_name,
                            "class": element.get_attribute("class"),
                            "href": element.get_attribute("href"),
                            "pattern": pattern
                        })
            
        except Exception as e:
            logger.warning(f"⚠️  Error analyzing download options: {e}")
        
        return downloads
    
    def _capture_network_requests(self) -> List[str]:
        """Capture network requests made by the page"""
        logger.info("🌐 Capturing network requests...")
        
        try:
            logs = self.driver.get_log('performance')
            api_calls = []
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if any(keyword in url.lower() for keyword in ['api', 'data', 'json', 'ajax', 'export', 'download']):
                        api_calls.append(url)
            
            return api_calls[:20]  # Limit to first 20 API calls
            
        except Exception as e:
            logger.warning(f"⚠️  Could not capture network requests: {e}")
            return []
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 WebDriver closed")

def main():
    """Main function to demonstrate the page structure analyzer"""
    print("🏒 Hudl Instat Page Structure Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = HudlPageStructureAnalyzer(headless=False)
    
    try:
        # Authenticate
        from hudl_credentials import HUDL_USERNAME, HUDL_PASSWORD
        if not analyzer.authenticate(HUDL_USERNAME, HUDL_PASSWORD):
            print("❌ Authentication failed")
            return
        
        # Analyze team page structure
        team_id = "21479"  # Bobcats team ID
        analysis = analyzer.analyze_team_page_structure(team_id)
        
        # Save analysis results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hudl_page_structure_analysis_{team_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"📄 Analysis saved to: {filename}")
        
        # Print summary
        print(f"\n📊 Analysis Summary:")
        print(f"  Navigation items: {len(analysis.get('navigation_structure', {}).get('main_nav', []))}")
        print(f"  Main tabs: {len(analysis.get('tabs_and_sections', {}).get('main_tabs', []))}")
        print(f"  Sections found: {len(analysis.get('tabs_and_sections', {}).get('sections', []))}")
        print(f"  Download buttons: {len(analysis.get('data_export_options', {}).get('download_buttons', []))}")
        print(f"  Data tables: {len(analysis.get('data_tables', {}).get('data_tables', []))}")
        print(f"  API endpoints: {len(analysis.get('api_endpoints', []))}")
        
    except ImportError:
        print("❌ Please update hudl_credentials.py with your actual credentials")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()
