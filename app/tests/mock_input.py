import json

import os


class MockInput:

    @classmethod
    def get_crewai(cls) -> dict:
        """
        Read the mock_event.json file and return its contents as a dictionary.
        """
        file_path = os.path.join(os.getcwd(), 'mock_event.json')
        with open(file_path, 'r') as file:
            return json.load(file)

    @classmethod
    def get_langgraph(cls) -> dict:
        return {
            "raw_input": (
                "Roger Freret is a Grammy-nominated audio engineer and senior software architect "
                "at a major Brazilian bank. He has worked with Antonio Adolfo, Leo Gandelman, Blitz, "
                "and Flavio Venturini. He's also a certified AWS expert and speaker on DevOps and cloud architecture."
            )
        }