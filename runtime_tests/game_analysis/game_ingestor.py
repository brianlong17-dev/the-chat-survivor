import glob
import os
import sqlite3

from runtime_tests.game_analysis.game_analyser import DB_PATH, DemoGameError, GameAnalyser

GAME_LOG_DIR = "logs/gamelogs"
MIN_BYTES = 100 * 1024


def _create_messages_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            game_id TEXT,
            message_id INTEGER,
            round INTEGER,
            name TEXT,
            message TEXT,
            PRIMARY KEY (game_id, message_id)
        )
    """)
    conn.commit()
    conn.close()


def _ingested_game_ids():
    _create_messages_table()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT DISTINCT game_id FROM messages").fetchall()
    conn.close()
    return {row[0] for row in rows}


def pending_game_ids():
    candidates = []
    for path in glob.glob(os.path.join(GAME_LOG_DIR, "*.jsonl")):
        if os.path.getsize(path) >= MIN_BYTES:
            candidates.append(os.path.basename(path).replace(".jsonl", "").split("_")[-1])

    ingested = _ingested_game_ids()
    return [game_id for game_id in candidates if game_id not in ingested]


class GameIngestor:
    """Reads one game log file into memory and writes its raw messages to the DB."""

    def __init__(self, game_id):
        self.game_id = game_id
        _create_messages_table()

    def already_ingested(self):
        return self.game_id in _ingested_game_ids()

    def ingest(self):
        analyser = GameAnalyser(self.game_id)
        rows = [
            (self.game_id, entry.id, entry.round, entry.name, entry.message)
            for entry in analyser.game_log
        ]
        conn = sqlite3.connect(DB_PATH)
        conn.executemany(
            """INSERT OR REPLACE INTO messages (game_id, message_id, round, name, message)
               VALUES (?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        conn.close()
        return len(rows)

    def run(self):
        if self.already_ingested():
            print(f"{self.game_id}: already ingested")
            return
        try:
            count = self.ingest()
        except DemoGameError:
            print(f"{self.game_id}: skipped (demo game)")
            return
        print(f"{self.game_id}: ingested {count} messages")
