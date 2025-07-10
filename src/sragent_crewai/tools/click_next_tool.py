from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel
from sragent_crewai.utils.session_manager import get_page

class ClickNextInput(BaseModel):
    pass  # No input needed — always looks for the "Next" button

class ClickNextTool(BaseTool):
    name: str = "click_next"
    description: str = "Clicks the 'Next' button to move to the next page or section of the form."
    args_schema: Type[BaseModel] = ClickNextInput

    def _run(self) -> str:
        try:
            page = get_page()
            button = page.query_selector("button:has-text('Next')")
            if button:
                if button.is_enabled():
                    button.click()
                    page.wait_for_timeout(1000)
                    return "Clicked the 'Next' button."
                else:
                    return "'Next' button was found but disabled."
            else:
                return "No 'Next' button was found on the page."
        except Exception as e:
            return f"ClickNextTool error: {str(e)}"
