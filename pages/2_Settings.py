"""Administration and system boundaries panel with dynamic per-sensor threshold controls.

Provides production-ready OOP repository wrappers, nominal SQL mapping to prevent
downstream degradation, structured memory-buffered file export layers, and integrated
sub-process ledger synchronization.
"""

from __future__ import annotations

import io
import logging
import os
import sqlite3
import sys
from pathlib import Path
from typing import Final

import pandas as pd
import streamlit as st

from app.ai.ai_interface import render_full_global_sidebar
from translations import TranslationProvider

# Path resilience framework injection targeting multipage module isolation environments
PROJECT_ROOT: Final[str] = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Initialize localized logger configuration for the panel space boundary
LOGGER: Final[logging.Logger] = logging.getLogger("SmartCity.Settings")


class SettingsRepository:
    """Manages transactional state persistence for granular system boundaries."""

    def __init__(self) -> None:
        """Initialize the repository infrastructure link wrappers using strict typing."""
        env_path = os.environ.get("DATABASE_PATH")
        self._db_path: Final[Path] = Path(env_path) if env_path else Path("app.db")

    @property
    def _active_db_path(self) -> Path:
        """Resolve the active database path safely from structural scopes."""
        return self._db_path if self._db_path.is_file() else Path("app.db")

    def load_all_sensors(self) -> list[tuple[int, str]]:
        """Fetch all registered stations to generate form navigation contexts."""
        query: Final[str] = "SELECT id, name FROM sensors ORDER BY id"
        try:
            with sqlite3.connect(str(self._active_db_path), timeout=10.0) as conn:
                return conn.execute(query).fetchall()
        except sqlite3.Error as err:
            LOGGER.error("Failed to fetch all sensors: %s", err)
            return []

    def load_sensor_threshold(self, sensor_id: int) -> dict[str, float]:
        """Fetch active alert boundary rules using nominal column mapping."""
        fallback: Final[dict[str, float]] = {
            "temperature": 32.0,
            "noise_level": 75.0,
            "traffic_load": 80.0,
            "air_quality": 80.0,
            "soil_moisture": 35.0,
        }
        query: Final[str] = """
            SELECT temp_limit, noise_limit, traffic_limit, air_limit, soil_limit
            FROM settings WHERE sensor_id = ? LIMIT 1
        """
        try:
            with sqlite3.connect(str(self._active_db_path), timeout=10.0) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, (sensor_id,))
                row = cursor.fetchone()
                if row is not None:
                    return {
                        "temperature": float(row["temp_limit"]),
                        "noise_level": float(row["noise_limit"]),
                        "traffic_load": float(row["traffic_limit"]),
                        "air_quality": float(row["air_limit"]),
                        "soil_moisture": float(row["soil_limit"]),
                    }
        except sqlite3.Error as err:
            LOGGER.error("Nominal attributes failure for sensor %d: %s", sensor_id, err)
        return fallback

    def save_sensor_threshold(
        self,
        sensor_id: int,
        temp: float,
        noise: float,
        traffic: float,
        air: float,
        soil: float,
    ) -> bool:
        """Persist configurations securely inside an atomic upsert context."""
        query: Final[str] = """
            INSERT INTO settings (
                sensor_id, temp_limit, noise_limit, traffic_limit, air_limit, soil_limit
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(sensor_id) DO UPDATE SET
                temp_limit = excluded.temp_limit,
                noise_limit = excluded.noise_limit,
                traffic_limit = excluded.traffic_limit,
                air_limit = excluded.air_limit,
                soil_limit = excluded.soil_limit
        """
        try:
            with sqlite3.connect(str(self._active_db_path), timeout=15.0) as conn:
                conn.execute(query, (sensor_id, temp, noise, traffic, air, soil))
                conn.commit()
                return True
        except sqlite3.Error as err:
            LOGGER.critical("ACID update exception for sensor %d: %s", sensor_id, err)
            return False

    def fetch_raw_telemetry_dump(self) -> pd.DataFrame:
        """Extract a flattened join matrix representing historical sensory data."""
        query: Final[str] = """
            SELECT s.name AS station_name, c.timestamp, c.temperature,
                   c.noise_level, c.traffic_load, c.air_quality, c.soil_moisture
            FROM city_stats c
            JOIN sensors s ON c.sensor_id = s.id
            ORDER BY c.timestamp DESC
        """
        try:
            with sqlite3.connect(str(self._active_db_path), timeout=15.0) as conn:
                return pd.read_sql_query(query, conn)
        except (sqlite3.Error, pd.errors.DatabaseError) as err:
            LOGGER.error("Failed to compile analytics join dump: %s", err)
            return pd.DataFrame()


class DataExportService:
    """Isolated binary spreadsheet compiling engine preventing memory leaks."""

    @staticmethod
    def generate_csv_bytes(df: pd.DataFrame) -> bytes:
        """Convert a flattened chronological dataframe dump cleanly into UTF-8 CSV bytes."""
        if df.empty:
            return b""
        return df.to_csv(index=False).encode("utf-8")

    @staticmethod
    def generate_excel_bytes(df: pd.DataFrame) -> bytes:
        """Compile a styled spreadsheet using memory-buffered XlsxWriter engines."""
        if df.empty:
            return b""
        output: Final[io.BytesIO] = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, sheet_name="Urban Telemetry", index=False)
                worksheet = writer.sheets["Urban Telemetry"]
                for idx, col in enumerate(df.columns):
                    series = df[col]
                    max_len: int = max(int(series.astype(str).map(len).max()), len(col)) + 3
                    worksheet.set_column(idx, idx, max_len)
            return output.getvalue()
        except Exception as exc:
            LOGGER.error("Spreadsheet compiler execution failure: %s", exc)
            return b""


class SettingsPage:
    """Orchestrates configuration state boundaries and administrative web forms."""

    def __init__(self) -> None:
        """Initialize the layout compilation loops and services framework."""
        self._repository: Final[SettingsRepository] = SettingsRepository()
        self._export_service: Final[DataExportService] = DataExportService()

    def enforce_authentication(self) -> None:
        """Route authorization gate protection layer validating system session state vectors."""
        if st.session_state.get("authenticated", False):
            return

        expected_token = st.secrets.get("SESSION_SECURITY_TOKEN", "")
        url_token = st.query_params.get("session_token", "")

        if expected_token and url_token == expected_token:
            st.session_state["authenticated"] = True
            return

        st.warning("Restricted access! Please authenticate on the main platform index page view.")
        st.stop()

    def display(self) -> None:
        """Execute unified interface layout compilation loops with segmented per-sensor tabs."""
        self.enforce_authentication()

        provider: Final[TranslationProvider] = TranslationProvider(
            default_language=st.session_state.get("lang", "EN")
        )
        active_translations_dict = provider.get_all_translations()

        render_full_global_sidebar(active_translations_dict)

        st.title(f"⚙️ {provider.get('settings_title')}")
        st.caption(
            "⚡ Granular Operational Configuration Framework: "
            "Adjust tailored safety margins for individual urban micro-climates."
        )
        st.divider()

        st.markdown("#### 🚀 Database Infrastructure Initialization")
        seed_col1, seed_col2 = st.columns(2)
        with seed_col1:
            seed_triggered = st.button(
                "Execute seed_db.py",
                key="btn_execute_infrastructure_seed",
                use_container_width=True,
            )
        with seed_col2:
            st.info(
                "Clicking this control vector executes the structured relational seed pipeline "
                "within an isolated environment, population-mapping all default Cluj stations."
            )

        if seed_triggered:
            with st.spinner("Synchronizing local relational database ledger tables..."):
                try:
                    from seed_db import seed_relational_infrastructure

                    seed_relational_infrastructure()
                    st.success("✨ Relational schema seeded successfully! Reloading views.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Failed to execute database initialization logic: {exc}")

        st.divider()

        st.markdown(f"#### 🚨 {provider.get('tab_alerts_cfg')} (Per-Station Fine Tuning)")

        sensors_list: Final[list[tuple[int, str]]] = self._repository.load_all_sensors()

        if not sensors_list:
            st.warning(
                "⚠️ No sensors registered inside the local relational database ledger schema. "
                "Please trigger the seed initialization block above."
            )
        else:
            tab_names: Final[list[str]] = [f"📍 {row[1]}" for row in sensors_list]
            ui_tabs = st.tabs(tab_names)

            for index, row in enumerate(sensors_list):
                sensor_id = int(row[0])
                sensor_name = str(row[1])

                with ui_tabs[index]:
                    st.write(f"Customize criteria profiles for: **{sensor_name}**")
                    current_limits = self._repository.load_sensor_threshold(sensor_id)

                    with st.form(key=f"form_sensor_node_limits_id_{sensor_id}"):
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            val_temp = st.number_input(
                                f"🌡️ {provider.get('temp')} Bound (°C)",
                                value=float(current_limits["temperature"]),
                                step=0.5,
                                key=f"input_t_{sensor_id}",
                            )
                        with col2:
                            val_noise = st.number_input(
                                f"🔊 {provider.get('noise')} Limit (dB)",
                                value=float(current_limits["noise_level"]),
                                step=1.0,
                                key=f"input_n_{sensor_id}",
                            )
                        with col3:
                            val_traffic = st.number_input(
                                f"🚗 {provider.get('traffic')} Ceiling (%)",
                                value=float(current_limits["traffic_load"]),
                                step=5.0,
                                key=f"input_tr_{sensor_id}",
                            )
                        with col4:
                            val_air = st.number_input(
                                f"🌫️ {provider.get('air_quality')} Max Index",
                                value=float(current_limits["air_quality"]),
                                step=5.0,
                                key=f"input_a_{sensor_id}",
                            )
                        with col5:
                            val_soil = st.number_input(
                                f"🌱 {provider.get('soil_moisture')} Floor (%)",
                                value=float(current_limits["soil_moisture"]),
                                step=1.0,
                                key=f"input_s_{sensor_id}",
                            )

                        commit_btn = st.form_submit_button(
                            label=f"💾 Save Boundaries for Node {sensor_id}",
                            use_container_width=True,
                        )

                        if commit_btn:
                            is_saved = self._repository.save_sensor_threshold(
                                sensor_id,
                                float(val_temp),
                                float(val_noise),
                                float(val_traffic),
                                float(val_air),
                                float(val_soil),
                            )
                            if is_saved:
                                st.success(f"✨ Custom guidelines committed for: {sensor_name}")
                                st.rerun()
                            else:
                                st.error(
                                    "❌ ACID pipeline exception encountered on write operation."
                                )

        st.divider()

        st.markdown(f"#### 📥 {provider.get('tab_export_cfg')}")
        raw_dump: Final[pd.DataFrame] = self._repository.fetch_raw_telemetry_dump()

        if raw_dump.empty:
            st.warning("⚠️ Telemetry matrix logging channels returned empty data blocks.")
        else:
            st.dataframe(raw_dump.head(10), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            exp_col1, exp_col2 = st.columns(2)

            with exp_col1:
                csv_data = self._export_service.generate_csv_bytes(raw_dump)
                st.download_button(
                    label="📄 Download Structured CSV Dataset File",
                    data=csv_data,
                    file_name="smart_city_cluj_telemetry.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            with exp_col2:
                xlsx_data = self._export_service.generate_excel_bytes(raw_dump)
                st.download_button(
                    label="📊 Download Dynamic Excel Matrix Spreadsheet",
                    data=xlsx_data,
                    file_name="smart_city_cluj_matrix.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )


if __name__ == "__main__":
    page = SettingsPage()
    page.display()
