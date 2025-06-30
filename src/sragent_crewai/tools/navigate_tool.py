from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_browser_session
from sragent_crewai.utils.smart_click import smart_click


class NavigateToolInput(BaseModel):
    """Input schema for NavigateTool."""
    destination: str = Field(..., description="Where to go, like 'start a new submission request'")


class NavigateTool(BaseTool):
    name: str = "navigate"
    description: str = (
        "Navigate through the CRDC portal. "
        "Based on the destination description, it clicks the right buttons to get there. "
        "This tool uses reasoning to figure out which UI elements to interact with."
    )
    args_schema: Type[BaseModel] = NavigateToolInput

    def _run(self, destination: str) -> str:
        try:
            _, _, page = get_browser_session()

            page.goto("https://hub-qa.datacommons.cancer.gov/")
            page.wait_for_load_state("networkidle")

            if "submission" in destination.lower():
                smart_click(page, "Submission Requests")
                smart_click(page, "Start a Submission Request")
                try:
                    smart_click(page, "I agree")
                except:
                    pass

            elif "dashboard" in destination.lower():
                smart_click(page, "Dashboard")

            # Additional navigation logic can go here

            return f"Navigated to: {page.url}"

        except Exception as e:
            return f"NavigateTool error: {str(e)}"
