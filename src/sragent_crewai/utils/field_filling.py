from sragent_crewai.utils.form_scraping import normalize

def fill_text_field(el, value):
    try:
        if el.is_disabled() or not el.is_enabled():
            print(f"[fill_text_field] Skipping disabled input: {el}")
            return
        if el.evaluate("el => el.readOnly || el.hasAttribute('readonly')"):
            print(f"[fill_text_field] Skipping readonly input: {el}")
            return
        el.fill(str(value))
    except Exception as e:
        print(f"[fill_text_field] Error filling field: {e}")




def handle_dropdown(page, el, label_text, chosen):
    try:
        el.click()
        page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)

        # Remove Material UI backdrops if present
        page.evaluate("""
            () => {
                const backdrops = document.querySelectorAll('.MuiBackdrop-root');
                for (const b of backdrops) {
                    b.style.setProperty('display', 'none', 'important');
                }
            }
        """)

        options = page.query_selector_all("[role='presentation'] [role='option']")
        for opt in options:
            text = opt.inner_text().strip()
            if normalize(chosen) == normalize(text):
                print(f"[handle_dropdown] Selecting: {text}")
                opt.click()
                return True

        print(f"[handle_dropdown] Option '{chosen}' not found for label '{label_text}'")
    except Exception as e:
        print(f"[handle_dropdown] Error for '{label_text}': {e}")
    return False


def check_checkbox(el, should_check: bool):
    try:
        if should_check:
            el.check()
    except Exception as e:
        print(f"[check_checkbox] Failed to set checkbox: {e}")

