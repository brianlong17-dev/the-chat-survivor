import glob
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from runtime_tests.game_analysis.game_analyser_distinctive_voice import DistinctiveVoiceAnalyser
from runtime_tests.game_analysis.game_ingestor import GAME_LOG_DIR, MIN_BYTES, GameIngestor, pending_game_ids
from runtime_tests.game_analysis.game_message_embedder import GameMessageEmbedder

GAME_ID = "f30753"


def _date_from_path(path):
    match = re.search(r"(\d{8}_\d{6})", os.path.basename(path))
    return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")


def run_single_game(game_id):
    GameIngestor(game_id).run()
    GameMessageEmbedder().embed_game(game_id)

    analyser = DistinctiveVoiceAnalyser(game_id)
    analyser._load_embeddings()
    print(f"game_id: {analyser.game_id}")
    print(f"entries: {len(analyser.game_log)}")

    missing = [entry for entry in analyser.game_log if entry.embedding is None]
    print(f"entries with embedding after load: {len(analyser.game_log) - len(missing)}")
    print(f"entries missing embedding: {len(missing)}")

    finalists = analyser.finalists()
    print(f"finalists: {finalists}")
    for name in finalists:
        print(f"\n{name}:")
        for round_num, score in analyser.chracter_scores_per_round(name):
            print(f"  Round {round_num}: {score:.4f}")
        print(f"  slope: {analyser._slope_score(name):+.5f}")

    print(f"\ngame score: {analyser._game_score():+.5f}")

    print("\nRound 15 messages:")
    for entry in analyser.game_log:
        if entry.round == 15:
            print(f"  {entry.name}: {entry.message[:150]}")


def run_all_games():
    for game_id in pending_game_ids():
        GameIngestor(game_id).run()
    GameMessageEmbedder().run()

    paths = sorted(
        (p for p in glob.glob(os.path.join(GAME_LOG_DIR, "*.jsonl")) if os.path.getsize(p) >= MIN_BYTES),
        key=_date_from_path,
    )

    results = []
    for path in paths:
        game_id = os.path.basename(path).replace(".jsonl", "").split("_")[-1]
        date = _date_from_path(path)

        analyser = DistinctiveVoiceAnalyser(game_id)
        analyser._load_embeddings()
        score = analyser._game_score()
        score_str = f"{score:+.5f}" if score is not None else "n/a"
        print(f"{date}  ({game_id}): {score_str}")

        if score is not None:
            results.append((date, score))

    return results


def plot_game_scores(results):
    import matplotlib.pyplot as plt

    dates, scores = zip(*results)
    plt.plot(dates, scores, marker="o")
    plt.axhline(0, color="gray", linewidth=0.5)
    plt.xlabel("game date")
    plt.ylabel("game score (convergence slope)")
    plt.title("Distinctive voice convergence over time")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("runtime_tests/game_analysis/outputs/game_scores.png")
    print("saved plot to runtime_tests/game_analysis/outputs/game_scores.png")


if __name__ == "__main__":
    results = run_all_games()
    plot_game_scores(results)
    #run_single_game(GAME_ID)
