"""Database initialization and master data seeding pipeline for Cluj-Napoca.

Ensures the physical storage matrices are fully compliant with relational layout
blueprints and PEP 8 geometric formatting limits across all execution environments.
"""

from __future__ import annotations

import logging
import os
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from typing import Final

# Configuration layer targeting enterprise logging output targets
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER: Final[logging.Logger] = logging.getLogger("SmartCity.Seeder")

# Static station metadata matrices representing all 7 localized smart city nodes
STATIONS_PAYLOAD: Final[list[tuple[int, str, float, float]]] = [
    (1, "Mărăști - Sens Giratoriu", 46.7761, 23.6144),
    (2, "Mănăștur - Str. Primăverii", 46.7583, 23.5512),
    (3, "Piața Unirii - Centru Urban", 46.7712, 23.5896),
    (4, "Gheorgheni - Iulius Area", 46.7731, 23.6238),
    (5, "Zorilor - Observatorului", 46.7534, 23.5861),
    (6, "Grădini Mănăștur - Calea Florești", 46.7562, 23.5394),
    (7, "Iris - Zona Industrială", 46.7932, 23.6015),
]


def seed_relational_infrastructure() -> None:
    """Execute target queries synchronously inside automated transaction wrappers."""
    LOGGER.info("Starting production database schema mapping verification...")

    env_path = os.environ.get("DATABASE_PATH")
    db_file: Final[str] = env_path if env_path else "app.db"

    try:
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            # 1. Ensure structural tables exist in pure execution environments (CI/CD)
            LOGGER.info("Enforcing DDL structure alignment maps...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    noise_level REAL NOT NULL,
                    traffic_load REAL NOT NULL,
                    air_quality REAL NOT NULL,
                    soil_moisture REAL NOT NULL,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    sensor_id INTEGER PRIMARY KEY,
                    temp_limit REAL NOT NULL DEFAULT 32.0,
                    noise_limit REAL NOT NULL DEFAULT 75.0,
                    traffic_limit REAL NOT NULL DEFAULT 80.0,
                    air_limit REAL NOT NULL DEFAULT 80.0,
                    soil_limit REAL NOT NULL DEFAULT 35.0,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
                );
            """)

            # 2. Purge pre-existing telemetry records to maintain transaction idempotency
            LOGGER.info("Clearing legacy historical sensory matrices...")
            cursor.execute("DELETE FROM city_stats;")
            cursor.execute("DELETE FROM settings;")
            cursor.execute("DELETE FROM sensors;")

            # 3. Insert geographic telemetry master nodes
            LOGGER.info("Mapping spatial sensor deployment coordinates into 'sensors'...")
            for s_id, s_name, s_lat, s_lon in STATIONS_PAYLOAD:
                cursor.execute(
                    "INSERT INTO sensors (id, name, latitude, longitude) VALUES (?, ?, ?, ?);",
                    (s_id, s_name, s_lat, s_lon),
                )

            # Configure 5-column baseline localized warning limits
            LOGGER.info("Seeding custom fine-tuned micro-climate boundary parameters...")
            insert_settings_sql = """
                INSERT INTO settings (
                    sensor_id, temp_limit, noise_limit, traffic_limit, air_limit, soil_limit
                ) VALUES (?, ?, ?, ?, ?, ?);
            """
            for s_id, _, _, _ in STATIONS_PAYLOAD:
                cursor.execute(insert_settings_sql, (s_id, 32.0, 75.0, 80.0, 80.0, 35.0))

            # 5. Generate structured multi-horizon mock sensor dataset timelines
            LOGGER.info("Simulating multi-horizon chronological telemetry intervals...")
            insert_telemetry_sql = """
                INSERT INTO city_stats (
                    sensor_id, timestamp, temperature, noise_level,
                    traffic_load, air_quality, soil_moisture
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """

            base_time = datetime.now(UTC)
            for s_id, _, _, _ in STATIONS_PAYLOAD:
                for step in range(12):
                    target_time = base_time - timedelta(hours=step)
                    cursor.execute(
                        insert_telemetry_sql,
                        (
                            s_id,
                            target_time.strftime("%Y-%m-%d %H:%M:%S"),
                            18.5 + (step * 0.4),
                            55.0 + (step % 3 * 5.0),
                            float((40.0 + (step * 4.5)) % 55.0),
                            42.0 + (step * 2.0),
                            60.0 - (step * 1.2),
                        ),
                    )

            conn.commit()
            LOGGER.info("✨ Relational database initialization pipeline executed successfully.")

    except Exception as exc:
        LOGGER.critical("ACID pipeline rollback triggered due to execution failure: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    seed_relational_infrastructure()
