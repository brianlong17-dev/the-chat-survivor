import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from runtime_tests.game_analysis.game_analyser import GameAnalyser

GAME_ID = "1b4843"


def main():
    analyser = GameAnalyser(GAME_ID, source="db")
    print(f"characters: {analyser.character_list()}")
    analyser.print_messages_in_round(2)


if __name__ == "__main__":
    main()
