import os

from crosscutting.logging.app_logger import AppLogger
import tweepy

class SocialNetworksRepository:

    def __init__(self,
                 logger: AppLogger):

        self._logger = logger
        self._client = None
        self._access_token = None

    async def tweet(self, message: str) -> dict:
        """Publishes a short message on Twitter (X)."""

        if not self._client:
            self._client = tweepy.Client(
                consumer_key=os.getenv("X_CONSUMER_KEY"),
                consumer_secret=os.getenv("X_CONSUMER_SECRET"),
                access_token=os.getenv("X_ACCESS_TOKEN"),
                access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
            )

        try:
            _ = self._client.create_tweet(
                text=message,
                media_ids=None,  # Add media IDs if attaching media
                poll_options=None,  # Add poll options if creating a poll
                user_auth=True  # Use OAuth 1.0a User Context
            )
        except Exception as e:
            return {"success": False, "reason": str(e).replace('\n', ' ') + " Try something else"}


        return {"success": True, "reason": "Tweet posted successfully."}