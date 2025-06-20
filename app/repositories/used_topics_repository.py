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

    def __getstate__(self):
        return {"name": self.name, "timestamp": self.timestamp.isoformat()}

    def __setstate__(self, state):
        self.name = state["name"]
        self.timestamp = datetime.fromisoformat(str(state["timestamp"]))


class UsedTopicsRepository:
    def __init__(self,
                 configs: Configs,
                 logger: AppLogger):

        self._logger = logger
        self._file_path = f"{os.getcwd()}{configs.used_topics.cache_path}"
        self._ttl = timedelta(hours=configs.used_topics.cache_ttl_hours)
        self._topics: List[UsedTopic] = []

    async def get_all_topic_names(self) -> List[str]:
        """Retrieve all topic names as a list of strings."""
        await self._prune()
        return [topic.name for topic in self._topics]

    async def add_topics_batch(self, topics: List[str] | set[str]):
        """Add multiple topics or update their timestamps if they already exist."""
        await self._prune()
        current_time = datetime.now(timezone.utc)
        for name in topics:
            for topic in self._topics:
                if topic.name == name:
                    topic.timestamp = current_time
                    break
            else:
                self._topics.append(UsedTopic(name=name, timestamp=current_time))

    async def _prune(self):
        """Remove expired topics."""
        now = datetime.now(timezone.utc)
        initial_count = len(self._topics)

        self._topics = [topic for topic in self._topics if now - topic.timestamp <= self._ttl]
        pruned_count = initial_count - len(self._topics)

        if pruned_count > 0:
            self._logger.debug(f"{pruned_count} topic(s) pruned.")

    async def flush(self):
        """Prune expired topics and save to the file."""
        await self._prune()
        with open(self._file_path, "wb") as f:
            pickle.dump(self._topics, f)
        self._logger.info("Used topics flushed.")

    async def load(self):
        """Load topics from the file and prune expired ones."""
        if not os.path.exists(self._file_path):
            self._topics = []
            self._logger.debug("No topics to load.")
            return

        if os.path.getsize(self._file_path) == 0:
            self._topics = []
            self._logger.debug("No topics to load.")
            return

        with open(self._file_path, "rb") as f:
            self._topics = pickle.load(f)

        await self._prune()
        self._logger.debug(f"{len(self._topics)} topic(s) loaded.")

        if self._topics:
            next_to_prune = min(self._topics, key=lambda t: t.timestamp)
            time_to_prune = (next_to_prune.timestamp + self._ttl) - datetime.now(timezone.utc)
            minutes, seconds = divmod(time_to_prune.total_seconds(), 60)
            hours, minutes = divmod(minutes, 60)
            self._logger.debug(f"Next topic to be pruned: '{next_to_prune.name}' in {int(hours)} hour(s) and {int(minutes)} minute(s).")