from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page, set_page
from sragent_crewai.utils.smart_click import smart_click

class CreateSubmissionToolInput(BaseModel):
    pass

class CreateSubmissionTool(BaseTool):
    name: str = "create_submission"
    description: str = "Creates a new submission request."
    args_schema: Type[BaseModel] = CreateSubmissionToolInput

    def _run(self) -> str:
        try:
            page = get_page()
            page.wait_for_timeout(1000)
            smart_click(page, "Go to Submission Requests tab", filter_by_tag="div[role='button']")
            page.wait_for_timeout(1000)
            smart_click(page, "Start a Submission Request", filter_by_tag="button")
            page.wait_for_timeout(1000)
            smart_click(page, "Read and Accept Terms")
            set_page(page)

            return f"Submission request started at URL: {page.url}"

        except Exception as e:
            return f"CreateSubmissionTool error: {str(e)}"
