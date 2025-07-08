from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.smart_fill import smart_fill
from sragent_crewai.utils.fill_form_set_vals import fill_rest_form

class SmartFillFormToolInput(BaseModel):
    goal: str = Field(default="Fill out the form as reasonably as possible")

class SmartFillFormTool(BaseTool):
    name: str = "smart_fill_form"
    description: str = "Uses AI to identify and fill out all fields on a form."
    args_schema: Type[BaseModel] = SmartFillFormToolInput

    def _run(self, goal: str) -> str:
        try:
            page = get_page()
            all_results = []

            #while True:
            result = smart_fill(page, goal)
            all_results.append(result)
            print(f"[smart_fill_form] One section filled.")
            next_button = page.query_selector("button:has-text('Next')")
            next_button.click()
            fill_rest_form(page)
                
                
                
                # Try clicking Next button
                #next_button = page.query_selector("button:has-text('Next')")
                #if next_button and next_button.is_enabled():
                #    next_button.click()
                #    print("[smart_fill_form] Clicked Next. Waiting for new section...")
                #    page.wait_for_selector("input, textarea, select, [role='button']", timeout=5000)
                #else:
                #    print("[smart_fill_form] No Next button found or it is disabled.")
                #    break

            return "\n".join(all_results)

        except Exception as e:
            return f"SmartFillFormTool error: {str(e)}"
