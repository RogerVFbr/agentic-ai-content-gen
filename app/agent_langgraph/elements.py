import asyncio
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from crosscutting.app_logger import AppLogger

class ResearchAgentElements:

    def __init__(self,
                 logger: AppLogger):

        self.logger = logger
        self.llm = None
        self.search_tool = None
        self.music_prompt = """You are a music historian. Based on the raw input and search results, summarize Roger Freret's music career.\n\nInput: {input}\n\nSearch Results:\n{search_results}"""
        self.tech_prompt = """You are a technology analyst. Based on the raw input and search results, summarize Roger Freret's career in IT.\n\nInput: {input}\n\nSearch Results:\n{search_results}"""
        self.narrative_prompt = """Create a compelling unified professional narrative based on the following summaries:\n\nMusic: {music_summary}\n\nTech: {tech_summary}"""
        self.editor_prompt = """Edit the narrative below into a polished bio for a professional portfolio site:\n\n{narrative}"""

    def initialize(self):
        if self.llm is None:
            self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)

        if self.search_tool is None:
            self.search_tool = Tool.from_function(
                name="web_search",
                description="Search the web for relevant information",
                func=SerpAPIWrapper().run,
            )

    async def async_search(self, query):
        return f"Fake search results for: {query}"  # Replace with real async search if needed

    # === Async Agent Functions ===
    async def music_agent(self, state):
        query = "Roger Freret music career awards collaborations site:linkedin.com OR site:discogs.com"
        search_results = await self.async_search(query)
        response = await self.llm.ainvoke(self.music_prompt.format(
            input=state.raw_input,
            search_results=search_results
        ))
        state.music_summary = response.content
        return state

    async def tech_agent(self, state):
        query = "Roger Freret software architect technology site:linkedin.com OR site:github.com"
        search_results = await self.async_search(query)
        response = await self.llm.ainvoke(self.tech_prompt.format(
            input=state.raw_input,
            search_results=search_results
        ))
        state.tech_summary = response.content
        return state

    async def narrative_agent(self, state):
        response = await self.llm.ainvoke(self.narrative_prompt.format(
            music_summary=state.music_summary,
            tech_summary=state.tech_summary
        ))
        state.narrative = response.content
        return state

    async def editor_agent(self, state):
        response = await self.llm.ainvoke(self.editor_prompt.format(narrative=state.narrative))
        state.final_portfolio = response.content
        return state