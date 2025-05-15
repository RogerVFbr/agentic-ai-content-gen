from typing import List

from pydantic import BaseModel, Field


class TrendResearch(BaseModel):
    """Final result of the trend research"""
    trends_tool_call_status: bool = Field(description = "Whether the trend tool was called successfully or not")
    trends_tool_call_reason: str = Field(description = "Reason why or why not you called the trend tool. Give all possible details. Include eny error logs.")
    search_tool_call_status: bool = Field(description = "Whether the search tool was called successfully or not")
    search_tool_call_reason: str = Field(description = "Reason why or why not you called the search tool. Give all possible details. Include eny error logs.")
    primary_topic: str = Field(description = "The primary topic you would recommend from your search")
    primary_topic_reason: str = Field(description = "The reason why you would recommend the primary topic")
    primary_topic_links: List[str] = Field(description = "A list of links related to the primary topic which you retrieved from your search")
    secondary_topic: str = Field(description = "The secondary topic you would recommend from your search")
    secondary_topic_reason: str = Field(description = "The reason why you would recommend the secondary topic")
    secondary_topic_links: List[str] = Field(description = "A list of links related to the secondary topic which you retrieved from your search")
    full_topics_list: List[str] = Field(description = "The list of topics originally retrieved from Google Trends only with their names")


class TrendResearchValidationStatus(BaseModel):
    """Final result of the trend research validation"""
    primary_topic_validation_status: bool = Field(description = "State whether the trend research for the primary topic is valid or not")
    primary_topic_validation_reason: str = Field(description = "Justify your validation conclusion for the primary topic. Give all possible details. Include any error logs.")
    secondary_topic_validation_status: bool = Field(description = "State whether the trend research for the secondary topic is valid or not")
    secondary_topic_validation_reason: str = Field(description = "Justify your validation conclusion for the secondary topic. Give all possible details. Include any error logs.")
    topics: str = Field(description="The topics you analyzed.")


class TrendResearchValidation(BaseModel):
    history: List[TrendResearchValidationStatus] = []

class MemeGenState(BaseModel):
    trend_research: TrendResearch = None
    trend_research_validation_history: TrendResearchValidation = TrendResearchValidation()
