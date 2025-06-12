from enum import Enum

from typing import Dict

from pydantic import BaseModel

class WebSearchClient(Enum):
    Tavily = "Tavily"
    SerperDev = "SerperDev"

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
    used_topics: UsedTopics
    web_search: WebSearch
    flags: Flags
    remote_credentials: Dict[str, str]