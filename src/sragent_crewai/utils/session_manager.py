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
    _browser = _playwright.chromium.launch(headless=True)  # or True for headless
    _context = _browser.new_context()
    _page = _context.new_page()
    return _browser, _context, _page

def get_page():
    return get_browser_session()[2]

def set_page(page):
    global _page
    _page = page
    
    

#from playwright.async_api import async_playwright

#_playwright = None
#_browser = None
#_context = None
#_page = None

#async def get_browser_session():
#    global _playwright, _browser, _context, _page
#    if _page is not None:
#        return _browser, _context, _page

#    _playwright = await async_playwright().start()
#    _browser = await _playwright.chromium.launch(headless=False)
#    _context = await _browser.new_context()
#    _page = await _context.new_page()
#    return _browser, _context, _page

#async def get_page():
#    return (await get_browser_session())[2]

#def set_page(page):
#    global _page
#    _page = page