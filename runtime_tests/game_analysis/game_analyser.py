import glob
import json
import os
import sqlite3
from dataclasses import dataclass

GAME_LOG_DIR = "logs/gamelogs"
DB_PATH = "data/embeddings.db"


class DemoGameError(ValueError):
    pass


@dataclass
class GameEntry:
    round: int
    id: int
    name: str
    message: str
    embedding: list[float] | None = None


class GameAnalyser:

    def __init__(self, game_id=None, source="file"):
        self.game_id = game_id
        if source == "file":
            self.raw_game_log = self._create_log_from_file()
            self.game_log = self._create_proccessed_game_log()
        elif source == "db":
            self.game_log = self._create_log_from_db()
        else:
            raise ValueError(f"unknown source {source!r} — expected 'file' or 'db'")

    def _create_proccessed_game_log(self):
        entries = []
        round_num = 0
        for event in self.raw_game_log:
            if event.get("type") == "round_start":
                round_num += 1
            elif event.get("type") == "public_action" and event['speaker'].upper() != 'HOST':
                if 'Lorem ipsum dolor' in event['message']:
                    raise DemoGameError(f"This is a demo game? {self.game_id}")
                entries.append(GameEntry(
                    round=round_num,
                    id=event['message_id'],
                    name=event['speaker'],
                    message=event['message'],
                ))
        if round_num == 0:
            raise ValueError(f"no round_start events in {self._read_log_file()} — log format changed?")
        return entries

    #---- roster ----#

    def character_list(self):
        return sorted({entry.name for entry in self.game_log})

    def finalists(self):
        last_round = max(entry.round for entry in self.game_log)
        return sorted({entry.name for entry in self.game_log if entry.round == last_round})

    #---- reading files -----#

    def _create_log_from_file(self):
        file = self._read_log_file()
        if file is None:
            return None
        with open(file) as f:
            return [json.loads(line) for line in f if line.strip()]
    
        
    def _read_log_file(self):
        matches = glob.glob(os.path.join(GAME_LOG_DIR, f"*{self.game_id}*.jsonl"))
        return matches[0] if matches else None

    #---- reading db ----#

    def _create_log_from_db(self):
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT message_id, round, name, message FROM messages WHERE game_id = ? ORDER BY message_id",
            (self.game_id,),
        ).fetchall()
        conn.close()

        if not rows:
            raise ValueError(f"no ingested messages for game_id {self.game_id!r} — has it been ingested?")

        return [
            GameEntry(round=round_num, id=message_id, name=name, message=message)
            for message_id, round_num, name, message in rows
        ]

    #----- printing ----#

    def print_log(self):
        for entry in self.game_log:
            print(f"{entry.name}: {entry.message[:150]}")

    def print_messages_in_round(self, target_round):
        for entry in self.game_log:
            if entry.round == target_round:
                print(f"{entry.name}: {entry.message}")

