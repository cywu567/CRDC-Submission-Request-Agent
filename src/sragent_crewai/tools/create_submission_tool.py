from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page, set_page
from sragent_crewai.utils.smart_click import smart_click
from sragent_crewai.utils.log_utils import log_tool_execution


class CreateSubmissionToolInput(BaseModel):
    pass

class CreateSubmissionTool(BaseTool):
    name: str = "create_submission"
    description: str = "Creates a new submission request."
    args_schema: Type[BaseModel] = CreateSubmissionToolInput

    def _run(self) -> str:
        input_data = {}

        try:
            page = get_page()
            page.wait_for_timeout(1000)
            smart_click(page, "Go to Submission Requests tab", filter_by_tag="div[role='button']")
            page.wait_for_timeout(1000)
            smart_click(page, "Start a Submission Request", filter_by_tag="button")
            page.wait_for_timeout(1000)
            smart_click(page, "Read and Accept Terms")
            set_page(page)

            output = f"Submission request started at URL: {page.url}"

            log_tool_execution(
                tool_name="create_submission",
                input_data=input_data,
                output_data={"url": page.url},
                status="success"
            )

            return output

        except Exception as e:
            log_tool_execution(
                tool_name="create_submission",
                input_data=input_data,
                output_data=None,
                status="error",
                error_message=str(e)
            )
            return f"CreateSubmissionTool error: {str(e)}"