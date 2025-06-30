from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

class BedrockDecisionInput(BaseModel):
    goal: str = Field(..., description="What the agent is trying to do")
    options: List[str] = Field(..., description="List of visible button or action texts")

class BedrockDecisionTool(BaseTool):
    name: str = "bedrock_decision_tool"
    description: str = "Uses Claude 3 Haiku via AWS Bedrock to choose the best action from options."
    args_schema: Type[BaseModel] = BedrockDecisionInput

    def _run(self, goal: str, options: List[str]) -> str:
        system_prompt = (
            "You are helping a browser automation agent decide which button to click "
            "based on the goal and the visible options."
        )

        user_prompt = f"""{system_prompt}

        The page shows these options:
        {options}

        The agent's goal is: "{goal}"

        Which option should it click? Respond with only the exact button text."""

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 50
        }

        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        result = json.loads(response["body"].read().decode())
        return result["content"][0]["text"].strip()
