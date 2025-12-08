import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Test eBay
print("Testing eBay...")
url = 'https://www.ebay.com/sch/i.html?_nkw=laptop'
response = requests.get(url, headers=HEADERS, timeout=10)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# Save HTML for inspection
with open('ebay_response.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("Saved to ebay_response.html")

# Try to find items
items = soup.select('.s-item')
print(f"Found {len(items)} items with .s-item selector")

# Try alternative selectors
alt_items = soup.select('[class*="s-item"]')
print(f"Found {len(alt_items)} items with partial class match")

# Print first few class names
all_divs = soup.find_all('div', limit=20)
print("\nFirst 20 div classes:")
for div in all_divs:
    if div.get('class'):
        print(f"  {div.get('class')}")
