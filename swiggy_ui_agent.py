from playwright.sync_api import sync_playwright
import time
import re

SWIGGY_URL = "https://www.swiggy.com"


def search_swiggy(query):
    results = []

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="./swiggy_profile",
            headless=False,
            viewport=None,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            args=["--start-maximized"],
        )

        page = context.new_page()

        # Stealth fix
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

        context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
        })

        print("🌐 Opening Swiggy...")
        page.goto(SWIGGY_URL, timeout=60000)
        page.wait_for_timeout(8000)

        print("📍 Closing location dropdown if open...")
        page.keyboard.press("Escape")
        page.wait_for_timeout(2000)

        print("🔎 Waiting for search container...")
        page.wait_for_selector("text=Search for restaurant", timeout=20000)

        print("🖱 Clicking search container...")
        page.locator("text=Search for restaurant").first.click()
        page.wait_for_timeout(2000)

        print("⌨ Waiting for actual search input...")
        search_input = page.locator("input[placeholder*='Search']")
        search_input.wait_for(timeout=20000)

        print(f"⌨ Typing query: {query}")
        search_input.fill(query)
        page.keyboard.press("Enter")

        print("⏳ Waiting for dish results...")
        page.wait_for_selector("div[data-testid='normal-dish-item']", timeout=20000)

        print("📦 Collecting dish cards...")

        dish_cards = page.locator("div[data-testid='normal-dish-item']")
        count = min(dish_cards.count(), 5)

        print(f"Found {count} dishes")

        for i in range(count):
            try:
                card = dish_cards.nth(i)

                lines = [
                    l.strip()
                    for l in card.inner_text().split("\n")
                    if l.strip()
                ]

                dish_name = lines[1] if len(lines) > 1 else "Unknown Dish"

                price_number = 0
                if len(lines) > 2 and lines[2].isdigit():
                    price_number = int(lines[2])

                # 🔥 GO UP to restaurant container
                restaurant_container = card.locator(
                    "xpath=ancestor::div[@data-testid='search-pl-dish-first-v2-card']"
                ).first

                restaurant_name = "Unknown"
                rating_value = 0.0

                try:
                    header_text = restaurant_container.inner_text()

                    # Extract restaurant name
                    for line in header_text.split("\n"):
                        if line.startswith("By "):
                            restaurant_name = line.replace("By ", "").strip()

                    # Extract rating
                    import re
                    match = re.search(r"\b\d\.\d\b", header_text)
                    if match:
                        rating_value = float(match.group())

                except:
                    pass

                results.append({
                    "restaurant": restaurant_name,
                    "dish": dish_name,
                    "rating": rating_value,
                    "price": price_number,
                    "veg": "veg item" in lines[0].lower()
                })

            except Exception as e:
                print("⚠ Skipping card:", e)
        print("⏳ Keeping browser open for 3 seconds...")
        time.sleep(3)

        context.close()

    return results