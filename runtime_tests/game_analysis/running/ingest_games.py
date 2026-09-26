import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from runtime_tests.game_analysis.game_ingestor import GameIngestor, pending_game_ids


def main():
    ids = pending_game_ids()
    print(f"pending game ids: {ids}")
    for game_id in ids:
        GameIngestor(game_id).run()


if __name__ == "__main__":
    main()
