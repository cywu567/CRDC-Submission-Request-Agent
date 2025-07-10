import re

def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

def scrape_field_map(form):
    elements = form.query_selector_all("input, textarea, select, div[role='button']")
    field_map = {}

    for el in elements:
        if not el.is_visible():
            continue
        if el.get_attribute("aria-hidden") == "true":
            continue
        if el.get_attribute("tabindex") == "-1":
            continue

        el_id = el.get_attribute("id")
        el_name = el.get_attribute("name")
        el_placeholder = el.get_attribute("placeholder")
        el_tag = el.evaluate("el => el.tagName").lower()
        el_role = el.get_attribute("role")
        is_dropdown = el_tag == "div" and el_role == "button" and el.get_attribute("aria-haspopup") == "listbox"

        label_text = ""
        if el_id:
            label_el = form.query_selector(f"label[for='{el_id}']")
            if label_el:
                label_text = label_el.inner_text().strip()

        if not label_text:
            if el_name:
                label_text = el_name
            elif el_placeholder:
                label_text = el_placeholder
            elif el_id and not el_id.startswith(":r"):
                label_text = el_id
            else:
                continue

        norm_label = normalize(label_text)
        entry = (el, "select" if is_dropdown else "input")
        field_map.setdefault(norm_label, []).append(entry)

    return field_map


def fill_field_by_label(page, label_text, value):
    try:
        form = page.query_selector_all("form")[0]
        field_map = scrape_field_map(form)
        norm_key = normalize(label_text)

        if norm_key in field_map:
            for el, kind in field_map[norm_key]:
                if kind == "input":
                    el.fill(str(value))
                    return
        print(f"[fill_field_by_label] No input field matched label: {label_text}")
    except Exception as e:
        print(f"[fill_field_by_label] Error for label '{label_text}': {e}")



def fill_dropdown_by_label(page, label_text, option_text):
    try:
        # Try finding dropdown by label proximity
        dropdown_button = page.query_selector(f"text={label_text} >> xpath=.. >> xpath=.//*[contains(@role, 'button')]")
        if not dropdown_button:
            # Fallback to aria-label search
            dropdown_button = page.query_selector(f"[role='button'][aria-label='{label_text}']")

        if not dropdown_button:
            print(f"[fill_dropdown_by_label] Dropdown not found for label: {label_text}")
            return

        dropdown_button.click()
        page.wait_for_timeout(300)

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
            if opt.inner_text().strip() == option_text:
                opt.click()
                return

        print(f"[fill_dropdown_by_label] Option '{option_text}' not found for '{label_text}'")
    except Exception as e:
        print(f"[fill_dropdown_by_label] Error for label '{label_text}': {e}")


def check_checkbox_by_label(page, label_text):
    try:
        form = page.query_selector_all("form")[0]
        field_map = scrape_field_map(form)
        norm_key = normalize(label_text)

        for el in form.query_selector_all("input[type='checkbox']"):
            container = el.evaluate_handle("el => el.closest('div')")
            if container and normalize(container.inner_text()) == norm_key:
                el.check()
                return
        print(f"[check_checkbox_by_label] No checkbox matched label: {label_text}")
    except Exception as e:
        print(f"[check_checkbox_by_label] Error for '{label_text}': {e}")

def check_switch_by_label(page, label_text):
    print("label_text", label_text)
    try:
        norm_target = normalize(label_text)
        label_els = page.query_selector_all("label")

        for label_el in label_els:
            text = label_el.inner_text().strip()
            if normalize(text) == norm_target:
                label_el.click()
                print(f"[check_switch_by_label] Clicked label to toggle switch: {text}")
                return

        print(f"[check_switch_by_label] No matching <label> found for: {label_text}")
    except Exception as e:
        print(f"[check_switch_by_label] Error for label '{label_text}': {e}")



#def check_radio_by_label(page, label_text, value_text):
#    try:
#        form = page.query_selector_all("form")[0]
#        norm_label = normalize(label_text)
#        norm_value = normalize(value_text)

#        radios = form.query_selector_all("input[type='radio']")
#        for radio in radios:
#            value = radio.get_attribute("value") or ""
#            parent_text = radio.evaluate("el => el.closest('div')?.innerText || ''")
#            if norm_label in normalize(parent_text) and norm_value in normalize(value):
#                radio.check()
#                print(f"[check_radio_by_label] Checked '{value_text}' for '{label_text}'")
#                return

#        print(f"[check_radio_by_label] No match for '{label_text}' = '{value_text}'")
#    except Exception as e:
#        print(f"[check_radio_by_label] Error for '{label_text}': {e}")
def check_radio_by_id(page, radio_id):
    try:
        radio = page.query_selector(f"input[type='radio']#{radio_id}")
        if radio:
            radio.check()
            print(f"[check_radio_by_id] Checked radio with id: {radio_id}")
        else:
            print(f"[check_radio_by_id] No radio found with id: {radio_id}")
    except Exception as e:
        print(f"[check_radio_by_id] Error checking radio with id '{radio_id}': {e}")


        
        
def fill_rest_form(page):
    #fill_dropdown_by_label(page, "Program", "test star (TEST)")

    #fill_field_by_label(page, "Study Title", "Lung Cancer RNA Study")
    #fill_field_by_label(page, "Study Abbreviation", "LCRS")
    #fill_field_by_label(page, "Study Description", "This study analyzes RNA data from lung cancer patients to identify biomarkers.")

    #fill_field_by_label(page, "Funding Agency/Organization", "National Cancer Institute (NCI)")
    #fill_field_by_label(page, "Grant or Contract Number(s)", "CA123456")
    #fill_field_by_label(page, "NCI Program Officer", "Dr. Jane Smith")
    #fill_field_by_label(page, "NCI Genomic Program Administrator", "Dr. Alan Brown")
    
    #next_button = page.query_selector("button:has-text('Next')")
    #next_button.click()
    #page.wait_for_timeout(1000)

    check_checkbox_by_label(page, "Controlled Access")
    check_switch_by_label(page, "Has your study been registered in dbGaP?")
    fill_field_by_label(page, "If yes, provide dbGaP PHS number with the version number", "phs002529.v1.p1")

    #fill_dropdown_by_label(page, "Cancer types (select all that apply)", "Lung")
    fill_field_by_label(page, "Pre-Cancer types (provide all that apply)", "Atypical Hyperplasia")

    fill_dropdown_by_label(page, "Species of subjects", "Homo sapiens")
    fill_field_by_label(page, "Number of subjects included in the submission", "42")

    next_button = page.query_selector("button:has-text('Next')")
    next_button.click()
    page.wait_for_timeout(1000)
    
    fill_field_by_label(page, "Targeted Data Submission Delivery Date", "07/15/2025")
    fill_field_by_label(page, "Expected Publication Date", "08/01/2025")

    #check_switch_by_label(page, "Clinical")
    check_switch_by_label(page, "Genomics")
    #check_switch_by_label(page, "Imaging")
    check_switch_by_label(page, "Proteomics")

    fill_field_by_label(page, "Other Data Type(s)", "Epigenetics")

    file_inputs = page.query_selector_all("tr input")
    if len(file_inputs) >= 4:
        file_inputs[0].fill("FASTQ")
        file_inputs[1].fill(".fq")
        file_inputs[2].fill("10")
        file_inputs[3].fill("50 GB")
    else:
        print("[file table] Could not find all 4 inputs for file row.")

    check_radio_by_id(page, "section-d-data-de-identified-yes-radio-button")

    check_checkbox_by_label(page, "Cell lines")
    fill_field_by_label(page, "Additional Comments or Information about this submission", "Test data only.")


    #save_button = page.query_selector("button:has-text('Save')")
    #save_button.click()
    #next_button = page.query_selector("button:has-text('Next')")
    #next_button.click()
    #page.wait_for_timeout(1000)
    #submit_button = page.query_selector("button:has-text('Submit')")
    #submit_button.click()
    #submit_button = page.query_selector("button:has-text('Confirm to Submit')")
    #submit_button.click()
    
    
    
    
