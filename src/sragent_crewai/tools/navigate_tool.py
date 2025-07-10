from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page, set_page
from sragent_crewai.utils.smart_click import smart_click
from sragent_crewai.utils.log_utils import log_tool_execution
import time


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
        input_data = {"destination": destination}

        try:
            page = get_page()
            result = smart_click(page, destination)
            set_page(page)

            output = {
                "click_result": result,
                "final_url": page.url
            }

            log_tool_execution(
                tool_name="navigate",
                input_data=input_data,
                output_data=output,
                status="success"
            )

            return f"Navigation result: {result}\nFinal URL: {page.url}"

        except Exception as e:
            log_tool_execution(
                tool_name="navigate",
                input_data=input_data,
                output_data=None,
                status="error",
                error_message=str(e)
            )
            return f"NavigateTool error: {str(e)}"