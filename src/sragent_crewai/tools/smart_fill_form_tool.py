from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.smart_fill import smart_fill

class SmartFillFormToolInput(BaseModel):
    goal: str = Field(default="Fill out the form as reasonably as possible")

class SmartFillFormTool(BaseTool):
    name: str = "smart_fill_form"
    description: str = "Uses AI to identify and fill out all fields on a form."
    args_schema: Type[BaseModel] = SmartFillFormToolInput

    def _run(self, goal: str) -> str:
        try:
            page = get_page()
            result = smart_fill(page, goal)
            return result
        except Exception as e:
            return f"SmartFillFormTool error: {str(e)}"
