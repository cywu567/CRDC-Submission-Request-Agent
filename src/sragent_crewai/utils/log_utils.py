import boto3
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path="/Users/celinewu/Desktop/ESI 2025/CRDC/CRDC-AI-Farm/sragent_crewai/.env.logging", override=True)
dynamodb = boto3.resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION_NAME"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

def log_fill_section(tool, goal, section_number, fields_filled, status, table="SR-Agent-FillFormLogs"):
    try:
        table = dynamodb.Table(table)
        print(f"[log_fill_section] Logging to table: {table.name}")
        table.put_item(Item={
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "goal": goal,
            "section_number": section_number,
            "fields_filled": fields_filled,
            "status": status
        })
    except Exception as e:
        print(f"[log_fill_section] Error logging form fill: {e}")


def log_tool_execution(tool_name, input_data, output_data, status="success", error_message=None, table="SR-Agent-ToolFormLogs"):
    try:
        table = dynamodb.Table(table)
        table.put_item(Item={
            "execution_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": tool_name,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error_message": error_message
        })
    except Exception as e:
        print(f"[log_tool_execution] Error logging tool run: {e}")
