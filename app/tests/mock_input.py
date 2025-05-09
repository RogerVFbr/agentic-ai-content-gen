import json

import os


class MockInput:

    @classmethod
    def get(cls) -> dict:
        """
        Read the mock_event.json file and return its contents as a dictionary.
        """
        file_path = os.path.join(os.getcwd(), 'mock_event.json')
        with open(file_path, 'r') as file:
            return json.load(file)