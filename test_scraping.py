#!/usr/bin/env python3
"""
Standalone web scraping test for the Tixel Scraper.
This tests only the ticket checking functionality.
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def check_tickets(url):
    """
    Check if tickets are available on the Tixel page.
    Returns True if tickets are found, False otherwise.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        print(f"🔗 Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"📄 Content Length: {len(response.text)} characters")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for ticket elements
        ticket_elements = soup.find_all('div', class_='space-y-3 text-left')
        
        print(f"🎫 Found {len(ticket_elements)} ticket elements")
        
        # Print some details about what we found
        if ticket_elements:
            print("\n📋 Ticket Elements Found:")
            for i, element in enumerate(ticket_elements[:3]):  # Show first 3
                text = element.get_text(strip=True)[:100]  # First 100 chars
                print(f"  {i+1}. {text}...")
        
        # Look for other potential ticket indicators
        other_indicators = [
            ('button', {'class': 'btn'}),
            ('a', {'href': lambda x: x and 'buy' in x.lower()}),
            ('div', {'class': lambda x: x and 'ticket' in x.lower()}),
            ('span', {'class': lambda x: x and 'price' in x.lower()}),
        ]
        
        print("\n🔍 Other Potential Ticket Indicators:")
        for tag, attrs in other_indicators:
            elements = soup.find_all(tag, attrs)
            if elements:
                print(f"  - Found {len(elements)} {tag} elements matching criteria")
                if elements:
                    sample_text = elements[0].get_text(strip=True)[:50]
                    print(f"    Sample: {sample_text}...")
        
        return len(ticket_elements) > 0
        
    except requests.RequestException as e:
        print(f"❌ Error fetching Tixel page: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def analyze_page_structure(url):
    """
    Analyze the page structure to help understand what elements are available.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    try:
        print(f"\n🔬 Analyzing page structure for: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for common class patterns
        all_divs = soup.find_all('div', class_=True)
        class_patterns = {}
        
        for div in all_divs:
            classes = div.get('class', [])
            for cls in classes:
                if any(keyword in cls.lower() for keyword in ['ticket', 'price', 'buy', 'available', 'sold']):
                    class_patterns[cls] = class_patterns.get(cls, 0) + 1
        
        if class_patterns:
            print("\n📊 Relevant CSS Classes Found:")
            for cls, count in sorted(class_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {cls}: {count} occurrences")
        
        # Look for text content that might indicate tickets
        page_text = soup.get_text().lower()
        keywords = ['ticket', 'available', 'sold out', 'buy now', 'purchase', 'general admission']
        
        print("\n🔤 Keyword Analysis:")
        for keyword in keywords:
            count = page_text.count(keyword)
            if count > 0:
                print(f"  - '{keyword}': {count} occurrences")
        
    except Exception as e:
        print(f"❌ Error analyzing page: {str(e)}")

def main():
    """Main testing function"""
    
    print("🕷️  Tixel Web Scraping Test")
    print("=" * 40)
    
    # Get URL from .env file
    tixel_url = os.getenv('TIXEL_URL')
    
    if not tixel_url:
        print("❌ TIXEL_URL not found in .env file!")
        print("Please ensure your .env file contains the TIXEL_URL variable.")
        return
    
    print(f"🎯 Testing URL: {tixel_url}")
    
    # Test ticket checking
    print("\n1️⃣ Testing ticket availability check...")
    tickets_available = check_tickets(tixel_url)
    
    if tickets_available:
        print("\n✅ TICKETS FOUND! The scraper detected available tickets.")
    else:
        print("\n❌ NO TICKETS FOUND. The scraper did not detect any tickets.")
    
    # Analyze page structure
    print("\n2️⃣ Analyzing page structure...")
    analyze_page_structure(tixel_url)
    
    print("\n" + "=" * 40)
    print("🎯 Summary:")
    print(f"  URL: {tixel_url}")
    print(f"  Tickets Available: {'YES' if tickets_available else 'NO'}")
    print(f"  Status: {'✅ Working' if tickets_available else '⚠️  No tickets detected'}")
    
    if not tickets_available:
        print("\n💡 Troubleshooting Tips:")
        print("  1. Check if the URL is correct and accessible")
        print("  2. The page might not have tickets available right now")
        print("  3. The page structure might have changed")
        print("  4. Check the 'Relevant CSS Classes' above for clues")

if __name__ == "__main__":
    main() 