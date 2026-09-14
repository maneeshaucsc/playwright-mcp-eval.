"""
LESSON 1: Launching a browser and navigating

Playwright's core objects, from outside in:
  Playwright  -> launches a  Browser  -> which opens a  BrowserContext
  (an isolated session, like a private window) -> which opens  Page(s)
  (an actual tab).

Why the extra "context" layer exists: it lets you run many isolated
sessions (different cookies/storage) from ONE browser process. In an eval
harness this matters a lot — you can run many agent "sessions" in
parallel without them polluting each other's state.
"""
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        # headless=False pops open a visible browser window so you can watch.
        # In real eval/test runs you'd normally use headless=True (faster, no UI).
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://example.com")
        print("Page title:", page.title())
        print("Page URL:", page.url)

        # grab some visible text
        heading = page.locator("h1").text_content()
        print("H1 text:", heading)

        page.wait_for_timeout(2000)  # just so you can see it before it closes
        browser.close()


if __name__ == "__main__":
    main()
