from pydantic import BaseModel

class PortfolioState(BaseModel):
    raw_input: str = ""
    music_summary: str = "No music summary available."
    tech_summary: str = "No tech summary available."
    narrative: str = "No narrative available."
    final_portfolio: str = "No final portfolio available."