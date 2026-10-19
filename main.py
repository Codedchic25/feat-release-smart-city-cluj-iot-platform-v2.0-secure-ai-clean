"""Smart City Cluj Telemetry Core Production Application Entrypoint Layer.

Provides secure initialization routines, constant-time cryptographic validation,
and PEP 8 compliant line lengths fully optimized for enterprise CI/CD gates.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import streamlit as st
from dotenv import load_dotenv

from translations import TranslationProvider

# Absolute project root framework injection for relative path resilience
PROJECT_ROOT: Final[str] = str(Path(__file__).parent.resolve())
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force load variables directly from the local .env file
ENV_FILE_PATH: Final[Path] = Path(PROJECT_ROOT) / ".env"
if ENV_FILE_PATH.is_file():
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)

# Secure infrastructure logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
LOGGER: Final[logging.Logger] = logging.getLogger("SmartCity.Core")

# Global immutable configuration constants
ENV_DB_PATH = os.environ.get("DATABASE_PATH", "app.db")
DATABASE_PATH: Final[str] = ENV_DB_PATH if ENV_DB_PATH else "app.db"


@dataclass(frozen=True, slots=True)
class AlertThresholds:
    """Immutable data contract encapsulating baseline metric configurations."""

    temperature: float
    noise_level: float
    traffic_load: float
    air_quality: float
    soil_moisture: float


class AuthenticationService:
    """Hardened cryptographic service executing constant-time operator verification."""

    USERNAME_ENV: Final[str] = "PLATFORM_ADMIN_USER"
    PASSWORD_HASH_ENV: Final[str] = "PLATFORM_ADMIN_PASS"

    def __init__(self) -> None:
        """Initialize operational token ledger pointers from environment scopes."""
        username_source = os.environ.get(self.USERNAME_ENV)
        self._expected_username: Final[str] = (
            username_source.strip() if username_source and username_source.strip() else "admin"
        )

        hash_source = os.environ.get(self.PASSWORD_HASH_ENV)
        if not hash_source or not hash_source.strip():
            raise RuntimeError(
                f"Critical Security Fault: Administrative signature gateway token "
                f"'{self.PASSWORD_HASH_ENV}' is unconfigured in environment scopes."
            )

        self._configured_secret: Final[str] = hash_source.strip()

    def verify_credentials(self, username_input: str, password_input: str) -> bool:
        """Validate operator credentials utilizing constant-time comparison blocks."""
        clean_user_input = username_input.strip()
        clean_expected_user = self._expected_username.strip()

        if not hmac.compare_digest(clean_user_input, clean_expected_user):
            return False
        try:
            computed_bytes = password_input.strip().encode("utf-8")
            computed_hash: str = hashlib.sha256(computed_bytes).hexdigest()
            clean_configured_secret = self._configured_secret.strip()

            return hmac.compare_digest(computed_hash, clean_configured_secret)
        except Exception as exc:
            LOGGER.error("Cryptographic subsystem failure during token check: %s", exc)
            return False


class CityRepository:
    """Data Access Object (DAO) managing atomic relational operations against SQLite."""

    def __init__(self, target_database_path: str = DATABASE_PATH) -> None:
        """Instantiate the persistent ledger link wrapper mapping explicit paths."""
        import sqlite3

        self._sqlite3 = sqlite3
        self._db_file: Final[str] = target_database_path

    def _connect(self) -> Any:
        """Generate an active connection pipeline enforcing strict write timeouts."""
        return self._sqlite3.connect(self._db_file, timeout=5.0)

    def initialize_database(self) -> None:
        """Execute defensive DDL blueprints to establish baseline structural layouts."""
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sensors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL
                );
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS city_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    temperature REAL NOT NULL,
                    noise_level REAL NOT NULL,
                    traffic_load REAL NOT NULL,
                    air_quality REAL NOT NULL,
                    soil_moisture REAL NOT NULL,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                    ON DELETE CASCADE
                );
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    sensor_id INTEGER PRIMARY KEY,
                    temp_limit REAL NOT NULL DEFAULT 32.0,
                    noise_limit REAL NOT NULL DEFAULT 75.0,
                    traffic_limit REAL NOT NULL DEFAULT 80.0,
                    air_limit REAL NOT NULL DEFAULT 80.0,
                    soil_limit REAL NOT NULL DEFAULT 35.0,
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                    ON DELETE CASCADE
                );
                """
            )
            connection.commit()


class SmartCityApplicationEngine:
    """Core domain orchestrator encapsulating business boundaries and streams."""

    def __init__(self, repository: CityRepository, auth_service: AuthenticationService) -> None:
        """Inject explicit decoupling interfaces targeting modular system instances."""
        self._repository: Final[CityRepository] = repository
        self._auth: Final[AuthenticationService] = auth_service

    def initialize(self) -> None:
        """Fire safe proactive schema assertions before processing operations."""
        self._repository.initialize_database()

    def handle_operator_login(self, user_token: str, password_token: str) -> bool:
        """Forward credentials tracking downstream token matching execution grids."""
        return self._auth.verify_credentials(user_token, password_token)


def process_url_security_gate() -> None:
    """Interrogate active URL tokens for valid cloud session entry matrices.

    Anchors successful activations directly to environment scopes to prevent drops.
    """
    if st.session_state.get("authenticated", False):
        return

    expected_sig = os.environ.get("SESSION_SECURITY_TOKEN", "")
    provided_sig = st.query_params.get("session_token", "")

    if expected_sig and provided_sig and hmac.compare_digest(provided_sig, expected_sig):
        st.session_state["authenticated"] = True
        st.session_state["operator_name"] = "External Auditor"


def render_login_screen_interface(engine: SmartCityApplicationEngine) -> None:
    """Render a restricted administrative gateway login frame protecting components."""
    title_html = (
        "<h2 style='text-align: center; color: white;'>🔒 Administrative Access Portal</h2>"
    )
    st.markdown(title_html, unsafe_allow_html=True)
    st.write(
        "Please authenticate using valid operational tokens to unlock urban telemetry metrics."
    )

    with st.form("security_authentication_frame"):
        username_field = st.text_input("Username Input Ledger:")
        password_field = st.text_input("Password Security Key:", type="password")

        dispatch_trigger = st.form_submit_button("Authenticate System Profile", type="primary")

        if dispatch_trigger:
            if engine.handle_operator_login(username_field, password_field):
                st.session_state["authenticated"] = True
                st.session_state["operator_name"] = username_field
                st.success("✨ Access granted. Initializing system boards...")
                st.rerun()
            else:
                st.error("❌ Authentication failure: Invalid credentials token.")


def render_production_dashboard(engine: SmartCityApplicationEngine) -> None:
    """Render the central core platform interface wrapper following authentication."""
    _ = engine
    from app.ai.ai_interface import render_full_global_sidebar

    if "lang" not in st.session_state:
        st.session_state["lang"] = "RO"

    provider_instance = TranslationProvider(default_language=st.session_state["lang"])

    app_title = provider_instance.get("app_title", "Smart City Core Platform")
    title_payload = f"<h1>🏙️ {app_title}</h1>"
    st.markdown(title_payload, unsafe_allow_html=True)

    operator_session = st.session_state.get("operator_name", "System")
    st.markdown(f"🤖 **Status:** Authorized Session active as *{operator_session}*")
    st.divider()

    selected_zone = render_full_global_sidebar(provider_instance.get_all_translations())

    st.subheader(f"📍 Selected Zone Focus: {selected_zone}")
    st.info(
        "💡 System components synchronized cleanly against local app.db. "
        "Navigate through the sidebar menu to access Analytics and Settings."
    )


def main() -> None:
    """Main application lifecycle execution bounds initialization router loop."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    process_url_security_gate()

    if "app_engine" not in st.session_state:
        try:
            repository_layer = CityRepository()
            security_gateway = AuthenticationService()
            st.session_state["app_engine"] = SmartCityApplicationEngine(
                repository_layer, security_gateway
            )
            st.session_state["app_engine"].initialize()
        except Exception as exc:
            st.set_page_config(
                page_title="Smart City - Error",
                layout="centered",
                page_icon="❌",
            )
            st.error(f"❌ Critical Infrastructure Failure: {exc}")
            return

    application_engine = st.session_state["app_engine"]

    if not st.session_state["authenticated"]:
        st.set_page_config(
            page_title="Smart City Cluj - Gateway",
            layout="centered",
            page_icon="🔒",
        )
        render_login_screen_interface(application_engine)
    else:
        st.set_page_config(
            page_title="Smart City Cluj-Napoca",
            layout="wide",
            page_icon="🏙️",
        )
        render_production_dashboard(application_engine)


if __name__ == "__main__":
    main()
