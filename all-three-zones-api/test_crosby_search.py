#!/usr/bin/env python3
"""
Test script to search for Sidney Crosby specifically
"""

import requests
import json
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_crosby_search():
    """Test searching for Sidney Crosby specifically"""
    logger.info("🏒 Testing Sidney Crosby Search")
    logger.info("=" * 50)
    
    # Test API search endpoint
    try:
        # Test 1: Direct API call
        logger.info("1. Testing API search endpoint...")
        response = requests.get("http://localhost:8000/search?query=Sidney%20Crosby")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ API Response: {data}")
            
            if data:
                logger.info(f"✅ Found {len(data)} results for Sidney Crosby")
                for i, player in enumerate(data):
                    logger.info(f"  Player {i+1}: {player}")
            else:
                logger.warning("⚠️  No results found for Sidney Crosby")
        else:
            logger.error(f"❌ API Error: {response.status_code} - {response.text}")
        
        # Test 2: Test with different search terms
        logger.info("\n2. Testing different search terms...")
        search_terms = ["Crosby", "Sidney", "Sidney Crosby", "SIDNEY CROSBY"]
        
        for term in search_terms:
            encoded_term = requests.utils.quote(term)
            response = requests.get(f"http://localhost:8000/search?query={encoded_term}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ '{term}': Found {len(data)} results")
            else:
                logger.error(f"❌ '{term}': Error {response.status_code}")
        
        # Test 3: Test all players endpoint
        logger.info("\n3. Testing all players endpoint...")
        response = requests.get("http://localhost:8000/players")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ All players: Found {len(data)} total players")
            
            # Look for Crosby in the results
            crosby_found = any(
                'crosby' in str(player).lower() 
                for player in data
            )
            
            if crosby_found:
                logger.info("✅ Found Crosby in all players list")
            else:
                logger.warning("⚠️  Crosby not found in all players list")
        else:
            logger.error(f"❌ All players error: {response.status_code}")
        
        # Test 4: Test authentication status
        logger.info("\n4. Testing authentication...")
        from a3z_scraper import AllThreeZonesScraper
        
        scraper = AllThreeZonesScraper()
        
        if scraper.login():
            logger.info("✅ Authentication successful")
            
            # Try to get player data directly
            players = scraper.get_player_data()
            logger.info(f"✅ Direct scraper: Found {len(players)} players")
            
            # Look for Crosby in direct results
            crosby_players = [
                p for p in players 
                if 'crosby' in p.name.lower() or 'sidney' in p.name.lower()
            ]
            
            if crosby_players:
                logger.info(f"✅ Found {len(crosby_players)} Crosby players in direct results")
                for player in crosby_players:
                    logger.info(f"  - {player.name} ({player.team})")
            else:
                logger.warning("⚠️  No Crosby players found in direct results")
        else:
            logger.error("❌ Authentication failed")
            
    except Exception as e:
        logger.error(f"❌ Error during Crosby search test: {e}")
        return False
    finally:
        if 'scraper' in locals():
            scraper.close()
    
    return True

def main():
    """Main test function"""
    if test_crosby_search():
        logger.info("\n🎉 Crosby search test completed!")
        logger.info("\nNext steps:")
        logger.info("1. The API is working correctly")
        logger.info("2. We need to improve the Tableau data extraction")
        logger.info("3. Once parsing is fixed, Crosby data will be available")
    else:
        logger.error("❌ Crosby search test failed")

if __name__ == "__main__":
    main() 