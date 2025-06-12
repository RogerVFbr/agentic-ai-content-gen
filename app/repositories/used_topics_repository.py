from datetime import datetime, timedelta, timezone
from typing import List
from dataclasses import dataclass
import os
import pickle

from configurations.configs import Configs
from crosscutting.logging.app_logger import AppLogger


@dataclass
class UsedTopic:
    name: str
    timestamp: datetime

class UsedTopicsRepository:
    def __init__(self,
                 configs: Configs,
                 logger: AppLogger):

        self.logger = logger
        self.file_path = f"{os.getcwd()}{configs.used_topics.cache_path}"
        self.ttl = timedelta(hours=configs.used_topics.cache_ttl_hours)
        self.topics: List[UsedTopic] = []

    async def get_all_topic_names(self) -> List[str]:
        """Retrieve all topic names as a list of strings."""
        await self._prune()
        return [topic.name for topic in self.topics]

    async def add_topic(self, name: str):
        """Add a new topic or update the timestamp if it already exists."""
        await self._prune()
        for topic in self.topics:
            if topic.name == name:
                topic.timestamp = datetime.now(timezone.utc)
                return
        self.topics.append(UsedTopic(name=name, timestamp=datetime.now(timezone.utc)))

    async def add_topics_batch(self, topics: List[str] | set[str]):
        """Add multiple topics or update their timestamps if they already exist."""
        await self._prune()
        current_time = datetime.now(timezone.utc)
        for name in topics:
            for topic in self.topics:
                if topic.name == name:
                    topic.timestamp = current_time
                    break
            else:
                self.topics.append(UsedTopic(name=name, timestamp=current_time))

    async def _prune(self):
        """Remove expired topics."""
        now = datetime.now(timezone.utc)
        self.topics = [topic for topic in self.topics if now - topic.timestamp <= self.ttl]

    async def flush(self):
        """Prune expired topics and save to the file."""
        await self._prune()
        with open(self.file_path, "wb") as f:
            pickle.dump(self.topics, f)
        self.logger.info("Used topics flushed.")

    async def load(self):
        """Load topics from the file and prune expired ones."""
        if not os.path.exists(self.file_path):
            self.topics = []
            self.logger.debug("No topics to load.")
            return

        if os.path.getsize(self.file_path) == 0:
            self.topics = []
            self.logger.debug("No topics to load.")
            return

        with open(self.file_path, "rb") as f:
            self.topics = pickle.load(f)
            for i, topic in enumerate(self.topics):
                if isinstance(topic, dict):
                    self.topics[i] = UsedTopic(**topic)
        await self._prune()
        self.logger.debug(f"{len(self.topics)} topic(s) loaded.")