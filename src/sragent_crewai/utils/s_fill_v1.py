#from sragent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
#from faker import Faker
#import re
#import json

#def normalize(text):
#    return re.sub(r'[^a-z0-9]', '', text.lower())

#def get_dropdown_options(page, label):
#    try:
#        # Click the dropdown element to load the options
#        dropdown_el = page.query_selector(f"label:has-text('{label}') + * [role='button']")
#        if dropdown_el:
#            dropdown_el.click()
#            page.wait_for_timeout(500)
#            options = page.query_selector_all("[role='option']")
#            return [opt.inner_text().strip() for opt in options]
#    except:
#        pass
#    return []

#def handle_dropdown(page, el, label_text, decision_tool):
#    try:
#        el.click()
#        page.wait_for_timeout(300)  # Let animation finish

#        # Wait for the dropdown menu to be present
#        page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)

#        options = page.query_selector_all("[role='presentation'] [role='option']")
#        options = [opt for opt in options if opt.is_visible()]
#        option_texts = [opt.inner_text().strip() for opt in options]

#        if not option_texts:
#            print(f"[handle_dropdown] No options found for {label_text}")
#            return False

#        # Let Bedrock pick the right option
#        chosen = decision_tool._run(
#            goal=f"Choose an option for '{label_text}'", options=option_texts
#        )
#        print("chosen", chosen)

#        for opt in options:
#            text = opt.inner_text().strip()
#            if normalize(chosen) in normalize(text):
#                print(f"[handle_dropdown] Clicking option: {text}")
#                # Scroll into view and force click via JS
#                page.evaluate("""
#                    el => {
#                        el.scrollIntoView({ behavior: 'instant', block: 'center' });
#                        el.click();
#                    }
#                """, opt)
#                page.wait_for_timeout(300)
#                return True

#        print(f"[handle_dropdown] No matching option for '{chosen}' in {label_text}")
#    except Exception as e:
#        print(f"[handle_dropdown] Error handling dropdown '{label_text}': {e}")
#    return False

##def handle_dropdown(page, el, label_text, decision_tool):
##    try:
##        # Open the dropdown
##        page.evaluate("el => el.click()", el)
##        page.wait_for_selector("[role='presentation'] [role='option']", timeout=3000)

##        # Refresh option handles after opening the menu
##        options = page.query_selector_all("[role='presentation'] [role='option']")
##        visible_options = [opt for opt in options if opt.is_visible()]
##        option_texts = [opt.inner_text().strip() for opt in visible_options]

##        if not option_texts:
##            print(f"[handle_dropdown] No options found for {label_text}")
##            return False

##        # Ask Bedrock to choose
##        chosen = decision_tool._run(
##            goal=f"Choose an option for '{label_text}'", options=option_texts
##        )

##        # Find and click matching option
##        for opt in visible_options:
##            text = opt.inner_text().strip()
##            if normalize(chosen) in normalize(text):
##                # Get coordinates and click precisely
##                box = opt.bounding_box()
##                if box:
##                    page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
##                    page.wait_for_timeout(300)
##                    return True
##                else:
##                    print(f"[handle_dropdown] Couldn't get bounding box for '{text}'")
##                    return False

##        print(f"[handle_dropdown] No matching option for '{chosen}' in {label_text}")
##    except Exception as e:
##        print(f"[handle_dropdown] Error handling dropdown '{label_text}': {e}")
##    return False



#def smart_fill(page, goal: str = "Fill out the form as reasonably as possible"):
#    fake = Faker()
#    decision_tool = BedrockDecisionTool()
    
#    page.wait_for_timeout(1000)
#    form = page.query_selector_all("form")[0]
    
#    elements = form.query_selector_all("input, textarea, select, div[role='button']")
#    field_info = []
#    field_map = {}

#    for el in elements:
#        if not el.is_visible():
#            continue
#        if el.get_attribute("aria-hidden") == "true":
#            continue
#        if el.get_attribute("tabindex") == "-1":
#            continue

#        el_id = el.get_attribute("id")
#        el_name = el.get_attribute("name")
#        el_placeholder = el.get_attribute("placeholder")
#        el_type = el.get_attribute("type")
#        el_tag = el.evaluate("el => el.tagName").lower()
#        el_role = el.get_attribute("role")
#        is_dropdown = el_tag == "div" and el_role == "button" and el.get_attribute("aria-haspopup") == "listbox"

#        # Try to get associated label
#        label_text = ""
#        if el_id:
#            label_el = form.query_selector(f"label[for='{el_id}']")
#            if label_el:
#                label_text = label_el.inner_text().strip()

#        if not label_text:
#            if el_name:
#                label_text = el_name
#            elif el_placeholder:
#                label_text = el_placeholder
#            elif el_id and not el_id.startswith(":r"):
#                label_text = el_id
#            else:
#                continue

#        field_info.append({
#            "label": label_text,
#            "name": el_name,
#            "placeholder": el_placeholder,
#            "type": el_type,
#            "tag": el_tag,
#            "kind": "select" if is_dropdown else "input"
#        })

#        norm_label = normalize(label_text)
#        norm_name = normalize(el_name) if el_name else None

#        entry = (el, "select" if is_dropdown else "input")

#        if norm_label:
#            field_map.setdefault(norm_label, []).append(entry)
#        if norm_name:
#            field_map.setdefault(norm_name, []).append(entry)

#    if not field_info:
#        return "No usable fields found."

#    # Prompt
#    field_descriptions = "\n".join([
#        f"- Label: {f['label']}\n  Tag: {f['tag']}\n  Name: {f['name']}\n  Options: {get_dropdown_options(page, f['label']) if f['kind'] == 'select' else 'N/A'}"
#        for f in field_info
#    ])


#    prompt = f"""
#    You are filling out a web form with the goal: "{goal}".

#    Here are the fields and their details:
#    {field_descriptions}

#    If a field has options, choose one that makes sense. 
#    Return only a valid JSON object where each key is the name of the field, and the value is the chosen or generated input.
#    """

#    response = decision_tool._run(
#        goal=goal,
#        options=[f"{f['label']} ({f['tag']})" for f in field_info],
#        custom_prompt=prompt,
#        max_tokens=300
#    )

#    try:
#        json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
#        answers = json.loads(json_str)
#    except Exception:
#        return f"Failed to parse AI response:\n{response}"

#    filled = 0
#    for label, value in answers.items():
#        norm_key = normalize(label)
#        if norm_key in field_map:
#            for el, kind in field_map[norm_key]:
#                try:
#                    if kind == "input":
#                        el.fill(str(value))
#                    elif kind == "select":
#                        if handle_dropdown(page, el, label, decision_tool):
#                            filled += 1
#                            break
#                        else:
#                            print(f"[smart_fill] No dropdown option matched '{value}' for '{label}'")
#                            continue
#                    filled += 1
#                    break
#                except Exception as e:
#                    print(f"[smart_fill] Could not fill '{label}': {e}")
#        else:
#            print(f"[smart_fill] No matching element for '{label}'")

#    return f"Filled {filled} fields based on AI reasoning."