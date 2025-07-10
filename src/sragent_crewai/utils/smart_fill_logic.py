import json
import re
from sragent_crewai.utils.form_scraping import scrape_elements, normalize
from sragent_crewai.utils.field_filling import fill_text_field, handle_dropdown, check_checkbox
from sragent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
from sragent_crewai.utils.log_utils import log_fill_section


def smart_fill_section(page, goal="Fill out the form as reasonably as possible"):
    filled_keys = set()
    filled = 0
    max_passes = 3
    field_logs = []

    for attempt in range(max_passes):
        print(f"\n[smart_fill_section] Pass {attempt + 1}")
        field_info, _ = scrape_elements(page)

        field_map = {}
        for f in field_info:
            norm_key = normalize(f["full_key"])
            if norm_key in filled_keys:
                continue
            field_map.setdefault(norm_key, []).append((f['element'], f['kind']))

        # Rebuild LLM prompt with unfilled fields only
        field_descriptions = []
        for f in field_info:
            if normalize(f["full_key"]) in filled_keys:
                continue
            desc = f"- Field: {f['full_key']} | Type: {f['kind']}"
            if f["kind"] == "select" and f.get("options"):
                desc += f" | Options: {f['options']}"
            field_descriptions.append(desc)

        if not field_descriptions:
            break

        prompt = f"""
You are filling out a web form with the goal: "{goal}".

Here are the fields and their details:
{chr(10).join(field_descriptions)}

Return a valid JSON object where each key is the field's label and context, like:
{{ "First name (primaryContact)": "Alice", "Email (pi)": "alice@example.com" }}
"""

        decision_tool = BedrockDecisionTool()
        options = [f['full_key'] for f in field_info]
        response = decision_tool._run(goal=goal, options=options, custom_prompt=prompt, max_tokens=300)

        try:
            json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
            answers = json.loads(json_str)
        except Exception:
            return f"Failed to parse AI response:\n{response}"

        for full_label, value in answers.items():
            norm_key = normalize(full_label)
            if norm_key in filled_keys:
                continue

            entries = field_map.get(norm_key)
            if not entries:
                field_logs.append({"label": full_label, "value": value, "status": "not_found"})
                continue

            filled_successfully = False

            for el, kind in entries:
                try:
                    if kind == "input":
                        fill_text_field(el, value)
                        filled_keys.add(norm_key)
                        filled += 1
                        field_logs.append({"label": full_label, "value": value, "status": "success"})
                        filled_successfully = True
                        break

                    elif kind == "select":
                        values = value if isinstance(value, list) else [value]
                        for v in values:
                            if isinstance(v, dict):
                                v = v.get("name") or next(iter(v.values()), None)
                            if handle_dropdown(page, el, full_label, v):
                                filled_keys.add(norm_key)
                                filled += 1
                                field_logs.append({"label": full_label, "value": v, "status": "success"})
                                filled_successfully = True
                                break

                    elif kind == "checkbox":
                        should_check = str(value).strip().lower() in {"yes", "true", "1", "checked"}
                        check_checkbox(el, should_check)
                        filled_keys.add(norm_key)
                        filled += 1
                        field_logs.append({"label": full_label, "value": should_check, "status": "success"})
                        filled_successfully = True
                        break

                except Exception as e:
                    field_logs.append({
                        "label": full_label,
                        "value": value,
                        "status": "error",
                        "error": str(e)
                    })

            if not filled_successfully:
                field_logs.append({"label": full_label, "value": value, "status": "skipped"})

    result = f"Filled {filled} fields across {len(filled_keys)} unique keys"

    log_fill_section(
        tool="smart_fill_section",
        goal=goal,
        section_number=1,  # Replace if tracking section numbers
        fields_filled=field_logs,
        status="success" if filled > 0 else "no_fields_filled"
    )

    return result
