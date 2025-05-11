import asyncio
from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from crosscutting.graceful_shutdown import GracefulShutdown


# === LLM and Search Setup ===
load_dotenv()
llm = ChatOpenAI(model="gpt-4", temperature=0.3)
search = SerpAPIWrapper()
search_tool = Tool.from_function(
    name="web_search",
    description="Search the web for relevant information",
    func=search.run,
)

# === Prompt Templates ===
music_prompt = """You are a music historian. Based on the raw input and search results, summarize Roger Freret's music career.\n\nInput: {input}\n\nSearch Results:\n{search_results}"""
tech_prompt = """You are a technology analyst. Based on the raw input and search results, summarize Roger Freret's career in IT.\n\nInput: {input}\n\nSearch Results:\n{search_results}"""
narrative_prompt = """Create a compelling unified professional narrative based on the following summaries:\n\nMusic: {music_summary}\n\nTech: {tech_summary}"""
editor_prompt = """Edit the narrative below into a polished bio for a professional portfolio site:\n\n{narrative}"""

# === Async Web Search Stub ===
async def async_search(query):
    return f"Fake search results for: {query}"  # Replace with real async search if needed

# === State Type ===
class PortfolioState(BaseModel):
    raw_input: str = ""
    music_summary: str = "No music summary available."
    tech_summary: str = "No tech summary available."
    narrative: str = "No narrative available."
    final_portfolio: str = "No final portfolio available."

# === Async Agent Functions ===
async def music_agent(state):
    query = "Roger Freret music career awards collaborations site:linkedin.com OR site:discogs.com"
    search_results = await async_search(query)
    response = await llm.ainvoke(music_prompt.format(
        input=state.raw_input,
        search_results=search_results
    ))
    state.music_summary = response.content
    return state

async def tech_agent(state):
    query = "Roger Freret software architect technology site:linkedin.com OR site:github.com"
    search_results = await async_search(query)
    response = await llm.ainvoke(tech_prompt.format(
        input=state.raw_input,  # Access raw_input directly
        search_results=search_results
    ))
    state.tech_summary = response.content  # Use dot notation
    return state

async def narrative_agent(state):
    response = await llm.ainvoke(narrative_prompt.format(
        music_summary=state.music_summary,
        tech_summary=state.tech_summary
    ))
    state.narrative = response.content
    return state

async def editor_agent(state):
    response = await llm.ainvoke(editor_prompt.format(narrative=state.narrative))
    state.final_portfolio = response.content
    return state


# === LangGraph Builder ===
class LangGraphBuilder:
    def build(self):
        builder = StateGraph(PortfolioState)
        builder.add_node("MusicAgent", RunnableLambda(lambda state: asyncio.run(music_agent(state))))
        builder.add_node("TechAgent", RunnableLambda(lambda state: asyncio.run(tech_agent(state))))
        builder.add_node("NarrativeAgent", RunnableLambda(lambda state: asyncio.run(narrative_agent(state))))
        builder.add_node("EditorAgent", RunnableLambda(lambda state: asyncio.run(editor_agent(state))))

        builder.set_entry_point("MusicAgent")
        builder.add_edge("MusicAgent", "TechAgent")
        builder.add_edge("TechAgent", "NarrativeAgent")
        builder.add_edge("NarrativeAgent", "EditorAgent")
        builder.add_edge("EditorAgent", END)

        return builder.compile()

# === LangGraph Runner ===
class LangGraphRunner:
    def __init__(self, graph, input_data):
        self.graph = graph
        self.input_data = input_data
        self.is_running = True

    async def run(self):
        try:
            async for step in self.graph.astream(self.input_data):
                print(f"Step executed: {step}")
            return await self.graph.ainvoke(self.input_data)
        except asyncio.CancelledError:
            print("[-] Task was cancelled.")
            self.is_running = False
            raise

# === Main Execution ===
async def main():
    # loop = asyncio.get_running_loop()
    shutdown = GracefulShutdown()
    shutdown.register()

    input_data = {
        "raw_input": (
            "Roger Freret is a Grammy-nominated audio engineer and senior software architect "
            "at a major Brazilian bank. He has worked with Antonio Adolfo, Leo Gandelman, Blitz, "
            "and Flavio Venturini. He's also a certified AWS expert and speaker on DevOps and cloud architecture."
        )
    }

    graph = LangGraphBuilder().build()
    runner = LangGraphRunner(graph, input_data)

    task = asyncio.create_task(runner.run())
    shutdown_task = asyncio.create_task(shutdown.wait())  # Wrap shutdown.wait in a task

    done, pending = await asyncio.wait(
        [task, shutdown_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    if shutdown.cancel_event.is_set():
        print("[x] Cancelling task due to shutdown request...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("[✓] Task cancelled successfully.")

    elif task in done:
        result = task.result()
        print("\n=== Final Portfolio Output ===\n")
        print(result["final_portfolio"])

# async def main():
#     loop = asyncio.get_running_loop()
#     shutdown = GracefulShutdown(loop)
#     shutdown.register()
#
#     input_data = {
#         "raw_input": (
#             "Roger Freret is a Grammy-nominated audio engineer and senior software architect "
#             "at a major Brazilian bank. He has worked with Antonio Adolfo, Leo Gandelman, Blitz, "
#             "and Flavio Venturini. He's also a certified AWS expert and speaker on DevOps and cloud architecture."
#         )
#     }
#
#     graph = LangGraphBuilder().build()
#     runner = LangGraphRunner(graph, input_data)
#
#     task = asyncio.create_task(runner.run())
#     shutdown_task = asyncio.create_task(shutdown.wait())  # Wrap shutdown.wait in a task
#
#     done, pending = await asyncio.wait(
#         [task, shutdown_task],
#         return_when=asyncio.FIRST_COMPLETED
#     )
#
#     if shutdown.cancel_event.is_set():
#         print("[x] Cancelling task due to shutdown request...")
#         task.cancel()
#         try:
#             await task
#         except asyncio.CancelledError:
#             print("[✓] Task cancelled successfully.")
#
#     elif task in done:
#         result = task.result()
#         print("\n=== Final Portfolio Output ===\n")
#         print(result["final_portfolio"])

# === Entry Point ===
if __name__ == "__main__":
    asyncio.run(main())