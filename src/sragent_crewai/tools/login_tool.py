from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from sragent_crewai.utils.smart_click import smart_click
import pyotp
import time
from sragent_crewai.utils.session_manager import get_page, set_page
from sragent_crewai.utils.log_utils import log_tool_execution


class LoginToolInput(BaseModel):
    username: str = Field(..., description="CRDC portal username")
    password: str = Field(..., description="CRDC portal password")
    totp_secret: str = Field(..., description="Shared secret for TOTP 2FA")


class LoginTool(BaseTool):
    name: str = "login_tool"
    description: str = "Logs into the CRDC portal using Playwright, including TOTP-based 2FA."
    args_schema: Type[BaseModel] = LoginToolInput

    def _run(self, username: str, password: str, totp_secret: str) -> str:
        input_data = {"username": username}  # Avoid logging password or TOTP

        try:
            page = get_page()
            page.goto("https://hub-qa.datacommons.cancer.gov/")
            page.wait_for_load_state("networkidle")

            smart_click(page, "Allow for government monitorization by selecting Continue")
            page.wait_for_selector("text=Login to CRDC Submission Portal", timeout=10000)
            smart_click(page, "Click the main 'Log In' button to sign in to the CRDC portal (not sign up)")
            page.wait_for_selector("text=Login.gov")
            smart_click(page, "Choose Login.gov as the authentication method")

            page.wait_for_selector('input[name="user[email]"]')
            page.fill('input[name="user[email]"]', username)
            page.fill('input[name="user[password]"]', password)
            smart_click(page, "Submit my CRDC portal username and password")

            otp = pyotp.TOTP(totp_secret).now()
            page.get_by_label("One-time code").fill(otp)
            smart_click(page, "Submit my two-factor authentication code")

            page.wait_for_load_state("networkidle")
            try:
                smart_click(page, "Grant access to share information with the NIH and complete the login process")
                set_page(page)
            except:
                pass

            log_tool_execution(
                tool_name="login_tool",
                input_data=input_data,
                output_data={"message": "Login successful"},
                status="success"
            )
            return "Login successful"

        except Exception as e:
            log_tool_execution(
                tool_name="login_tool",
                input_data=input_data,
                output_data=None,
                status="error",
                error_message=str(e)
            )
            return f"LoginTool error: {str(e)}"
