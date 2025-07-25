import json
import re
from sragent_crewai.utils.form_scraping import scrape_elements, normalize
from sragent_crewai.utils.field_filling import fill_text_field, handle_dropdown, check_checkbox
from sragent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
from sragent_crewai.utils.log_utils import log_fill_section

def is_blank(value):
    return value is None or str(value).strip() == ""

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

        try:
            response = decision_tool._run(goal=goal, options=options, custom_prompt=prompt, max_tokens=300)
            json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
            answers = json.loads(json_str)
        except Exception as e:
            field_logs.append({
                "label": "bedrock_response",
                "value": response if "response" in locals() else None,
                "status": "bedrock_failure",
                "error": str(e)
            })

            shortened_options = options[:min(3, len(options))]
            fallback_prompt = f"""Goal: {goal}
Options: {shortened_options}
Respond with a valid JSON object like: {{ "field": "value" }}
"""
            try:
                response = decision_tool._run(goal=goal, options=shortened_options, custom_prompt=fallback_prompt)
                json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
                answers = json.loads(json_str)

                field_logs.append({
                    "label": "bedrock_response",
                    "value": response,
                    "status": "recovered",
                    "fix": "used fallback prompt with trimmed options"
                })
            except Exception as retry_error:
                field_logs.append({
                    "label": "bedrock_response",
                    "value": None,
                    "status": "retry_failed",
                    "error": str(retry_error)
                })
                return f"Failed to parse AI response after retry:\n{str(retry_error)}"

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
                        if is_blank(value):
                            field_logs.append({"label": full_label, "value": value, "status": "empty_value"})
                            break
                        fill_text_field(el, value)
                        actual_value = el.input_value()
                        if actual_value != str(value):
                            field_logs.append({
                                "label": full_label,
                                "value": value,
                                "status": "rejected_by_field",
                                "note": f"Field retained: '{actual_value}'"
                            })
                            break
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
                            if is_blank(v):
                                continue
                            if handle_dropdown(page, el, full_label, v):
                                filled_keys.add(norm_key)
                                filled += 1
                                field_logs.append({"label": full_label, "value": v, "status": "success"})
                                filled_successfully = True
                                break

                    elif kind == "checkbox":
                        if is_blank(value):
                            field_logs.append({"label": full_label, "value": value, "status": "empty_value"})
                            break
                        should_check = str(value).strip().lower() in {"yes", "true", "1", "checked"}
                        check_checkbox(el, should_check)
                        checked_state = el.is_checked()
                        if checked_state != should_check:
                            field_logs.append({
                                "label": full_label,
                                "value": should_check,
                                "status": "rejected_by_field",
                                "note": f"Checkbox retained: '{checked_state}'"
                            })
                            break
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

    successful_fills = sum(1 for log in field_logs if log.get("status") == "success")
    incomplete = any(log.get("status") in {"skipped", "rejected_by_field", "empty_value", "error"} for log in field_logs)

    log_fill_section(
        tool="smart_fill_section",
        goal=goal,
        section_number=1,
        fields_filled=field_logs,
        status="success" if successful_fills > 0 and not incomplete else "partial_or_failed"
    )


    return result


#import json
#import re
#from sragent_crewai.utils.form_scraping import scrape_elements, normalize
#from sragent_crewai.utils.field_filling import fill_text_field, handle_dropdown, check_checkbox
#from sragent_crewai.tools.bedrock_decision_tool import BedrockDecisionTool
#from sragent_crewai.utils.log_utils import log_fill_section

#def is_blank(value):
#    return value is None or str(value).strip() == ""

#async def smart_fill_section(page, goal="Fill out the form as reasonably as possible"):
#    filled_keys = set()
#    filled = 0
#    max_passes = 3
#    field_logs = []

#    for attempt in range(max_passes):
#        print(f"\n[smart_fill_section] Pass {attempt + 1}")
#        field_info, _ = await scrape_elements(page)

#        field_map = {}
#        for f in field_info:
#            norm_key = normalize(f["full_key"])
#            if norm_key in filled_keys:
#                continue
#            field_map.setdefault(norm_key, []).append((f['element'], f['kind']))

#        field_descriptions = []
#        for f in field_info:
#            if normalize(f["full_key"]) in filled_keys:
#                continue
#            desc = f"- Field: {f['full_key']} | Type: {f['kind']}"
#            if f["kind"] == "select" and f.get("options"):
#                desc += f" | Options: {f['options']}"
#            field_descriptions.append(desc)

#        if not field_descriptions:
#            break

#        prompt = f"""
#You are filling out a web form with the goal: "{goal}".

#Here are the fields and their details:
#{chr(10).join(field_descriptions)}

#Return a valid JSON object where each key is the field's label and context, like:
#{{ "First name (primaryContact)": "Alice", "Email (pi)": "alice@example.com" }}
#"""

#        decision_tool = BedrockDecisionTool()
#        options = [f['full_key'] for f in field_info]

#        try:
#            response = decision_tool._run(goal=goal, options=options, custom_prompt=prompt, max_tokens=300)
#            json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
#            answers = json.loads(json_str)
#        except Exception as e:
#            field_logs.append({
#                "label": "bedrock_response",
#                "value": response if "response" in locals() else None,
#                "status": "bedrock_failure",
#                "error": str(e)
#            })

#            shortened_options = options[:min(3, len(options))]
#            fallback_prompt = f"""Goal: {goal}
#Options: {shortened_options}
#Respond with a valid JSON object like: {{ "field": "value" }}
#"""
#            try:
#                response = decision_tool._run(goal=goal, options=shortened_options, custom_prompt=fallback_prompt)
#                json_str = re.search(r"\{.*\}", response, re.DOTALL).group()
#                answers = json.loads(json_str)

#                field_logs.append({
#                    "label": "bedrock_response",
#                    "value": response,
#                    "status": "recovered",
#                    "fix": "used fallback prompt with trimmed options"
#                })
#            except Exception as retry_error:
#                field_logs.append({
#                    "label": "bedrock_response",
#                    "value": None,
#                    "status": "retry_failed",
#                    "error": str(retry_error)
#                })
#                return f"Failed to parse AI response after retry:\n{str(retry_error)}"

#        for full_label, value in answers.items():
#            norm_key = normalize(full_label)
#            if norm_key in filled_keys:
#                continue

#            entries = field_map.get(norm_key)
#            if not entries:
#                field_logs.append({"label": full_label, "value": value, "status": "not_found"})
#                continue

#            filled_successfully = False

#            for el, kind in entries:
#                try:
#                    if kind == "input":
#                        if is_blank(value):
#                            field_logs.append({"label": full_label, "value": value, "status": "empty_value"})
#                            break
#                        await fill_text_field(el, value)
#                        actual_value = await el.input_value()
#                        if actual_value != str(value):
#                            field_logs.append({
#                                "label": full_label,
#                                "value": value,
#                                "status": "rejected_by_field",
#                                "note": f"Field retained: '{actual_value}'"
#                            })
#                            break
#                        filled_keys.add(norm_key)
#                        filled += 1
#                        field_logs.append({"label": full_label, "value": value, "status": "success"})
#                        filled_successfully = True
#                        break

#                    elif kind == "select":
#                        values = value if isinstance(value, list) else [value]
#                        for v in values:
#                            if isinstance(v, dict):
#                                v = v.get("name") or next(iter(v.values()), None)
#                            if is_blank(v):
#                                continue
#                            if await handle_dropdown(page, el, full_label, v):
#                                filled_keys.add(norm_key)
#                                filled += 1
#                                field_logs.append({"label": full_label, "value": v, "status": "success"})
#                                filled_successfully = True
#                                break

#                    elif kind == "checkbox":
#                        if is_blank(value):
#                            field_logs.append({"label": full_label, "value": value, "status": "empty_value"})
#                            break
#                        should_check = str(value).strip().lower() in {"yes", "true", "1", "checked"}
#                        await check_checkbox(el, should_check)
#                        checked_state = await el.is_checked()
#                        if checked_state != should_check:
#                            field_logs.append({
#                                "label": full_label,
#                                "value": should_check,
#                                "status": "rejected_by_field",
#                                "note": f"Checkbox retained: '{checked_state}'"
#                            })
#                            break
#                        filled_keys.add(norm_key)
#                        filled += 1
#                        field_logs.append({"label": full_label, "value": should_check, "status": "success"})
#                        filled_successfully = True
#                        break

#                except Exception as e:
#                    field_logs.append({
#                        "label": full_label,
#                        "value": value,
#                        "status": "error",
#                        "error": str(e)
#                    })

#            if not filled_successfully:
#                field_logs.append({"label": full_label, "value": value, "status": "skipped"})

#    result = f"Filled {filled} fields across {len(filled_keys)} unique keys"

#    successful_fills = sum(1 for log in field_logs if log.get("status") == "success")
#    incomplete = any(log.get("status") in {"skipped", "rejected_by_field", "empty_value", "error"} for log in field_logs)

#    log_fill_section(
#        tool="smart_fill_section",
#        goal=goal,
#        section_number=1,
#        fields_filled=field_logs,
#        status="success" if successful_fills > 0 and not incomplete else "partial_or_failed"
#    )


#    return result
