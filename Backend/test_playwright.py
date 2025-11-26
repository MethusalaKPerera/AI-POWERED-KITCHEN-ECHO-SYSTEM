from playwright.sync_api import sync_playwright
import time

def test_ebay_playwright():
    print("Testing eBay with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://www.ebay.com/sch/i.html?_nkw=laptop', timeout=10000)
            page.wait_for_selector('.s-item', timeout=5000)
            
            items = page.query_selector_all('.s-item')
            print(f"Found {len(items)} items")
            
            # Get first 3 items
            for i, item in enumerate(items[1:4]):  # Skip first (usually header)
                title = item.query_selector('.s-item__title')
                price = item.query_selector('.s-item__price')
                
                if title and price:
                    print(f"\nItem {i+1}:")
                    print(f"  Title: {title.inner_text()}")
                    print(f"  Price: {price.inner_text()}")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_ebay_playwright()
