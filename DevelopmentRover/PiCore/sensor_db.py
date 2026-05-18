import sqlite3
import time

DB_PATH = "rover_sensors.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS temperature_readings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature_c REAL    NOT NULL,
    timestamp     INTEGER NOT NULL
);
"""

INSERT_READING = """
INSERT INTO temperature_readings (temperature_c, timestamp)
VALUES (?, ?);
"""

SELECT_READINGS = """
SELECT id, temperature_c, timestamp
FROM temperature_readings
ORDER BY timestamp DESC
LIMIT ?;
"""


def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute(CREATE_TABLE)
    con.commit()
    con.close()


def log_temperature(temperature_c):
    con = sqlite3.connect(DB_PATH)
    con.execute(INSERT_READING, (temperature_c, int(time.time())))
    con.commit()
    con.close()


def get_temperatures(limit=100):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(SELECT_READINGS, (limit,)).fetchall()
    con.close()
    return rows
