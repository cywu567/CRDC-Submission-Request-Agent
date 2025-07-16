#from crewai import Agent, Crew, Process, Task
#from crewai.project import CrewBase, agent, crew, task
#from sragent_crewai.tools.login_tool import LoginTool
#from sragent_crewai.tools.navigate_tool import NavigateTool
#from sragent_crewai.tools.create_submission_tool import CreateSubmissionTool
#from sragent_crewai.tools.smart_fill_form_tool import SmartFillFormTool
#from crewai.agents.agent_builder.base_agent import BaseAgent
#from typing import List
#from dotenv import load_dotenv
#import os

## If you want to run a snippet of code before or after the crew starts,
## you can use the @before_kickoff and @after_kickoff decorators
## https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

#@CrewBase
#class SragentCrewai():
#    """SragentCrewai crew"""

#    agents: List[BaseAgent]
#    tasks: List[Task]
    
#    def __init__(self, inputs: dict):
#        self.inputs = inputs
    
#    # Learn more about YAML configuration files here:
#    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
#    # If you would like to add tools to your agents, you can learn more about it here:
#    # https://docs.crewai.com/concepts/agents#agent-tools
#    @agent
#    def login_agent(self) -> Agent:
#        return Agent(
#            config=self.agents_config['login_agent'],
#            tools=[LoginTool()],
#        )
        
#    @agent
#    def navigate_agent(self) -> Agent:
#        return Agent(
#            config=self.agents_config['navigate_agent'],
#            tools=[NavigateTool()],
#        )
        
#    @agent
#    def create_sr_agent(self) -> Agent:
#        return Agent(
#            config=self.agents_config['create_sr_agent'],
#            tools=[CreateSubmissionTool()],
#        )
        
#    @agent
#    def smart_fill_agent(self) -> Agent:
#        return Agent(
#            config=self.agents_config['smart_fill_agent'],
#            tools=[SmartFillFormTool()]
#        )

#    # To learn more about structured task outputs,
#    # task dependencies, and task callbacks, check out the documentation:
#    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#    @task
#    def login_task(self, inputs=None) -> Task:
#        return Task(
#            description="Log into the CRDC QA portal using login.gov. Use the login_tool. Credentials are:\n"
#                f"Username: {self.inputs['username']}\n"
#                f"Password: {self.inputs['password']}\n"
#                f"TOTP Secret: {self.inputs['totp_secret']}",
#            expected_output="A successful login message or URL verification",
#            agent=self.login_agent(),
#            input={
#                "username": self.inputs["username"],
#                "password": self.inputs["password"],
#                "totp_secret": self.inputs["totp_secret"]
#            },
#            input_direct=True,
#            args_schema=None
#        )
        
#    @task
#    def navigate_task(self):
#        return Task(
#            config=self.tasks_config["navigate_task"],
#            agent=self.navigate_agent(),
#            input={"destination": "submission request"},
#            input_direct=True,
#        )
        
#    @task
#    def create_submission_task(self):
#        return Task(
#            config=self.tasks_config["create_submission_task"],
#            agent=self.create_sr_agent(),
#        )
        
#    @task
#    def smart_fill_task(self):
#        return Task(
#            config=self.tasks_config["smart_fill_task"],
#            agent=self.smart_fill_agent(),
#        )

#    @crew
#    def crew(self) -> Crew:
#        """Creates the SragentCrewai crew"""
#        return Crew(
#            agents=self.agents, # Automatically created by the @agent decorator
#            tasks=self.tasks, # Automatically created by the @task decorator
#            process=Process.sequential,
#            verbose=True,
#            tools=[],
#            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#        )


from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from sragent_crewai.tools.login_tool import LoginTool
from sragent_crewai.tools.navigate_tool import NavigateTool
from sragent_crewai.tools.create_submission_tool import CreateSubmissionTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
from sragent_crewai.tools.smart_fill_form_tool import SmartFillFormTool
from sragent_crewai.tools.click_next_tool import ClickNextTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class SragentCrewai():
    """SragentCrewai crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self, inputs: dict):
        self.inputs = inputs
    
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def login_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['login_agent'],
            tools=[LoginTool()],
        )
        
    @agent
    def navigate_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['navigate_agent'],
            tools=[NavigateTool()],
        )
        
    @agent
    def create_sr_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['create_sr_agent'],
            tools=[CreateSubmissionTool()],
        )
        
    
    @agent
    def smart_fill_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['smart_fill_agent'],
            tools=[
                SmartFillFormTool(),
                ClickNextTool()
            ]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def login_task(self, inputs=None) -> Task:
        return Task(
            description="Log into the CRDC QA portal using login.gov. Use the login_tool. Credentials are:\n"
                f"Username: {self.inputs['username']}\n"
                f"Password: {self.inputs['password']}\n"
                f"TOTP Secret: {self.inputs['totp_secret']}",
            expected_output="A successful login message or URL verification",
            agent=self.login_agent(),
            input={
                "username": self.inputs["username"],
                "password": self.inputs["password"],
                "totp_secret": self.inputs["totp_secret"]
            },
            input_direct=True,
            args_schema=None
        )
        
    @task
    def navigate_task(self):
        return Task(
            config=self.tasks_config["navigate_task"],
            agent=self.navigate_agent(),
            input={"destination": "submission request"},
            input_direct=True,
        )
        
    @task
    def create_submission_task(self):
        return Task(
            config=self.tasks_config["create_submission_task"],
            agent=self.create_sr_agent(),
        )
            
    @task
    def smart_fill_form_task(self):
        return Task(
            config=self.tasks_config["smart_fill_section_task"],
            agent=self.smart_fill_agent(),
            #input={"goal": "Fill out the form as reasonably as possible"},
            #input_direct=True,
        )


    @crew
    def crew(self) -> Crew:
        """Creates the SragentCrewai crew"""
        return Crew(
            agents=self.agents,
            tasks=[
                self.login_task(),
                self.navigate_task(),
                self.create_submission_task(),
                self.smart_fill_form_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )

