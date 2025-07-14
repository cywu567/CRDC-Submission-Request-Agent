from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.log_utils import log_tool_execution

class ClickNextInput(BaseModel):
    pass  # No input needed — always looks for the "Next" button

class ClickNextTool(BaseTool):
    name: str = "click_next"
    description: str = "Clicks the 'Next' button to move to the next page or section of the form."
    args_schema: Type[BaseModel] = ClickNextInput

    def _run(self) -> str:
        input_data = {}

        try:
            page = get_page()
            button = page.query_selector("button:has-text('Next')")

            if button:
                if button.is_enabled():
                    button.click()
                    page.wait_for_timeout(1000)
                    return "Clicked the 'Next' button."
                else:
                    msg = "'Next' button was found but disabled."
            else:
                msg = "No 'Next' button was found on the page."

            # Only log if the button was missing or disabled
            log_tool_execution(
                tool_name="click_next",
                input_data=input_data,
                output_data={"result": msg},
                status="partial_or_failed"
            )
            return msg

        except Exception as e:
            log_tool_execution(
                tool_name="click_next",
                input_data=input_data,
                output_data=None,
                status="error",
                error_message=str(e)
            )
            return f"ClickNextTool error: {str(e)}"

