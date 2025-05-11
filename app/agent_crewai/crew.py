from crewai import Agent, Crew, Process, Task, TaskOutput
from crewai.agents.parser import AgentFinish
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from configurations.configs import Configs
from crosscutting.app_logger import AppLogger


@CrewBase
class ContentGen:
    """Agent crew"""

    agents: List[BaseAgent]
    tasks: List[Task]\

    def __init__(self, configs: Configs):
        self.configs = configs

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=False
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=False
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    def logs_callback(self, source: str, data):
        if isinstance(data, AgentFinish):
            AppLogger.info(f"{source} finished. {type(data)}")
        elif isinstance(data, TaskOutput):
            AppLogger.info(f"[{data.agent} - {data.name}] Finished.")

    @crew
    def crew(self) -> Crew:
        """Creates the Agent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.configs.flags.agent_log_verbose,
            step_callback=lambda x: self.logs_callback('Step', x),
            task_callback=lambda x: self.logs_callback('Task', x)
        )
