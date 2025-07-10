from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.session_manager import get_page
from sragent_crewai.utils.smart_fill_logic import smart_fill_section

class SmartFillSectionInput(BaseModel):
    goal: str = Field(
        default="Fill out the current form section as reasonably as possible",
        description="High-level instruction for what the AI should prioritize in this section."
    )

class SmartFillSectionTool(BaseTool):
    name: str = "smart_fill_section"
    description: str = "Uses Bedrock-backed LLM to analyze visible fields on the current page section and fill them with appropriate values."
    args_schema: Type[BaseModel] = SmartFillSectionInput

    def _run(self, goal: str) -> str:
        try:
            page = get_page()
            return smart_fill_section(page, goal)
        except Exception as e:
            return f"SmartFillSectionTool error: {str(e)}"
