import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

def log_fill_section(tool, goal, section_number, fields_filled, status, table="SR-Agent-FillFormLogs"):
    try:
        table = dynamodb.Table(table)
        print(f"[log_fill_section] Logging to table: {table.name}")
        table.put_item(Item={
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool,
            "goal": goal,
            "section_number": section_number,
            "fields_filled": fields_filled,
            "status": status
        })
    except Exception as e:
        print(f"[log_fill_section] Error logging form fill: {e}")
