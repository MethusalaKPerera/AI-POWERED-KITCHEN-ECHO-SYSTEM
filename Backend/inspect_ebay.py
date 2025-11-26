from playwright.sync_api import sync_playwright

def inspect_ebay():
    print("Inspecting eBay HTML...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto('https://www.ebay.com/sch/i.html?_nkw=laptop', timeout=15000)
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # Save HTML
            html = page.content()
            with open('ebay_playwright.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            print("Saved HTML to ebay_playwright.html")
            
            # Try to find product containers
            print("\nLooking for product containers...")
            
            # Try different selectors
            selectors_to_try = [
                '.s-item',
                '[class*="s-item"]',
                '.srp-results li',
                'li.s-item',
                '#srp-river-results li',
                '[data-view="mi:1686"]',
                'div.s-item__wrapper'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        
                        # Try to get first item details
                        if len(elements) > 0:
                            first = elements[0]
                            print(f"   First element HTML (first 200 chars): {first.inner_html()[:200]}")
                    else:
                        print(f"❌ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_ebay()
