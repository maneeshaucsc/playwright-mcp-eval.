"""
LESSON 2: Locators and actions

A Locator describes HOW to find an element -- it's lazy (doesn't search the
page until you act on it), and Playwright automatically re-finds it and
retries if the page is still loading/changing. This "auto-wait" is the
single biggest difference from older tools like Selenium, where you had to
manually write wait/retry logic.

Preferred locator strategies, in order of robustness:
  1. get_by_role()   - how a screen reader would find it (best: mirrors how
                        an AI agent "sees" a page via its accessibility tree)
  2. get_by_label()  - form fields, by their label text
  3. get_by_text()   - visible text
  4. get_by_test_id() - a data-testid attribute (best when devs add them)
  CSS/XPath selectors are a last resort -- brittle, break on redesigns.
"""
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=400)
        page = browser.new_page()

        # Playwright's own site has a search box -- a realistic target to practice on.
        page.goto("https://playwright.dev")

        # get_by_role is the recommended default: it finds elements the way
        # assistive tech (and, relevantly for you, browser-using AI agents) does.
        search_button = page.get_by_role("button", name="Search")
        search_button.click()

        search_box = page.get_by_placeholder("Search docs")
        search_box.fill("locators")

        # press a key
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)

        print("Current URL after search:", page.url)

        browser.close()


if __name__ == "__main__":
    main()
