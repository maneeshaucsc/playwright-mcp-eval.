"""
LESSON 4: Screenshots and tracing

For an evaluation harness, a numeric pass/fail score is often not enough --
when a task fails, you want EVIDENCE you can look at to understand why.
Screenshots and traces are how Playwright gives you that.

- Screenshot: a single image, cheap, good for "attach to the eval report."
- Trace: a full recording (DOM snapshots, network, console, actions) you
  can step through afterwards in a visual viewer -- like a flight recorder
  for the whole run. Invaluable when debugging why an agent's task failed.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).parent / "artifacts"


def main():
    OUT_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # start_chunks=True lets you save multiple named trace segments;
        # for a simple case, just start/stop once per run.
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()
        page.goto("https://example.com")
        page.screenshot(path=str(OUT_DIR / "example_page.png"))
        print(f"Screenshot saved -> {OUT_DIR / 'example_page.png'}")

        page.goto("https://playwright.dev")
        page.screenshot(path=str(OUT_DIR / "playwright_dev.png"), full_page=True)
        print(f"Full-page screenshot saved -> {OUT_DIR / 'playwright_dev.png'}")

        context.tracing.stop(path=str(OUT_DIR / "trace.zip"))
        print(f"Trace saved -> {OUT_DIR / 'trace.zip'}")
        print("View it with:  playwright show-trace artifacts/trace.zip")

        browser.close()


if __name__ == "__main__":
    main()
