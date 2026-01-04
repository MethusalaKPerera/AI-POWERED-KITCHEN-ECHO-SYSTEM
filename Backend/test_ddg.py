from duckduckgo_search import DDGS

def test_ddg(query):
    print(f"Searching for '{query}' on DuckDuckGo...")
    try:
        results = DDGS().text(f"{query} site:ebay.com", max_results=5)
        for r in results:
            print(f" - {r['title']}: {r['href']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ddg("laptop")
