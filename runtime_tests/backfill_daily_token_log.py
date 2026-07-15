import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.shared_helpers import get_master_logger
from web.rate_limits import _connect


def main():
    today = date.today().isoformat()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT date, games, demos, tokens FROM daily_counts WHERE date < ? ORDER BY date",
            (today,),
        ).fetchall()

    already_logged = _logged_dates()
    logger = get_master_logger("daily_tokens", "daily_token_log")

    written = 0
    for day, games, demos, tokens in rows:
        if day in already_logged:
            continue
        logger.info(json.dumps({"date": day, "games": games, "demos": demos, "tokens": tokens}))
        written += 1
        print(f"logged {day}: games={games} demos={demos} tokens={tokens}")

    print(f"\n{written} day(s) backfilled, {len(rows) - written} already present, {today} left for the live rollup.")


def _logged_dates() -> set[str]:
    from core.shared_helpers import MASTER_LOG_DIR
    import os
    path = os.path.join(MASTER_LOG_DIR, "daily_token_log")
    if not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {json.loads(line)["date"] for line in f if line.strip()}


if __name__ == "__main__":
    main()
