import requests
from bs4 import BeautifulSoup

def scrape_products(product_type, site):
    print(f"Scraping {product_type} from {site}...")
    if site == "ebay":
        url = f'https://www.ebay.com/sch/i.html?_nkw={product_type}'
    elif site == "walmart":
        url = f'https://www.walmart.com/search/?query={product_type}'
    else:
        return []

    # User's code didn't have headers, let's try without first
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to retrieve the page from {site}.")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        products = []

        if site == "ebay":
            listings = soup.select('.s-item')
            print(f"Found {len(listings)} items on eBay")
            for listing in listings[:5]: # Check first 5
                name = listing.select_one('.s-item__title')
                price = listing.select_one('.s-item__price')
                if name and price:
                    print(f"Found: {name.text.strip()} - {price.text.strip()}")
                    products.append(name.text.strip())

        elif site == "walmart":
            # Walmart class names change frequently, user's selectors might be old
            listings = soup.select('.search-result-gridview-item')
            print(f"Found {len(listings)} items on Walmart")
            
    except Exception as e:
        print(f"Error: {e}")

    return products

if __name__ == "__main__":
    scrape_products("laptop", "ebay")
    print("-" * 20)
    scrape_products("laptop", "walmart")
