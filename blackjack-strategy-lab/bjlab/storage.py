"""Persistence: SQLite cumulative aggregates + JSONL run log for check-ins."""
import json
import os
import time

_HERE = os.path.dirname(__file__)
ROOT = os.path.dirname(_HERE)
DB_PATH = os.path.join(ROOT, "data", "lab.db")
LOG_PATH = os.path.join(ROOT, "logs", "runs.jsonl")

_FIELDS = ["hands", "sum_net", "sum_sq", "sum_wagered", "shoes", "shoes_pos",
           "best_shoes", "shoe_net_sum", "shoe_net_sq"]


def connect(path=DB_PATH):
    import sqlite3
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cols = ", ".join(f"{f} REAL" for f in _FIELDS)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS tourney (
            config TEXT, strategy TEXT, {cols},
            PRIMARY KEY (config, strategy)
        )""")
    conn.commit()
    return conn


def accumulate(conn, config, agg):
    for strategy, a in agg.items():
        placeholders = ", ".join("?" for _ in _FIELDS)
        updates = ", ".join(f"{f} = {f} + excluded.{f}" for f in _FIELDS)
        vals = [config, strategy] + [a[f] for f in _FIELDS]
        conn.execute(f"""
            INSERT INTO tourney (config, strategy, {", ".join(_FIELDS)})
            VALUES (?, ?, {placeholders})
            ON CONFLICT(config, strategy) DO UPDATE SET {updates}
        """, vals)
    conn.commit()


def load(conn, config):
    rows = conn.execute(
        f"SELECT strategy, {', '.join(_FIELDS)} FROM tourney WHERE config=?",
        (config,)).fetchall()
    out = {}
    for row in rows:
        out[row[0]] = dict(zip(_FIELDS, row[1:]))
    return out


def log_run(config, num_shoes, snapshot):
    """Append one JSONL line summarizing this run - the file you share at check-ins."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "config": config,
        "shoes_this_run": num_shoes,
        "strategies": snapshot,     # list of {name, ev_per_100, di, edge_pct, hands}
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(rec) + "\n")
