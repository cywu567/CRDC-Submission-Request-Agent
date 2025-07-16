# sragent_crewai/utils/aws_client.py
from dotenv import load_dotenv
import boto3
import os

def get_bedrock_client(env_path="/Users/celinewu/Desktop/ESI 2025/CRDC/CRDC-AI-Farm/sragent_crewai/.env"):
    load_dotenv(dotenv_path=env_path, override=True)
    return boto3.client(
        "bedrock-runtime",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION_NAME", "us-east-1")
    )
