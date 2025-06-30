from playwright.sync_api import sync_playwright

_playwright = None
_browser = None
_context = None
_page = None

def get_browser_session():
    global _playwright, _browser, _context, _page
    if _page is not None:
        return _browser, _context, _page

    _playwright = sync_playwright().start()
    _browser = _playwright.chromium.launch(headless=False)  # or True for headless
    _context = _browser.new_context()
    _page = _context.new_page()
    return _browser, _context, _page
