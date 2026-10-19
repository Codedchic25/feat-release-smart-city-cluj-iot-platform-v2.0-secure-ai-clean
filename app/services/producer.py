"""Asynchronous background telemetry producer and operational core services.

Fully aligned with production-ready OOP structures, asynchronous event loops,
and PEP 8 geometric formatting limits enforced within the CI/CD pipeline matrix.
"""

from __future__ import annotations

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from datetime import datetime
from pathlib import Path
from typing import Final, NamedTuple

# Core framework components mapping database persistence layers
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize isolated nominal logger module profile tracking boundaries
LOGGER: Final[logging.Logger] = logging.getLogger("SmartCity.Producer")


class SensorThresholds(NamedTuple):
    """Immutable data structure representing sensory alert boundaries."""

    temp_limit: float
    noise_limit: float
    air_limit: float
    soil_limit: float


class AlertProcessorInterface(ABC):
    """Abstract interface defining alert routing capabilities for inversion of control."""

    @abstractmethod
    async def send_local_log_alert_async(self, alert_type: str, message_body: str) -> None:
        """Writes infrastructure anomaly alerts safely to the destination target."""

    @abstractmethod
    async def process_alerts_async(
        self,
        sensor_name: str,
        telemetry_data: dict[str, float],
        thresholds: SensorThresholds,
    ) -> None:
        """Evaluates live operational sensory dimensions against system parameters."""


class AlertProcessor(AlertProcessorInterface):
    """Handles operational metric evaluation and thread-safe alert throttling."""

    def __init__(
        self,
        log_file_path: str | Path = "security_alerts.log",
        cooldown_seconds: float = 10.0,
    ) -> None:
        """Initialize the asynchronous alert throttling processor layer.

        Args:
            log_file_path: Target physical location path for anomalies storage.
            cooldown_seconds: Minimum boundary (seconds) between identical events.
        """
        self._log_file_path: Final[Path] = Path(log_file_path)
        self._cooldown_seconds: Final[float] = cooldown_seconds
        self._alert_cooldown_registry: Final[dict[str, float]] = {}
        self._lock: Final[asyncio.Lock] = asyncio.Lock()

    async def send_local_log_alert_async(self, alert_type: str, message_body: str) -> None:
        """Writes infrastructure anomaly alerts safely to the local filesystem with thread-pools."""
        loop = asyncio.get_running_loop()
        current_time: Final[float] = loop.time()

        async with self._lock:
            last_sent_timestamp = self._alert_cooldown_registry.get(alert_type, 0.0)
            if current_time - last_sent_timestamp < self._cooldown_seconds:
                return
            self._alert_cooldown_registry[alert_type] = current_time

        time_iso = datetime.now().isoformat()
        log_line: Final[str] = f"[{time_iso}] [{alert_type}] {message_body}\n"

        try:
            await loop.run_in_executor(None, lambda: self._write_to_file(log_line))
        except OSError as err:
            LOGGER.error("Failed to write system alert to disk: %s", err)

    def _write_to_file(self, content: str) -> None:
        """Synchronous file append operation designed to be executed inside a thread pool."""
        with open(self._log_file_path, mode="a", encoding="utf-8") as file:
            file.write(content)

    async def process_alerts_async(
        self,
        sensor_name: str,
        telemetry_data: dict[str, float],
        thresholds: SensorThresholds,
    ) -> None:
        """Evaluates live operational sensory dimensions against system parameters."""
        alert_tasks: list[asyncio.Task[None]] = []

        temperature = telemetry_data["temperature"]
        air_quality = telemetry_data["air_quality"]
        soil_moisture = telemetry_data["soil_moisture"]

        if temperature > thresholds.temp_limit:
            msg = (
                f"Critical thermal variance detected at station "
                f"'{sensor_name}': {temperature:.1f}°C"
            )
            alert_tasks.append(
                asyncio.create_task(
                    self.send_local_log_alert_async(f"{sensor_name}_temperature", msg)
                )
            )

        if air_quality > thresholds.air_limit:
            msg = (
                f"Elevated particulate matter pollution at station "
                f"'{sensor_name}': {air_quality:.1f} PM2.5"
            )
            alert_tasks.append(
                asyncio.create_task(
                    self.send_local_log_alert_async(f"{sensor_name}_air_quality", msg)
                )
            )

        if soil_moisture < thresholds.soil_limit:
            msg = (
                f"Critical soil moisture deficit recorded at station "
                f"'{sensor_name}': {soil_moisture:.1f}%"
            )
            alert_tasks.append(
                asyncio.create_task(
                    self.send_local_log_alert_async(f"{sensor_name}_soil_moisture", msg)
                )
            )

        if alert_tasks:
            await asyncio.gather(*alert_tasks, return_exceptions=True)


class TelemetryProducerEngine:
    """Orchestrates structured metadata loops, SQL transactions, and maintenance sweeps."""

    def __init__(
        self,
        session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
        alert_processor: AlertProcessorInterface | None = None,
    ) -> None:
        """Initialize the background telemetry simulation and processing engine.

        Args:
            session_factory: Async context manager factory yielding database
                sessions (Dependency Injection).
            alert_processor: AlertProcessor instance handling log delivery.
        """
        self._session_factory: Final[Callable[[], AbstractAsyncContextManager[AsyncSession]]] = (
            session_factory
        )
        self._alert_processor: Final[AlertProcessorInterface] = alert_processor or AlertProcessor()
        self._generation_interval: Final[int] = 5

    @staticmethod
    def generate_sensor_telemetry(sensor_name: str) -> dict[str, float]:
        """Calculates simulated telemetry signals representing typical urban drift arrays."""
        _ = sensor_name
        traffic = random.randint(10, 95)
        temperature = round(random.uniform(18, 32) + (traffic * 0.03), 1)
        noise_level = round(random.uniform(40, 65) + (traffic * 0.2), 1)
        air_quality = round(0.45 * traffic + random.uniform(10.0, 25.0), 1)
        soil_moisture = round(random.uniform(25, 75) - (temperature * 0.15), 1)

        return {
            "temperature": temperature,
            "noise_level": noise_level,
            "traffic_load": float(traffic),
            "air_quality": air_quality,
            "soil_moisture": soil_moisture,
        }

    async def execute_continuous_simulation_loop_async(self) -> None:
        """Runs the infinite asynchronous loop pulling data and processing safety limits."""
        from sqlalchemy import text

        query = text("""
            SELECT s.id, s.name, st.temp_limit, st.noise_limit, st.air_limit, st.soil_limit
            FROM sensors s
            LEFT JOIN settings st ON s.id = st.sensor_id
        """)

        while True:
            try:
                async with self._session_factory() as session:
                    result = await session.execute(query)
                    sensors = result.all()

                    if not sensors:
                        LOGGER.warning(
                            "Target table 'sensors' contains no records. "
                            "Awaiting administrative seeding setup..."
                        )
                        await asyncio.sleep(5)
                        continue

                    for row in sensors:
                        _sensor_id, sensor_name, t_lim, n_lim, a_lim, s_lim = row

                        thresholds = SensorThresholds(
                            temp_limit=float(t_lim) if t_lim is not None else 32.0,
                            noise_limit=float(n_lim) if n_lim is not None else 75.0,
                            air_limit=float(a_lim) if a_lim is not None else 80.0,
                            soil_limit=float(s_lim) if s_lim is not None else 35.0,
                        )

                        telemetry = self.generate_sensor_telemetry(sensor_name)

                        await self._alert_processor.process_alerts_async(
                            sensor_name=sensor_name,
                            telemetry_data=telemetry,
                            thresholds=thresholds,
                        )

            except Exception as exc:
                LOGGER.error("Simulation cycle breakdown encountered: %s", exc, exc_info=True)

            await asyncio.sleep(self._generation_interval)
