#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from sragent_crewai.crew import SragentCrewai
from dotenv import load_dotenv
import os
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    load_dotenv()
    inputs = {
        "username": os.getenv("LOGIN_USERNAME"),
        "password": os.getenv("LOGIN_PASSWORD"),
        "totp_secret": os.getenv("TOTP_SECRET")
    }

    try:
        crew_instance = SragentCrewai(inputs=inputs)
        crew_instance.crew().kickoff()
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        SragentCrewai().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SragentCrewai().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        SragentCrewai().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def run_direct():
    from sragent_crewai.tools.login_tool import LoginTool
    load_dotenv()
    tool = LoginTool()

    # Print inputs loaded from .env
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")
    totp_secret = os.getenv("TOTP_SECRET")

    print("Running LoginTool directly with:")
    print("  username:", username)
    print("  password:", '*' * len(password) if password else None)
    print("  totp_secret:", totp_secret)

    result = tool.run(
        username=username,
        password=password,
        totp_secret=totp_secret
    )
    print("LoginTool result:", result)

def direct_run():
    from dotenv import load_dotenv
    from sragent_crewai.tools.login_tool import LoginTool
    from sragent_crewai.tools.navigate_tool import NavigateTool
    from sragent_crewai.tools.create_submission_tool import CreateSubmissionTool
    from sragent_crewai.tools.smart_fill_form_tool import SmartFillFormTool

    load_dotenv()

    # Load credentials from .env
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")
    totp_secret = os.getenv("TOTP_SECRET")

    # Step 1: Login
    login_tool = LoginTool()
    login_result = login_tool.run(
        username=username,
        password=password,
        totp_secret=totp_secret
    )
    print("LoginTool result:", login_result)

    # Step 2: Navigate
    destination = "submission request"
    print(f"Navigating to destination: '{destination}'")
    navigate_tool = NavigateTool()
    navigate_result = navigate_tool.run(destination=destination)
    print("NavigateTool result:", navigate_result)
    
    # Step 3: Create submission request
    print("Creating submission request...")
    create_tool = CreateSubmissionTool()
    create_result = create_tool.run()
    print("CreateSubmissionTool result:", create_result)
    
    print("Filling form with smart AI tool...")
    fill_tool = SmartFillFormTool()
    fill_result = fill_tool.run({"goal": "Fill out the submission request form with realistic test data"})
    print("SmartFillFormTool result:", fill_result)

if __name__ == "__main__":
    #direct_run()
    run()