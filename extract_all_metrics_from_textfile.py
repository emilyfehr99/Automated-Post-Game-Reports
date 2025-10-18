#!/usr/bin/env python3
"""
Extract All Metrics from Textfile
Extracts ALL 135+ metrics from textfile.txt using the complete HTML structure
"""

import re
import json
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_all_metrics_from_textfile():
    """Extract all metrics from textfile.txt"""
    try:
        logger.info("🚀 Starting All Metrics Extraction from Textfile...")
        
        # Read the textfile
        with open('hudl-scraping/textfile.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"📄 Read {len(content)} characters from textfile.txt")
        
        # Pattern to match T9n wrapper elements with data-lexic
        pattern = r'<span data-lexic="(\d+)" class="T9n__T9nWrapper-sc-nijj7l-0 huyyNB">([^<]+)</span>'
        
        # Find all matches
        matches = re.findall(pattern, content)
        logger.info(f"📊 Found {len(matches)} T9n wrapper elements in textfile")
        
        # Group by lexic ID
        metrics_by_lexic = defaultdict(lambda: {'lexic_id': '', 'full_name': '', 'abbreviation': '', 'all_texts': []})
        
        for lexic_id, text in matches:
            lexic_id = int(lexic_id)
            text = text.strip()
            
            if not text:
                continue
                
            metrics_by_lexic[lexic_id]['lexic_id'] = lexic_id
            metrics_by_lexic[lexic_id]['all_texts'].append(text)
            
            # Determine if this is the full name or abbreviation
            if len(text) > 3 and not text.isupper() and not text.isdigit():
                # Likely the full name
                if not metrics_by_lexic[lexic_id]['full_name']:
                    metrics_by_lexic[lexic_id]['full_name'] = text
            elif len(text) <= 3 and text.isupper():
                # Likely the abbreviation
                if not metrics_by_lexic[lexic_id]['abbreviation']:
                    metrics_by_lexic[lexic_id]['abbreviation'] = text
        
        # Convert to regular dict and sort by lexic ID
        metrics_dict = dict(sorted(metrics_by_lexic.items()))
        
        logger.info(f"📊 Found {len(metrics_dict)} unique metrics with lexic IDs")
        
        # Show all metrics found
        logger.info("📊 ALL METRICS FOUND IN TEXTFILE:")
        logger.info("=" * 100)
        for i, (lexic_id, metric) in enumerate(metrics_dict.items(), 1):
            full_name = metric['full_name'] or 'N/A'
            abbreviation = metric['abbreviation'] or 'N/A'
            logger.info(f"{i:3d}. ID {lexic_id}: {full_name} ({abbreviation})")
            if len(metric['all_texts']) > 2:
                logger.info(f"     All texts: {', '.join(metric['all_texts'])}")
        
        # Also extract all column headers
        logger.info("🔍 Extracting all column headers...")
        column_header_pattern = r'<div role="columnheader"[^>]*>.*?<span data-lexic="(\d+)" class="T9n__T9nWrapper-sc-nijj7l-0 huyyNB">([^<]+)</span>.*?<span data-lexic="(\d+)" class="T9n__T9nWrapper-sc-nijj7l-0 huyyNB">([^<]+)</span>'
        
        column_headers = re.findall(column_header_pattern, content)
        logger.info(f"📊 Found {len(column_headers)} column header pairs")
        
        # Show column headers
        logger.info("📊 COLUMN HEADERS FOUND:")
        logger.info("=" * 80)
        for i, (lexic1, name1, lexic2, name2) in enumerate(column_headers, 1):
            logger.info(f"{i:3d}. {name1.strip()} ({lexic1}) / {name2.strip()} ({lexic2})")
        
        # Save results
        results = {
            'metrics': metrics_dict,
            'column_headers': column_headers,
            'total_t9n_elements': len(matches),
            'unique_metrics': len(metrics_dict),
            'total_column_headers': len(column_headers)
        }
        
        with open('all_metrics_from_textfile.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("✅ Results saved to all_metrics_from_textfile.json")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Error extracting metrics from textfile: {e}")
        return {}

def main():
    """Main function"""
    results = extract_all_metrics_from_textfile()
    
    if results:
        logger.info(f"✅ Successfully extracted {results.get('unique_metrics', 0)} unique metrics!")
        logger.info(f"📊 Total T9n elements: {results.get('total_t9n_elements', 0)}")
        logger.info(f"📊 Column headers: {results.get('total_column_headers', 0)}")
    else:
        logger.error("❌ Failed to extract metrics from textfile")

if __name__ == "__main__":
    main()
