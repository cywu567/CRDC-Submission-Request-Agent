#from crewai.tools import BaseTool
#from typing import Type
#from pydantic import BaseModel, Field
#from sragent_crewai.utils.session_manager import get_page
#from sragent_crewai.utils.smart_fill_logic import smart_fill_section
#from sragent_crewai.tools.click_next_tool import ClickNextTool
#from sragent_crewai.utils.fill_form_set_vals import fill_rest_form


#class SmartFillFormToolInput(BaseModel):
#    goal: str = Field(default="Fill out the form as reasonably as possible")

#class SmartFillFormTool(BaseTool):
#    name: str = "smart_fill_form"
#    description: str = "Uses AI to fill out all sections of a multi-page form and then submit it."
#    args_schema: Type[BaseModel] = SmartFillFormToolInput

#    def _run(self, goal: str) -> str:
#        try:
#            page = get_page()
#            filled_sections = 0
#            all_results = []

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
#            return f"SmartFillFormTool error: {str(e)}"

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.smart_fill_logic import smart_fill_section
from sragent_crewai.tools.click_next_tool import ClickNextTool
from sragent_crewai.utils.fill_form_set_vals import fill_rest_form


class SmartFillFormToolInput(BaseModel):
    goal: str = Field(default="Fill out the form as reasonably as possible")

class SmartFillFormTool(BaseTool):
    name: str = "smart_fill_form"
    description: str = "Uses AI to fill out all sections of a multi-page form and then submit it."
    args_schema: Type[BaseModel] = SmartFillFormToolInput

    def _run(self, goal: str) -> str:
        try:
            page = get_page()
            filled_sections = 0
            all_results = []

            #while True:
            #    section_result = smart_fill_section(page, goal)
            #    all_results.append(section_result)
            #    filled_sections += 1
            #    print(f"[smart_fill_form] Filled section {filled_sections}")

            #    if isinstance(section_result, dict) and not section_result.get("ready_to_proceed", True):
            #        print(f"[smart_fill_form] LLM determined not to proceed: {section_result.get('reason')}")
            #        break

            #    click_result = ClickNextTool()._run()
            #    print(f"[smart_fill_form] Next click result: {click_result}")
            #    if "Clicked the 'Next' button." not in click_result:
            #        print("[smart_fill_form] No more Next button. Preparing to submit.")
            #        break


            result = smart_fill_section(page, goal)
            all_results.append(result)
            filled_sections += 1
            print(f"[smart_fill_form] Filled section {filled_sections}")
            click_result = ClickNextTool()._run()
            
            result = smart_fill_section(page, goal)
            all_results.append(result)
            filled_sections += 1
            print(f"[smart_fill_form] Filled section {filled_sections}")
            click_result = ClickNextTool()._run()

            fill_rest_form(page)

            #Final Save and Submit
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

            return f"Filled {filled_sections} sections and submitted the form."

        except Exception as e:
            return f"SmartFillFormTool error: {str(e)}"
