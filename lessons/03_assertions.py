"""
LESSON 3: Assertions with expect()

This is the single most important concept for YOUR use case: expect() is
how Playwright checks "did this actually happen/work" -- which is exactly
what an evaluation harness needs to do to score pass/fail.

Key difference from a plain `if` check: expect() auto-retries for a few
seconds before failing. Web pages update asynchronously (JS renders things
a moment after navigation), so a naive `if page.locator(...).text == "x"`
would often fail due to timing, not because anything is actually wrong.
expect() absorbs that timing noise -- which is also exactly the kind of
flakiness an eval harness needs to be robust to.
"""
from playwright.sync_api import sync_playwright, expect


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://example.com")

        # --- Assertions you'll use constantly ---

        # Page-level
        expect(page).to_have_title("Example Domain")
        expect(page).to_have_url("https://example.com/")

        # Element-level
        heading = page.locator("h1")
        expect(heading).to_be_visible()
        expect(heading).to_have_text("Example Domain")

        link = page.locator("a")
        expect(link).to_be_visible()
        expect(link).to_have_attribute("href", "https://iana.org/domains/example")

        print("All assertions passed.")

        # --- What a FAILING assertion looks like (for learning) ---
        try:
            expect(heading).to_have_text("Wrong Text", timeout=1000)
        except AssertionError as e:
            print("\nExpected failure caught (this is what a failed eval check looks like):")
            print(str(e).splitlines()[0])  # first line only, keep it short

        browser.close()


if __name__ == "__main__":
    main()
