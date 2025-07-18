import re

def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower().strip()) if text else ''

def extract_context(el):
    context = None
    try:
        current = el
        for _ in range(3):
            current = current.evaluate_handle("el => el.closest('fieldset, section, div')")
            if not current:
                break
            inner = current.inner_text().strip()
            lines = [line.strip() for line in inner.split("\n") if line.strip()]
            if lines:
                first = lines[0].strip()
                if normalize(first) not in {"firstname", "lastname", "email", "position"} and not re.match(r'^[\u200b\s]*$', first):
                    context = first
                    break
    except Exception as e:
        print(f"[extract_context] Error climbing DOM: {e}")

    if not context:
        try:
            name_attr = el.get_attribute("name")
            if name_attr and "[" in name_attr:
                context = name_attr.split("[")[0]
        except Exception as e:
            print(f"[extract_context] Error in name-based fallback: {e}")

    return context

def scrape_elements(page):
    page.wait_for_timeout(1000)
    form_elements = page.query_selector_all("form")
    if not form_elements:
        print("[scrape_elements] No <form> tags found on the page.")
        return [], {}

    form = max(form_elements, key=lambda f: len(f.query_selector_all("input, textarea, select, div[role='button']")))
    elements = form.query_selector_all("input, textarea, select, div[role='button']")

    field_info = []
    field_map = {}

    for el in elements:
        try:
            if not el.is_visible():
                continue
            if el.get_attribute("aria-hidden") == "true":
                continue
            if el.get_attribute("tabindex") == "-1":
                continue

            el_id = el.get_attribute("id")
            el_name = el.get_attribute("name")
            el_placeholder = el.get_attribute("placeholder")
            el_type = el.get_attribute("type")
            el_tag = el.evaluate("el => el.tagName").lower()
            el_role = el.get_attribute("role")
            is_dropdown = el_tag == "div" and el_role == "button" and el.get_attribute("aria-haspopup") == "listbox"
            is_checkbox = el_tag == "input" and el_type == "checkbox"


            # Detect label
            label_text = ""
            if el_id:
                label_el = form.query_selector(f"label[for='{el_id}']")
                if label_el:
                    label_text = label_el.inner_text().strip()

            if not label_text:
                if is_checkbox:
                    container = el.evaluate_handle("el => el.closest('div')")
                    if container:
                        label_text = container.inner_text().strip()
                elif el_name:
                    label_text = el_name
                elif el_placeholder:
                    label_text = el_placeholder
                elif el_id and not el_id.startswith(":r"):
                    label_text = el_id
                else:
                    continue

            # Avoid scraping context from selected dropdown value
            raw_context = extract_context(el)
            context_text = None if is_dropdown and raw_context in (el.inner_text().strip(), el.get_attribute("value")) else raw_context

            if is_checkbox:
                kind = "checkbox"
            elif is_dropdown:
                kind = "select"
            else:
                kind = "input"


            # Build full_key without repeating label as context
            if context_text and normalize(context_text) != normalize(label_text):
                full_key = f"{label_text} ({context_text})"
            else:
                full_key = label_text

            norm_key = normalize(full_key)


            options = None
            if is_dropdown:
                try:
                    el.click()
                    page.wait_for_timeout(300)
                    page.evaluate("""
                        () => {
                            const backdrops = document.querySelectorAll('.MuiBackdrop-root');
                            for (const b of backdrops) {
                                b.style.setProperty('display', 'none', 'important');
                            }
                        }
                    """)
                    page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)
                    option_els = page.query_selector_all("[role='presentation'] [role='option']")
                    options = [opt.inner_text().strip() for opt in option_els if opt.is_visible()]
                    page.keyboard.press("Escape")
                    print(f"[scrape_elements] Dropdown '{label_text}' options: {options}")
                except Exception as e:
                    print(f"[scrape_elements] Could not scrape options for dropdown '{label_text}': {e}")

            print(f"[scrape_elements] Label: '{label_text}' | Context: '{context_text}' | Normalized Key: '{norm_key}'")

            field_map.setdefault(norm_key, []).append((el, kind))

            field_info.append({
                "label": label_text,
                "context": context_text,
                "kind": kind,
                "tag": el_tag,
                "name": el_name,
                "element": el,
                "options": options if is_dropdown else None,
                "full_key": full_key
            })
        except Exception as e:
            print(f"[scrape_elements] Error processing element: {e}")

    return field_info, field_map


#import re

#def normalize(text):
#    return re.sub(r'[^a-z0-9]', '', text.lower().strip()) if text else ''

#async def extract_context(el):
#    context = None
#    try:
#        current = el
#        for _ in range(3):
#            current = await current.evaluate_handle("el => el.closest('fieldset, section, div')")
#            if not current:
#                break
#            inner = (await current.inner_text()).strip()
#            lines = [line.strip() for line in inner.split("\n") if line.strip()]
#            if lines:
#                first = lines[0].strip()
#                if normalize(first) not in {"firstname", "lastname", "email", "position"} and not re.match(r'^[\u200b\s]*$', first):
#                    context = first
#                    break
#    except Exception as e:
#        print(f"[extract_context] Error climbing DOM: {e}")

#    if not context:
#        try:
#            name_attr = await el.get_attribute("name")
#            if name_attr and "[" in name_attr:
#                context = name_attr.split("[")[0]
#        except Exception as e:
#            print(f"[extract_context] Error in name-based fallback: {e}")

#    return context


#async def scrape_elements(page):
#    await page.wait_for_timeout(1000)
#    form_elements = await page.query_selector_all("form")
#    if not form_elements:
#        print("[scrape_elements] No <form> tags found on the page.")
#        return [], {}

#    form = max(
#        form_elements,
#        key=lambda f: len(f.query_selector_all("input, textarea, select, div[role='button']"))
#    )
#    elements = await form.query_selector_all("input, textarea, select, div[role='button']")

#    field_info = []
#    field_map = {}

#    for el in elements:
#        try:
#            if not await el.is_visible():
#                continue
#            if await el.get_attribute("aria-hidden") == "true":
#                continue
#            if await el.get_attribute("tabindex") == "-1":
#                continue

#            el_id = await el.get_attribute("id")
#            el_name = await el.get_attribute("name")
#            el_placeholder = await el.get_attribute("placeholder")
#            el_type = await el.get_attribute("type")
#            el_tag = (await el.evaluate("el => el.tagName")).lower()
#            el_role = await el.get_attribute("role")
#            is_dropdown = el_tag == "div" and el_role == "button" and await el.get_attribute("aria-haspopup") == "listbox"
#            is_checkbox = el_tag == "input" and el_type == "checkbox"

#            label_text = ""
#            if el_id:
#                label_el = await form.query_selector(f"label[for='{el_id}']")
#                if label_el:
#                    label_text = (await label_el.inner_text()).strip()

#            if not label_text:
#                if is_checkbox:
#                    container = await el.evaluate_handle("el => el.closest('div')")
#                    if container:
#                        label_text = (await container.inner_text()).strip()
#                elif el_name:
#                    label_text = el_name
#                elif el_placeholder:
#                    label_text = el_placeholder
#                elif el_id and not el_id.startswith(":r"):
#                    label_text = el_id
#                else:
#                    continue

#            raw_context = await extract_context(el)
#            el_inner_text = (await el.inner_text()).strip()
#            el_value = await el.get_attribute("value")
#            context_text = None if is_dropdown and raw_context in (el_inner_text, el_value) else raw_context

#            kind = "checkbox" if is_checkbox else "select" if is_dropdown else "input"
#            full_key = f"{label_text} ({context_text})" if context_text and normalize(context_text) != normalize(label_text) else label_text
#            norm_key = normalize(full_key)

#            options = None
#            if is_dropdown:
#                try:
#                    await el.click()
#                    await page.wait_for_timeout(300)
#                    await page.evaluate("""
#                        () => {
#                            const backdrops = document.querySelectorAll('.MuiBackdrop-root');
#                            for (const b of backdrops) {
#                                b.style.setProperty('display', 'none', 'important');
#                            }
#                        }
#                    """)
#                    await page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)
#                    option_els = await page.query_selector_all("[role='presentation'] [role='option']")
#                    options = [await opt.inner_text() for opt in option_els if await opt.is_visible()]
#                    await page.keyboard.press("Escape")
#                    print(f"[scrape_elements] Dropdown '{label_text}' options: {options}")
#                except Exception as e:
#                    print(f"[scrape_elements] Could not scrape options for dropdown '{label_text}': {e}")

#            print(f"[scrape_elements] Label: '{label_text}' | Context: '{context_text}' | Normalized Key: '{norm_key}'")

#            field_map.setdefault(norm_key, []).append((el, kind))
#            field_info.append({
#                "label": label_text,
#                "context": context_text,
#                "kind": kind,
#                "tag": el_tag,
#                "name": el_name,
#                "element": el,
#                "options": options if is_dropdown else None,
#                "full_key": full_key
#            })

#        except Exception as e:
#            print(f"[scrape_elements] Error processing element: {e}")

#    return field_info, field_map
