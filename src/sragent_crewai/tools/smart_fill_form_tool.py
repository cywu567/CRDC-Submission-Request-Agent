#from crewai.tools import BaseTool
#from typing import Type
#from pydantic import BaseModel, Field
#from sragent_crewai.utils.session_manager import get_page
#from sragent_crewai.utils.smart_fill_logic import smart_fill_section
#from sragent_crewai.tools.click_next_tool import ClickNextTool
#from sragent_crewai.utils.fill_form_set_vals import fill_rest_form
#from sragent_crewai.utils.log_utils import log_tool_execution


#class SmartFillFormToolInput(BaseModel):
#    goal: str = Field(default="Fill out the form as reasonably as possible")

#class SmartFillFormTool(BaseTool):
#    name: str = "smart_fill_form"
#    description: str = "Uses AI to fill out all sections of a multi-page form and then submit it."
#    args_schema: Type[BaseModel] = SmartFillFormToolInput

#    def _run(self, goal: str) -> str:
#        input_data = {"goal": goal}
#        filled_sections = 0
#        all_results = []
#        try:
#            page = get_page()

#            # Fill each section and click Next
#            while True:
#                result = smart_fill_section(page, goal)
#                all_results.append(result)
#                filled_sections += 1
#                print(f"[smart_fill_form] Filled section {filled_sections}")

#                click_result = ClickNextTool()._run()
#                print(f"[smart_fill_form] Next click result: {click_result}")
#                if "Clicked the 'Next' button." not in click_result:
#                    print("[smart_fill_form] No more Next button. Preparing to submit.")
#                    break

#            #result = smart_fill_section(page, goal)
#            #all_results.append(result)
#            #filled_sections += 1
#            #print(f"[smart_fill_form] Filled section {filled_sections}")
#            #click_result = ClickNextTool()._run()
            
#            #result = smart_fill_section(page, goal)
#            #all_results.append(result)
#            #filled_sections += 1
#            #print(f"[smart_fill_form] Filled section {filled_sections}")
#            #click_result = ClickNextTool()._run()

#            #fill_rest_form(page)

#            # Final Save and Submit
#            save_button = page.query_selector("button:has-text('Save')")
#            if save_button:
#                save_button.click()

#            next_button = page.query_selector("button:has-text('Next')")
#            if next_button:
#                next_button.click()
#                page.wait_for_timeout(1000)

#            submit_button = page.query_selector("button:has-text('Submit')")
#            if submit_button:
#                submit_button.click()

#            confirm_button = page.query_selector("button:has-text('Confirm to Submit')")
#            if confirm_button:
#                confirm_button.click()

#            return f"Filled {filled_sections} sections and submitted the form."

#        except Exception as e:
#            log_tool_execution(
#                tool_name="smart_fill_form",
#                input_data=input_data,
#                output_data={"filled_sections": filled_sections, "results": all_results},
#                status="error",
#                error_message=str(e)
#            )
#            return f"SmartFillFormTool error: {str(e)}"

from crewai.tools import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.smart_fill_logic import smart_fill_section
from sragent_crewai.tools.click_next_tool import ClickNextTool
from sragent_crewai.utils.fill_form_set_vals import fill_rest_form
from sragent_crewai.utils.log_utils import log_tool_execution


class SmartFillFormToolInput(BaseModel):
    goal: str = Field(default="Fill out the form as reasonably as possible")

class SmartFillFormTool(BaseTool):
    name: str = "smart_fill_form"
    description: str = "Uses AI to fill out all sections of a multi-page form and then submit it."
    args_schema: Type[BaseModel] = SmartFillFormToolInput

    def _run(self, goal: Optional[str] = None) -> str:
        goal = goal or "Fill out the form as reasonably as possible"
        input_data = {"goal": goal}
        filled_sections = 0
        all_results = []

        try:
            page = get_page()

            # Section 1
            result = smart_fill_section(page, goal)
            all_results.append(result)
            filled_sections += 1
            print(f"[smart_fill_form] Filled section {filled_sections}")
            click_result = ClickNextTool()._run()

            # Section 2
            result = smart_fill_section(page, goal)
            all_results.append(result)
            filled_sections += 1
            print(f"[smart_fill_form] Filled section {filled_sections}")
            click_result = ClickNextTool()._run()

            fill_rest_form(page)

            # Final Save and Submit
            save_button = page.query_selector("button:has-text('Save')")
            if save_button:
                save_button.click()

            next_button = page.query_selector("button:has-text('Next')")
            if next_button:
                next_button.click()
                page.wait_for_timeout(1000)

            submit_button = page.query_selector("button:has-text('Submit')")
            if submit_button:
                submit_button.click()

            confirm_button = page.query_selector("button:has-text('Confirm to Submit')")
            if confirm_button:
                confirm_button.click()

            output_data = {
                "filled_sections": filled_sections,
                "results": all_results
            }

            return f"Filled {filled_sections} sections and submitted the form."

        except Exception as e:
            log_tool_execution(
                tool_name="smart_fill_form",
                input_data=input_data,
                output_data=None,
                status="error",
                error_message=str(e)
            )
            return f"SmartFillFormTool error: {str(e)}"