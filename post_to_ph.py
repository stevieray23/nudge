from playwright.sync_api import sync_playwright

errors = []

def run():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False, args=['--disable-blink-features=AvoidRendererProcessLimit'])
    ctx = browser.new_context()
    page = ctx.new_page()

    try:
        print("Opening Product Hunt...")
        page.goto("https://www.producthunt.com", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=20000)
        print("Looking for sign in button...")
        page.screenshot(path="C:/Users/steph/.qclaw-oversea/workspace/projects/chase/ph_home.png", fullPage=False)
        print("Screenshot saved.")
    except Exception as e:
        print(f"Error: {e}")
        errors.append(str(e))
    finally:
        browser.close()
        pw.stop()

if __name__ == "__main__":
    run()
    if errors:
        print("Errors:", errors)
