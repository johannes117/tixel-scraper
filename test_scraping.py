#!/usr/bin/env python3
"""
Standalone web scraping test for the Tixel Scraper.
This tests only the ticket checking functionality with criteria filtering.
"""

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()

def check_tickets_with_criteria(url, max_price=None, desired_quantity=None):
    """
    Check if tickets matching the criteria are available on the Tixel page.
    Returns (True, ticket_details) if matching tickets are found, (False, None) otherwise.
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
        
        # Find all button elements which act as containers for ticket listings
        ticket_listings = soup.select('div[class*="mt-6 space-y-3"] button[class*="rounded-lg"]')
        
        if not ticket_listings:
            print("❌ No ticket listing containers found on page.")
            return False, None
            
        print(f"🎫 Found {len(ticket_listings)} ticket listings to analyze")
        
        matching_tickets = []
        all_tickets = []
        
        for i, ticket in enumerate(ticket_listings):
            try:
                # Extract ticket type/description
                type_element = ticket.find('p', class_='font-semibold')
                ticket_type = type_element.text.strip() if type_element else "N/A"
                
                # Extract the text containing price and quantity
                details_element = ticket.find('p', class_='text-gray-500')
                if not details_element:
                    continue
                
                details_text = details_element.text.strip()

                # Parse price using regex
                price_match = re.search(r'\$(\d+\.?\d*)', details_text)
                price = float(price_match.group(1)) if price_match else -1

                # Parse quantity using regex
                quantity_match = re.search(r'(\d+)\s+ticket', details_text)
                quantity = int(quantity_match.group(1)) if quantity_match else -1

                if price > 0 and quantity > 0:
                    ticket_info = {
                        "type": ticket_type,
                        "price": price,
                        "quantity": quantity,
                        "details": details_text
                    }
                    all_tickets.append(ticket_info)
                    
                    print(f"  {i+1}. Type: '{ticket_type}', Price: ${price}, Quantity: {quantity}")
                    
                    # Check if it meets the criteria
                    meets_criteria = True
                    if max_price is not None and price > max_price:
                        meets_criteria = False
                    if desired_quantity is not None and quantity != desired_quantity:
                        meets_criteria = False
                    
                    if meets_criteria:
                        matching_tickets.append(ticket_info)
                        print(f"     ✅ MATCHES CRITERIA!")
                    else:
                        criteria_issues = []
                        if max_price is not None and price > max_price:
                            criteria_issues.append(f"price ${price} > ${max_price}")
                        if desired_quantity is not None and quantity != desired_quantity:
                            criteria_issues.append(f"quantity {quantity} != {desired_quantity}")
                        print(f"     ❌ Does not match: {', '.join(criteria_issues)}")
                
            except (AttributeError, ValueError, TypeError) as e:
                print(f"     ⚠️  Could not parse ticket {i+1}: {e}")
                continue

        print(f"\n📊 Summary:")
        print(f"  Total tickets found: {len(all_tickets)}")
        print(f"  Matching criteria: {len(matching_tickets)}")
        
        if matching_tickets:
            return True, matching_tickets[0]  # Return first matching ticket
        else:
            return False, None
        
    except requests.RequestException as e:
        print(f"❌ Error fetching Tixel page: {str(e)}")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False, None

def check_tickets_basic(url):
    """
    Basic ticket availability check (legacy function for compatibility).
    Returns True if any tickets are found, False otherwise.
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
        
        # Look for ticket elements (legacy method)
        ticket_elements = soup.find_all('div', class_='space-y-3 text-left')
        
        print(f"🎫 Found {len(ticket_elements)} ticket elements (legacy method)")
        
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
    
    print("🕷️  Tixel Web Scraping Test with Criteria")
    print("=" * 50)
    
    # Get configuration from .env file
    tixel_url = os.getenv('TIXEL_URL')
    max_price = float(os.getenv('MAX_PRICE', 100.0))
    desired_quantity = int(os.getenv('DESIRED_QUANTITY', 2))
    
    if not tixel_url:
        print("❌ TIXEL_URL not found in .env file!")
        print("Please ensure your .env file contains the TIXEL_URL variable.")
        return
    
    print(f"🎯 Testing URL: {tixel_url}")
    print(f"💰 Max Price: ${max_price}")
    print(f"🎫 Desired Quantity: {desired_quantity}")
    
    # Test 1: Basic ticket availability check (legacy)
    print("\n1️⃣ Testing basic ticket availability (legacy method)...")
    print("-" * 40)
    tickets_available_basic = check_tickets_basic(tixel_url)
    
    if tickets_available_basic:
        print("\n✅ TICKETS FOUND! (Basic check)")
    else:
        print("\n❌ NO TICKETS FOUND (Basic check)")
    
    # Test 2: Criteria-based ticket checking (new method)
    print("\n2️⃣ Testing criteria-based ticket checking...")
    print("-" * 40)
    matching_found, ticket_details = check_tickets_with_criteria(tixel_url, max_price, desired_quantity)
    
    if matching_found:
        print(f"\n✅ MATCHING TICKET FOUND!")
        print(f"  Type: {ticket_details['type']}")
        print(f"  Price: ${ticket_details['price']}")
        print(f"  Quantity: {ticket_details['quantity']}")
    else:
        print(f"\n❌ NO MATCHING TICKETS FOUND")
        print(f"  (No tickets meet criteria: price ≤ ${max_price}, quantity = {desired_quantity})")
    
    # Test 3: Analyze page structure
    print("\n3️⃣ Analyzing page structure...")
    print("-" * 40)
    analyze_page_structure(tixel_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 SUMMARY:")
    print(f"  URL: {tixel_url}")
    print(f"  Max Price: ${max_price}")
    print(f"  Desired Quantity: {desired_quantity}")
    print(f"  Basic Check: {'✅ Found tickets' if tickets_available_basic else '❌ No tickets'}")
    print(f"  Criteria Check: {'✅ Found matching' if matching_found else '❌ No matches'}")
    
    if tickets_available_basic and not matching_found:
        print(f"\n💡 INSIGHT: Tickets are available but none match your criteria!")
        print(f"   Try adjusting MAX_PRICE (currently ${max_price}) or DESIRED_QUANTITY (currently {desired_quantity})")
    elif not tickets_available_basic:
        print(f"\n💡 TROUBLESHOOTING TIPS:")
        print(f"   1. Check if the URL is correct and accessible")
        print(f"   2. The page might not have tickets available right now")
        print(f"   3. The page structure might have changed")
        print(f"   4. Check the 'Relevant CSS Classes' above for clues")

if __name__ == "__main__":
    main() 