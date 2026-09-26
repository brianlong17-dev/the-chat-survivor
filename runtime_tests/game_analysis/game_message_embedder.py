import array
import sqlite3
import time

from runtime_tests.game_analysis.game_analyser import DB_PATH

EMBED_DIM = 256

MODEL_HASHED_BOW = "hashed_bow_v1"
MODEL_GEMINI = "gemini-embedding-001"

DEFAULT_MODEL_VERSION = MODEL_HASHED_BOW

# Games known to have run with a non-standard agent class (AgenticPlayerFreeEvolution /
# AgenticPlayerSteepDecline) instead of the normal Debater — identified by their stilted,
# optimizer-brained dialogue register. Not recoverable from the game logs themselves.
CONTROL_GAME_IDS = {
    "1c4022", "912b08",  # originally flagged manually
    "1b4843", "aea406", "e6dd5e", "cf03f1", "da23a5", "33be27", "a4cd8c", "178692",  # found 2026-09-25
}


class GameMessageEmbedder:
    """Embeds messages already ingested into the DB and pushes the vectors back to it."""

    GEMINI_BATCH_LIMIT = 100
    GEMINI_TASK_TYPE = "SEMANTIC_SIMILARITY"
    GEMINI_MAX_RETRIES = 8
    GEMINI_BACKOFF_BASE = 4

    def __init__(self, model_version=DEFAULT_MODEL_VERSION):
        self.model_version = model_version
        self._gemini_client = None
        self._create_db()

    def _create_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                message_id INTEGER,
                model_version TEXT,
                game_id TEXT,
                round INTEGER,
                name TEXT,
                embedding BLOB,
                is_control INTEGER DEFAULT 0,
                PRIMARY KEY (game_id, message_id, model_version)
            )
        """)
        cols = {row[1] for row in conn.execute("PRAGMA table_info(embeddings)")}
        if "is_control" not in cols:
            conn.execute("ALTER TABLE embeddings ADD COLUMN is_control INTEGER DEFAULT 0")
        conn.commit()
        conn.close()

    #-------- pending games ---------#

    def pending_game_ids(self):
        conn = sqlite3.connect(DB_PATH)
        all_ids = {row[0] for row in conn.execute("SELECT DISTINCT game_id FROM messages")}
        embedded_ids = {
            row[0] for row in conn.execute(
                "SELECT DISTINCT game_id FROM embeddings WHERE model_version = ?", (self.model_version,)
            )
        }
        conn.close()
        return sorted(all_ids - embedded_ids)

    #-------- embedding a game ---------#

    def _messages_for_game(self, game_id):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT message_id, round, name, message FROM messages WHERE game_id = ? ORDER BY message_id",
            (game_id,),
        ).fetchall()
        conn.close()
        return rows

    def embed_game(self, game_id):
        rows = self._messages_for_game(game_id)
        if not rows:
            raise ValueError(f"no ingested messages for game_id {game_id!r} — run GameIngestor first")

        vectors = self._embed_batch([message for _, _, _, message in rows])
        is_control = int(game_id in CONTROL_GAME_IDS)
        db_rows = [
            (message_id, self.model_version, game_id, round_num, name, array.array("d", vector).tobytes(), is_control)
            for (message_id, round_num, name, message), vector in zip(rows, vectors)
        ]

        conn = sqlite3.connect(DB_PATH)
        conn.executemany(
            """INSERT OR REPLACE INTO embeddings
               (message_id, model_version, game_id, round, name, embedding, is_control)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            db_rows,
        )
        conn.commit()
        conn.close()

    def run(self):
        for game_id in self.pending_game_ids():
            self.embed_game(game_id)
            print(f"{game_id}: embedded ({self.model_version})")

    #-------- embedding implementations ---------#

    def _embed_batch(self, texts):
        if self.model_version == MODEL_HASHED_BOW:
            return [self._hash_embed(t) for t in texts]
        if self.model_version == MODEL_GEMINI:
            return self._gemini_embed(texts)
        raise ValueError(f"no embedding implementation for model_version {self.model_version!r}")

    def _hash_embed(self, text):
        import zlib

        vec = [0.0] * EMBED_DIM
        for word in text.lower().split():
            vec[zlib.crc32(word.encode()) % EMBED_DIM] += 1.0
        return vec

    #-------- gemini embedding ---------#

    def _gemini_client_lazy(self):
        if self._gemini_client is None:
            from core.api_client.api_client_setup import create_genai_client

            self._gemini_client = create_genai_client()
        return self._gemini_client

    def _gemini_embed(self, texts):
        import google.genai.types as types

        client = self._gemini_client_lazy()
        config = types.EmbedContentConfig(
            output_dimensionality=EMBED_DIM,
            task_type=self.GEMINI_TASK_TYPE,
        )

        vectors = []
        for start in range(0, len(texts), self.GEMINI_BATCH_LIMIT):
            chunk = texts[start:start + self.GEMINI_BATCH_LIMIT]
            response = self._embed_chunk_with_backoff(client, chunk, config)
            vectors.extend(list(e.values) for e in response.embeddings)

        if len(vectors) != len(texts):
            raise RuntimeError(f"gemini returned {len(vectors)} embeddings for {len(texts)} texts")
        return vectors

    def _embed_chunk_with_backoff(self, client, chunk, config):
        from core.api_client.api_client import _is_rate_limit

        for attempt in range(self.GEMINI_MAX_RETRIES):
            try:
                return client.models.embed_content(model=MODEL_GEMINI, contents=chunk, config=config)
            except Exception as e:
                if not _is_rate_limit(e) or attempt == self.GEMINI_MAX_RETRIES - 1:
                    raise
                wait = self.GEMINI_BACKOFF_BASE * (2 ** attempt)
                print(f"gemini embedding 429 — waiting {wait}s (retry {attempt + 1}/{self.GEMINI_MAX_RETRIES - 1})")
                time.sleep(wait)
