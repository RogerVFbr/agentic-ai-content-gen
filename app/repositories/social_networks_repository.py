from crosscutting.logging.app_logger import AppLogger


class SocialNetworksRepository():

    def __init__(self,
                 logger: AppLogger):

        self._logger = logger

    async def tweet(self, message: str) -> None:
        """Publishes a short message on Twitter (X)."""
        self._logger.info(f"Tweeted: {message}")