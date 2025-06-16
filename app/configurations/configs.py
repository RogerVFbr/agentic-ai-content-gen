from enum import Enum

from typing import Dict, Literal

from pydantic import BaseModel

class WebSearchClient(Enum):
    Tavily = "Tavily"
    SerperDev = "SerperDev"

class ImageGeneration(BaseModel):
    deliverables_path: str
    assets_path: str
    image_size: Literal["auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]

class UsedTopics(BaseModel):
    cache_path: str
    cache_ttl_hours: int

class WebSearch(BaseModel):
    client: WebSearchClient = WebSearchClient.Tavily
    cache_path: str
    cache_ttl_minutes: int
    quota_per_node: int

class Flags(BaseModel):
    agent_log_verbose: bool
    feature_y: bool

class Configs(BaseModel):
    image_generation: ImageGeneration
    used_topics: UsedTopics
    web_search: WebSearch
    flags: Flags
    remote_credentials: Dict[str, str]