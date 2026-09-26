import glob
import os
import re
import sys
from collections import namedtuple
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from runtime_tests.game_analysis.game_analyser_distinctive_voice import (
    MODEL_GEMINI,
    DistinctiveVoiceAnalyser,
    calculate_control_centroid,
    calculate_global_centroid,
    clear_scores,
    fetch_scores,
)
from runtime_tests.game_analysis.game_ingestor import GAME_LOG_DIR, GameIngestor, pending_game_ids
from runtime_tests.game_analysis.game_message_embedder import GameMessageEmbedder

PLOT_PATH = "runtime_tests/game_analysis/outputs/game_scores_gemini.png"

Row = namedtuple("Row", "game_id name score mean_distance norm_slope n_rounds is_finalist")


def _rows():
    return [Row(*r) for r in fetch_scores(MODEL_GEMINI)]


def ingest_and_score_all_games():
    clear_scores()
    for game_id in pending_game_ids():
        GameIngestor(game_id).run()

    embedder = GameMessageEmbedder(model_version=MODEL_GEMINI)
    candidate_ids = embedder.pending_game_ids()
    print(f"{len(candidate_ids)} candidate games")

    for game_id in candidate_ids:
        try:
            embedder.embed_game(game_id)
            analyser = DistinctiveVoiceAnalyser(game_id, model_version=MODEL_GEMINI)
            analyser._load_embeddings()
            analyser.score_game()
        except Exception as e:
            print(f"{game_id}: FAILED — {type(e).__name__}: {e}")


def _fmt(value):
    return f"{value:+.5f}" if value is not None else "   n/a  "


def print_scores():
    by_game = {}
    for row in _rows():
        by_game.setdefault(row.game_id, []).append(row)

    for game_id, rows in by_game.items():
        print(f"\n{game_id}")
        for row in sorted(rows, key=lambda r: r.name):
            marker = " *" if row.is_finalist else ""
            print(f"  slope {_fmt(row.score)}  dist {_fmt(row.mean_distance)}  {row.name} ({row.n_rounds} rounds){marker}")


def print_by_character():
    by_character = {}
    for row in _rows():
        by_character.setdefault(row.name, []).append(row)

    def mean_slope(rows):
        vals = [r.score for r in rows if r.score is not None]
        return sum(vals) / len(vals) if vals else 0.0

    for name in sorted(by_character, key=lambda n: mean_slope(by_character[n])):
        rows = by_character[name]
        print(f"\n{name}  (mean slope {mean_slope(rows):+.5f}, {len(rows)} games)")
        for row in sorted(rows, key=lambda r: r.game_id):
            marker = " *" if row.is_finalist else ""
            print(f"  slope {_fmt(row.score)}  dist {_fmt(row.mean_distance)}  {row.game_id} ({row.n_rounds} rounds){marker}")


def print_semifinalist_averages(min_games=3):
    by_character = {}
    for row in _rows():
        if row.is_finalist:
            by_character.setdefault(row.name, []).append(row)

    def mean(vals):
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    summary = [
        (
            name,
            mean([r.mean_distance for r in rows]),
            mean([r.score for r in rows]),
            mean([r.norm_slope for r in rows]),
            len(rows),
        )
        for name, rows in by_character.items()
        if len(rows) >= min_games
    ]

    print(f"{'distinctiveness':>15}  {'slope':>9}  {'norm_slope':>10}  character")
    for name, dist, slope, norm, n in sorted(summary, key=lambda x: x[1], reverse=True):
        print(f"{_fmt(dist):>15}  {_fmt(slope):>9}  {_fmt(norm):>10}  {name} ({n} semis)")


def _game_date(game_id):
    path = glob.glob(os.path.join(GAME_LOG_DIR, f"*{game_id}*.jsonl"))[0]
    return datetime.strptime(re.search(r"(\d{8}_\d{6})", os.path.basename(path)).group(1), "%Y%m%d_%H%M%S")


def plot_game_scores():
    by_game = {}
    for row in _rows():
        if row.is_finalist and row.score is not None:
            by_game.setdefault(row.game_id, []).append(row.score)

    points = sorted(
        (_game_date(game_id), sum(scores) / len(scores))
        for game_id, scores in by_game.items()
        if len(scores) == 3
    )
    print(f"{len(points)} games with 3 semi-finalists")

    import matplotlib.pyplot as plt

    dates, scores = zip(*points)
    plt.plot(dates, scores, marker="o")
    plt.axhline(0, color="gray", linewidth=0.5)
    plt.xlabel("game date")
    plt.ylabel("game score (mean semi-finalist slope)")
    plt.title("Distinctive voice convergence over time (gemini)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(PLOT_PATH)
    print(f"saved plot to {PLOT_PATH}")


def plot_distance_scores(centroid_source="control"):
    game_ids = sorted({r.game_id for r in _rows()}, key=_game_date)
    fixed_centroid = calculate_control_centroid(MODEL_GEMINI) if centroid_source == "control" else None

    ranked = []
    for game_id in game_ids:
        analyser = DistinctiveVoiceAnalyser(game_id, model_version=MODEL_GEMINI, centroid_source=centroid_source)
        if fixed_centroid is not None:
            analyser._centroid = fixed_centroid
        analyser._load_embeddings()
        finalists = analyser.finalists()
        if len(finalists) != 3:
            continue
        dists = []
        for name in finalists:
            points = analyser.chracter_scores_per_round(name)
            dists.append(sum(d for _, d in points) / len(points))
        ranked.append((_game_date(game_id), game_id, sum(dists) / len(dists)))

    print(f"{len(ranked)} games ranked by finalist mean distance from the {centroid_source} centroid (least distinctive first)\n")
    for date, game_id, dist in sorted(ranked, key=lambda x: x[2]):
        print(f"  {dist:.5f}  {game_id}  {date:%Y-%m-%d %H:%M}")

    import matplotlib.pyplot as plt

    dates = [d for d, _, _ in ranked]
    dists = [x for _, _, x in ranked]
    plt.plot(dates, dists, marker="o")
    plt.xlabel("game date")
    plt.ylabel(f"finalist mean distance from {centroid_source} centroid")
    plt.title(f"Finalist distinctiveness vs the {centroid_source} centroid over time")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = f"runtime_tests/game_analysis/outputs/game_distance_{centroid_source}.png"
    plt.savefig(path)
    print(f"\nsaved plot to {path}")


def plot_centroid_scores(centroid_source="control"):
    plot_path = f"runtime_tests/game_analysis/outputs/game_scores_{centroid_source}_centroid.png"
    game_ids = sorted({r.game_id for r in _rows()}, key=_game_date)
    fixed_centroid = calculate_control_centroid(MODEL_GEMINI) if centroid_source == "control" else None

    ranked = []
    for game_id in game_ids:
        analyser = DistinctiveVoiceAnalyser(game_id, model_version=MODEL_GEMINI, centroid_source=centroid_source)
        if fixed_centroid is not None:
            analyser._centroid = fixed_centroid
        analyser._load_embeddings()
        if len(analyser.finalists()) != 3:
            continue
        score = analyser._game_score()
        if score is None:
            continue
        ranked.append((_game_date(game_id), game_id, score))

    print(f"{len(ranked)} games ranked by slope vs the {centroid_source} centroid (most convergent first)\n")
    for date, game_id, score in sorted(ranked, key=lambda x: x[2]):
        print(f"  {score:+.5f}  {game_id}  {date:%Y-%m-%d %H:%M}")

    import matplotlib.pyplot as plt

    dates = [d for d, _, _ in ranked]
    scores = [s for _, _, s in ranked]
    plt.plot(dates, scores, marker="o")
    plt.axhline(0, color="gray", linewidth=0.5)
    plt.xlabel("game date")
    plt.ylabel(f"game score (mean semi-finalist slope vs {centroid_source} centroid)")
    plt.title(f"Movement toward the {centroid_source} centroid over time")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"\nsaved plot to {plot_path}")


def print_control():
    import math
    import sqlite3

    conn = sqlite3.connect("data/embeddings.db")
    games = conn.execute(
        "SELECT game_id, COUNT(*) FROM embeddings WHERE is_control = 1 GROUP BY game_id"
    ).fetchall()
    conn.close()

    print("control games (excluded from ordinary retrieval + global centroid):")
    for game_id, n in games:
        print(f"  {game_id} ({n} messages)")

    control = calculate_control_centroid(MODEL_GEMINI)
    glob = calculate_global_centroid(MODEL_GEMINI)
    dot = sum(a * b for a, b in zip(control, glob))
    norm = math.sqrt(sum(a * a for a in control)) * math.sqrt(sum(b * b for b in glob))
    print(f"\ncosine distance between control and global centroid: {1 - dot / norm:.6f}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "control":
        print_control()
    elif arg == "control-plot":
        plot_centroid_scores("control")
    elif arg == "random-plot":
        plot_centroid_scores("random")
    elif arg == "distance-plot":
        plot_distance_scores("control")
    elif arg == "print":
        print_scores()
    elif arg == "by-character":
        print_by_character()
    elif arg == "averages":
        min_games = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        print_semifinalist_averages(min_games)
    elif arg == "plot":
        plot_game_scores()
    else:
        ingest_and_score_all_games()
