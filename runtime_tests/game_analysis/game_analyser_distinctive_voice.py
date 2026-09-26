import array
import math
import random
import sqlite3
import time

from runtime_tests.game_analysis.game_analyser import GameAnalyser
from runtime_tests.game_analysis.game_message_embedder import (
    DB_PATH,
    DEFAULT_MODEL_VERSION,
    EMBED_DIM,
)


def _centroid(model_version, is_control):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT embedding FROM embeddings WHERE model_version = ? AND is_control = ?",
        (model_version, int(is_control)),
    ).fetchall()
    conn.close()

    vectors = [array.array("d", blob).tolist() for (blob,) in rows]
    return [sum(col) / len(vectors) for col in zip(*vectors)]


def calculate_global_centroid(model_version):
    return _centroid(model_version, is_control=False)


def calculate_control_centroid(model_version):
    return _centroid(model_version, is_control=True)


def mark_control_game(game_id, is_control=True):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE embeddings SET is_control = ? WHERE game_id = ?", (int(is_control), game_id))
    conn.execute("UPDATE voice_scores SET is_control = ? WHERE game_id = ?", (int(is_control), game_id))
    conn.commit()
    conn.close()


def clear_scores(model_version=None):
    conn = sqlite3.connect(DB_PATH)
    if model_version is None:
        conn.execute("DROP TABLE IF EXISTS voice_scores")
    else:
        conn.execute("DELETE FROM voice_scores WHERE model_version = ?", (model_version,))
    conn.commit()
    conn.close()


def fetch_scores(model_version, include_control=False):
    conn = sqlite3.connect(DB_PATH)
    clause = "" if include_control else "AND is_control = 0"
    rows = conn.execute(
        f"""SELECT game_id, character_name, score, mean_distance, norm_slope, n_rounds, is_finalist
            FROM voice_scores WHERE model_version = ? {clause}""",
        (model_version,),
    ).fetchall()
    conn.close()
    return rows


class DistinctiveVoiceAnalyser(GameAnalyser):
    def __init__(self, game_id=None, model_version=DEFAULT_MODEL_VERSION, centroid_source="global"):
        super().__init__(game_id)
        self.model_version = model_version
        self.centroid_source = centroid_source
        self._centroid = None
        self._create_db()

    def _create_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS voice_scores (
                game_id TEXT,
                model_version TEXT,
                character_name TEXT,
                score REAL,
                mean_distance REAL,
                norm_slope REAL,
                n_rounds INTEGER,
                is_finalist INTEGER,
                is_control INTEGER DEFAULT 0,
                computed_at REAL,
                PRIMARY KEY (game_id, model_version, character_name)
            )
        """)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(voice_scores)")}
        if "is_control" not in cols:
            conn.execute("ALTER TABLE voice_scores ADD COLUMN is_control INTEGER DEFAULT 0")
        conn.commit()
        conn.close()

    def _load_embeddings(self):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT message_id, embedding FROM embeddings WHERE game_id = ? AND model_version = ?",
            (self.game_id, self.model_version),
        ).fetchall()
        conn.close()

        vectors_by_id = {message_id: array.array("d", blob).tolist() for message_id, blob in rows}
        for entry in self.game_log:
            entry.embedding = vectors_by_id.get(entry.id)

    #-------- analysis ---------#

    def centroid(self):
        if self._centroid is None:
            if self.centroid_source == "control":
                self._centroid = calculate_control_centroid(self.model_version)
            elif self.centroid_source == "random":
                rng = random.Random(0)
                self._centroid = [rng.gauss(0, 1) for _ in range(EMBED_DIM)]
            else:
                self._centroid = calculate_global_centroid(self.model_version)
        return self._centroid

    def chracter_scores_per_round(self, character_name):
        centroid = self.centroid()

        vectors_by_round = {}
        for entry in self.game_log:
            if entry.name == character_name:
                vectors_by_round.setdefault(entry.round, []).append(entry.embedding)

        scores = []
        for round_num in sorted(vectors_by_round):
            vectors = vectors_by_round[round_num]
            round_vector = [sum(col) / len(vectors) for col in zip(*vectors)]
            scores.append((round_num, self._distance_to_centroid(round_vector, centroid)))
        return scores

    def _slope_score(self, character_name):
        return self._linear_slope(self.chracter_scores_per_round(character_name))

    @staticmethod
    def _linear_slope(points):
        if len(points) < 2:
            return None

        n = len(points)
        mean_x = sum(x for x, _ in points) / n
        mean_y = sum(y for _, y in points) / n
        cov = sum((x - mean_x) * (y - mean_y) for x, y in points)
        var = sum((x - mean_x) ** 2 for x, _ in points)
        return cov / var

    def finalists(self):
        rounds = sorted({entry.round for entry in self.game_log})
        if len(rounds) < 2:
            return []
        penultimate = rounds[-2]
        return sorted({entry.name for entry in self.game_log if entry.round == penultimate})

    def _game_score(self):
        finalists = self.finalists()
        if len(finalists) < 2:
            return None

        slopes = [self._slope_score(name) for name in finalists]
        slopes = [slope for slope in slopes if slope is not None]

        if not slopes:
            return None
        return sum(slopes) / len(slopes)

    #-------- score persistence ---------#

    def score_game(self):
        finalists = set(self.finalists())
        if not 2 <= len(finalists) <= 3:
            return None

        now = time.time()
        is_control = self._is_control_game()
        rows = []
        for name in self.character_list():
            points = self.chracter_scores_per_round(name)
            slope = self._linear_slope(points)
            mean_distance = sum(d for _, d in points) / len(points) if points else None
            norm_slope = slope / mean_distance if slope is not None and mean_distance else None
            rows.append((
                self.game_id, self.model_version, name,
                slope, mean_distance, norm_slope, len(points), int(name in finalists),
                is_control, now,
            ))
        self._push_scores_to_db(rows)
        return self._game_score()

    def _is_control_game(self):
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT MAX(is_control) FROM embeddings WHERE game_id = ?", (self.game_id,)
        ).fetchone()
        conn.close()
        return row[0] or 0

    def _push_scores_to_db(self, rows):
        conn = sqlite3.connect(DB_PATH)
        conn.executemany(
            """INSERT OR REPLACE INTO voice_scores
               (game_id, model_version, character_name, score, mean_distance, norm_slope,
                n_rounds, is_finalist, is_control, computed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        conn.close()

    def _distance_to_centroid(self, vector, centroid):
        dot = sum(a * b for a, b in zip(vector, centroid))
        norm = math.sqrt(sum(a * a for a in vector)) * math.sqrt(sum(b * b for b in centroid))
        return 1.0 - dot / norm
