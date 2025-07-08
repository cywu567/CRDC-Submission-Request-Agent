### **CRDC Datahub Submission Agent**

This project develops a custom AI agent to automate the testing of the CRDC Datahub submission request form. Built with Python tools for synthetic data generation and intelligent browser automation, it validates form behavior across text inputs, dropdowns, and dynamic UI elements using Playwright and Faker.
Designed for scalable execution on platforms like AWS Bedrock, the system supports remote, dependency-free operation. An integrated feedback loop logs form responses and system behaviors into a vector database, enabling the agent to learn from outcomes and improve over time. Agent orchestration is powered by CrewAI, allowing seamless task delegation and modular tool coordination.


## Setup
1. **Activate the Python virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

2. **Add Login Info to .env file**
   TOTP_SECRET=YOUR_TOTP_SECRET
   LOGIN_USERNAME=YOUR_LOGIN_USERNAME
   LOGIN_PASSWORD=YOUR_LOGIN_PASSWORD

3. **Install requirements**
   ```bash
   pip install boto3 pyotp playwright
   ```

4. To run, cd into the main folder, and run

```bash
PYTHONPATH=src python src/fedlead_agent_crewai/main.py   
```    
