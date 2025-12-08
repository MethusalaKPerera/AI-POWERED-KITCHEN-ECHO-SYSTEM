import requests
from bs4 import BeautifulSoup

def test_scrape_with_headers(query):
    print(f"Testing scraping for '{query}' with headers...")
    
    url = f'https://www.ebay.com/sch/i.html?_nkw={query}'
    
    # Mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.select('.s-item')
            print(f"Found {len(items)} items")
            
            for item in items[1:6]: # Skip first (often hidden) and show next 5
                title = item.select_one('.s-item__title')
                price = item.select_one('.s-item__price')
                if title and price:
                    print(f" - {title.text.strip()} : {price.text.strip()}")
        else:
            print("Failed to fetch page")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape_with_headers("laptop")
