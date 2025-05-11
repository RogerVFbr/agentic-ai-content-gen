class MockInput:

    @classmethod
    def get_crewai(cls) -> dict:
        return {
          "topic": "Cats",
          "current_year": 2025
        }

    @classmethod
    def get_langgraph(cls) -> dict:
        return {
            "raw_input": (
                "Roger Freret is a Grammy-nominated audio engineer and senior software architect "
                "at a major Brazilian bank. He has worked with Antonio Adolfo, Leo Gandelman, Blitz, "
                "and Flavio Venturini. He's also a certified AWS expert and speaker on DevOps and cloud architecture."
            )
        }