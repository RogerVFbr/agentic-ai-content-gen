from typing import List, Set, Optional

from pydantic import BaseModel, Field


class Research(BaseModel):
    """Final result of the trend research"""
    tool_call_status: bool = Field(description ="Whether the search tool was called successfully or not")
    tool_call_reason: str = Field(description ="Reason why or why not you called the search tool. Give all possible details. Include eny error logs.")
    combined_joke: str = Field(description = "The joke you created by combining the topics.")
    primary_topic: str = Field(description = "The primary topic you would recommend from your search")
    primary_topic_reason: str = Field(description = "The reason why you would recommend the primary topic")
    primary_topic_facts: List[str] = Field(description ="A list of short facts related to the primary topic which you retrieved from your search")
    secondary_topic: str = Field(description = "The secondary topic you would recommend from your search")
    secondary_topic_reason: str = Field(description = "The reason why you would recommend the secondary topic")
    secondary_topic_facts: List[str] = Field(description ="A list of short facts related to the secondary topic which you retrieved from your search")
    full_topics_list: List[str] = Field(description = "The list of topics originally retrieved from Google Trends only with their names")


class Validation(BaseModel):
    """Final result of the trend research validation"""
    iterations: int
    primary_topic: str = Field(description = "The primary topic exactly how you received it.")
    primary_topic_status: bool = Field(description ="State whether the trend research for the primary topic is valid or not")
    primary_topic_reason: str = Field(description ="Justify your validation conclusion for the primary topic. Give all possible details. Include any error logs.")
    secondary_topic: str = Field(description = "The secondary topic exactly how you received it.")
    secondary_topic_status: bool = Field(description ="State whether the trend research for the secondary topic is valid or not")
    secondary_topic_reason: str = Field(description ="Justify your validation conclusion for the secondary topic. Give all possible details. Include any error logs.")


class Edition(BaseModel):
    """Final result of the meme creation"""
    # text_setup: str = Field(description = "The setup part of the joke.")
    # text_punchline: str = Field(description = "The punchline part of the joke.")
    style: str = Field(description = "The meme style chosen.")
    prompt: str = Field(description = "The image generation prompt.")
    image_url: str = None
    image_id: str = None


class MemeGenState(BaseModel):
    prior_topics: Set[str] = set()
    research: Optional[Research] = None
    validation: Optional[Validation] = None
    editor: Optional[Edition] = None
