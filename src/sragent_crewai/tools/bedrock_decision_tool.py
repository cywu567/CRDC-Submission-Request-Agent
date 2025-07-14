#from crewai.tools import BaseTool
#from typing import Type, List
#from pydantic import BaseModel, Field
#from sragent_crewai.utils.log_utils import log_tool_execution
#import boto3
#import json

#bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

#class BedrockDecisionInput(BaseModel):
#    goal: str = Field(..., description="What the agent is trying to do")
#    options: List[str] = Field(..., description="List of visible button or action texts")
#    custom_prompt: str = Field("", description="Optional custom prompt to override default LLM behavior")
#    max_tokens: int = Field(50, description="Maximum number of tokens for LLM")

#class BedrockDecisionTool(BaseTool):
#    name: str = "bedrock_decision_tool"
#    description: str = "Uses Claude 3 Haiku via AWS Bedrock to choose the best action from options."
#    args_schema: Type[BaseModel] = BedrockDecisionInput

#    def _run(self, goal: str, options: List[str], custom_prompt: str = "", max_tokens: int=50) -> str:
#        input_data = {
#            "goal": goal,
#            "options": options,
#            "custom_prompt": custom_prompt,
#            "max_tokens": max_tokens
#        }
        
#        field_logs = []

#        try:
#            if custom_prompt and custom_prompt.strip():
#                user_prompt = custom_prompt
#            else:
#                user_prompt = f"""You are helping a browser automation agent decide which button to click
#                    based on the goal and the visible options.

#                    The page shows these options:
#                    {options}

#                    The agent's goal is: "{goal}"

#                    Which option should it click? Respond with only the exact button text."""

#            body = {
#                "anthropic_version": "bedrock-2023-05-31",
#                "messages": [
#                    {"role": "user", "content": user_prompt}
#                ],
#                "max_tokens": max_tokens
#            }

#            response = bedrock.invoke_model(
#                modelId="anthropic.claude-3-haiku-20240307-v1:0",
#                body=json.dumps(body),
#                contentType="application/json",
#                accept="application/json"
#            )

#            result = json.loads(response["body"].read().decode())
#            output_text = result["content"][0]["text"].strip()

#            return output_text

#        except Exception as e:
#            #log_tool_execution(
#            #    tool_name="bedrock_decision_tool",
#            #    input_data=input_data,
#            #    output_data=None,
#            #    status="error",
#            #    error_message=str(e)
#            #)
#            raise e

from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from sragent_crewai.utils.log_utils import log_tool_execution
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

class BedrockDecisionInput(BaseModel):
    goal: str = Field(..., description="What the agent is trying to do")
    options: List[str] = Field(..., description="List of visible button or action texts")
    custom_prompt: str = Field("", description="Optional custom prompt to override default LLM behavior")
    max_tokens: int = Field(50, description="Maximum number of tokens for LLM")

class BedrockDecisionTool(BaseTool):
    name: str = "bedrock_decision_tool"
    description: str = "Uses Claude 3 Haiku via AWS Bedrock to choose the best action from options."
    args_schema: Type[BaseModel] = BedrockDecisionInput

    def _run(self, goal: str, options: List[str], custom_prompt: str = "", max_tokens: int = 50) -> str:
        input_data = {
            "goal": goal,
            "options": options,
            "custom_prompt": custom_prompt,
            "max_tokens": max_tokens
        }

        def build_prompt(goal, opts):
            return f"""You are helping a browser automation agent decide which button to click
based on the goal and the visible options.

The page shows these options:
{opts}

The agent's goal is: \"{goal}\"

Which option should it click? Respond with only the exact button text."""

        def run_bedrock(prompt):
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-haiku-20240307-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )
            result = json.loads(response["body"].read().decode())
            return result["content"][0]["text"].strip()

        try:
            user_prompt = custom_prompt.strip() if custom_prompt else build_prompt(goal, options)
            return run_bedrock(user_prompt)

        except Exception as e:
            logs = [{
                "label": "bedrock_response",
                "value": None,
                "status": "bedrock_failure",
                "error": str(e)
            }]

            # Retry with fallback options and prompt
            try:
                fallback_options = options[:min(3, len(options))]
                fallback_prompt = custom_prompt.strip() if custom_prompt else build_prompt(goal, fallback_options)
                recovered = run_bedrock(fallback_prompt)

                logs.append({
                    "label": "bedrock_response",
                    "value": recovered,
                    "status": "recovered",
                    "fix": "used fallback prompt with trimmed options"
                })

                log_tool_execution(
                    tool_name="bedrock_decision_tool",
                    input_data={**input_data, "retry": True},
                    output_data=logs,
                    status="success"
                )

                return recovered

            except Exception as retry_error:
                logs.append({
                    "label": "bedrock_response",
                    "value": None,
                    "status": "retry_failed",
                    "error": str(retry_error)
                })

                log_tool_execution(
                    tool_name="bedrock_decision_tool",
                    input_data={**input_data, "retry": True},
                    output_data=logs,
                    status="partial_or_failed"
                )

                raise retry_error

