from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True)

    page = context.new_page()
    page.goto("https://example.com")
    page.screenshot(path="example.png")
    print("Screenshot saved.")

    context.tracing.stop(path="trace.zip")
    print("Trace saved.")

    browser.close()