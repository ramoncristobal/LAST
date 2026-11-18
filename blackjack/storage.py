"""SQLite persistence. Aggregates accumulate across every run so data grows over time."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "results.db")


def connect(path=DB_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS aggregate (
            config TEXT, mode TEXT,
            hands INTEGER, sum_net REAL, sum_sq REAL, sum_wagered REAL,
            PRIMARY KEY (config, mode)
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS count_edge (
            config TEXT, tc INTEGER,
            hands INTEGER, sum_net REAL, sum_wagered REAL,
            PRIMARY KEY (config, tc)
        )""")
    conn.commit()
    return conn


def update_aggregate(conn, config, mode, hands, sum_net, sum_sq, sum_wagered):
    conn.execute("""
        INSERT INTO aggregate (config, mode, hands, sum_net, sum_sq, sum_wagered)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(config, mode) DO UPDATE SET
            hands = hands + excluded.hands,
            sum_net = sum_net + excluded.sum_net,
            sum_sq = sum_sq + excluded.sum_sq,
            sum_wagered = sum_wagered + excluded.sum_wagered
    """, (config, mode, hands, sum_net, sum_sq, sum_wagered))


def update_count_edge(conn, config, buckets):
    # buckets: dict tc -> (hands, sum_net, sum_wagered)
    for tc, (h, net, wag) in buckets.items():
        conn.execute("""
            INSERT INTO count_edge (config, tc, hands, sum_net, sum_wagered)
            VALUES (?,?,?,?,?)
            ON CONFLICT(config, tc) DO UPDATE SET
                hands = hands + excluded.hands,
                sum_net = sum_net + excluded.sum_net,
                sum_wagered = sum_wagered + excluded.sum_wagered
        """, (config, int(tc), h, net, wag))


def get_aggregate(conn, config, mode):
    row = conn.execute(
        "SELECT hands, sum_net, sum_sq, sum_wagered FROM aggregate "
        "WHERE config=? AND mode=?", (config, mode)).fetchone()
    return row


def get_count_edge(conn, config):
    return conn.execute(
        "SELECT tc, hands, sum_net, sum_wagered FROM count_edge "
        "WHERE config=? ORDER BY tc", (config,)).fetchall()
