from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()

    page.goto("https://playwright.dev")

    page.get_by_role("button", name="Search").click()
    page.get_by_placeholder("Search docs").fill("locators")
    page.keyboard.press("Enter")

    page.wait_for_timeout(1500)
    print("URL after search:", page.url)

    browser.close()