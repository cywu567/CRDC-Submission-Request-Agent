
from sragent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
from faker import Faker
import json

def smart_fill(page, goal: str = "Fill out the form as reasonably as possible"):
    fake = Faker()
    decision_tool = BedrockDecisionTool()
    
    forms = page.query_selector_all("form")
    print(f"Found {len(forms)} forms")
    for i, f in enumerate(forms):
        print(f"\nForm {i} outer HTML:\n", f.evaluate("el => el.outerHTML"))
    
    form = None
    for f in page.query_selector_all("form"):
        fid = f.get_attribute("id")
        if fid == ":r18":
            form = f
            break

    if not form:
        return "Could not locate the Principal Investigator form."
    elements = form.query_selector_all("input, textarea, select")
    field_info = []
    field_map = {}

    for el in elements:
        if not el.is_visible():
            continue

        el_id = el.get_attribute("id")
        el_name = el.get_attribute("name")
        el_placeholder = el.get_attribute("placeholder")
        el_type = el.get_attribute("type")
        el_tag = el.evaluate("el => el.tagName").lower()

        # Try to get associated label
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
            
        key = f"{label_text} ({el_tag})"
        field_info.append({
            "label": label_text,
            "name": el_name,
            "placeholder": el_placeholder,
            "type": el_type,
            "tag": el_tag
        })
        field_map[key.lower()] = el

    if not field_info:
        return "No usable fields found."

    # Construct prompt for Bedrock
    field_descriptions = "\n".join([
        f"- Label: {f['label']}\n  Tag: {f['tag']}\n  Name: {f['name']}\n  Placeholder: {f['placeholder']}\n  Type: {f['type']}"
        for f in field_info
    ])
    prompt = f"""
You are filling out a web form with the goal: "{goal}".

Here are the fields:
{field_descriptions}

Return only a valid JSON object mapping each field label to a realistic value.
Example:
{{
  "First name (input)": "Alice",
  "Date of birth (input)": "01/01/2000",
  "State (select)": "California"
}}
"""

    response = decision_tool._run(
        goal=goal,
        options=[f"{f['label']} ({f['tag']})" for f in field_info],
        custom_prompt=prompt,
        max_tokens=300
    )

    try:
        answers = json.loads(response)
    except Exception:
        return f"Failed to parse AI response:\n{response}"

    filled = 0
    for label, value in answers.items():
        lower_label = label.lower()
        if lower_label in field_map:
            try:
                field_map[lower_label].fill(str(value))
                filled += 1
            except Exception as e:
                print(f"[smart_fill] Could not fill '{{label}}': {{e}}")
        else:
            print(f"[smart_fill] No matching element for '{{label}}'")

    return f"Filled {{filled}} fields based on AI reasoning."
