import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from runtime_tests.game_analysis.game_message_embedder import GameMessageEmbedder


def main():
    embedder = GameMessageEmbedder()
    print(f"pending game ids: {embedder.pending_game_ids()}")
    embedder.run()


if __name__ == "__main__":
    main()
