from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.smart_click import smart_click
from sragent_crewai.utils.session_manager import get_page

class SmartClickToolInput(BaseModel):
    goal: str = Field(..., description="The user's intent (e.g., 'Click login button', 'Continue')")
    filter_by_tag: str | None = Field(
        default=None,
        description="Optional HTML tag or role selector to limit clickable elements (e.g., 'button', 'div[role=button]')"
    )

class SmartClickTool(BaseTool):
    name: str = "smart_click"
    description: str = "Uses a Bedrock-backed LLM to choose and click the most appropriate button or element on the page."
    args_schema: Type[BaseModel] = SmartClickToolInput

    def _run(self, goal: str, filter_by_tag: str = None) -> str:
        try:
            page = get_page()
            clicked_text = smart_click(page, goal, filter_by_tag)
            return f"Successfully clicked: '{clicked_text}'"
        except Exception as e:
            return f"SmartClickTool error: {str(e)}"
