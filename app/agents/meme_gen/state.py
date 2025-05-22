from typing import List, Set, Optional

from pydantic import BaseModel, Field


class TrendResearch(BaseModel):
    """Final result of the trend research"""
    search_tool_call_status: bool = Field(description = "Whether the search tool was called successfully or not")
    search_tool_call_reason: str = Field(description = "Reason why or why not you called the search tool. Give all possible details. Include eny error logs.")
    primary_topic: str = Field(description = "The primary topic you would recommend from your search")
    primary_topic_reason: str = Field(description = "The reason why you would recommend the primary topic")
    primary_topic_facts: List[str] = Field(description ="A list of short facts related to the primary topic which you retrieved from your search")
    secondary_topic: str = Field(description = "The secondary topic you would recommend from your search")
    secondary_topic_reason: str = Field(description = "The reason why you would recommend the secondary topic")
    secondary_topic_facts: List[str] = Field(description ="A list of short facts related to the secondary topic which you retrieved from your search")
    full_topics_list: List[str] = Field(description = "The list of topics originally retrieved from Google Trends only with their names")


class TrendResearchValidationStatus(BaseModel):
    """Final result of the trend research validation"""
    iterations: int
    primary_topic: str = Field(description = "The primary topic exactly how you received it.")
    primary_topic_status: bool = Field(description ="State whether the trend research for the primary topic is valid or not")
    primary_topic_reason: str = Field(description ="Justify your validation conclusion for the primary topic. Give all possible details. Include any error logs.")
    secondary_topic: str = Field(description = "The secondary topic exactly how you received it.")
    secondary_topic_status: bool = Field(description ="State whether the trend research for the secondary topic is valid or not")
    secondary_topic_reason: str = Field(description ="Justify your validation conclusion for the secondary topic. Give all possible details. Include any error logs.")


class MemeGenState(BaseModel):
    prior_topics: Set[str] = set()
    trend_research: Optional[TrendResearch] = None
    trend_research_validation: Optional[TrendResearchValidationStatus] = None
