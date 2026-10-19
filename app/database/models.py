"""SQLAlchemy ORM models for the Smart City Cluj-Napoca IoT platform.

This module maps the relational database schema to Python object-oriented constructs
using modern SQLAlchemy v2.0 Declarative mapping layouts (Mapped/mapped_column).
It encapsulates structural constraints, foreign keys with cascading options,
and performance-optimizing indexes for high-throughput IoT analytics.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import REAL, TEXT, DateTime, ForeignKey, Index, Integer, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Abstract base class serving as the declarative root for all database models.

    Inherits from SQLAlchemy's DeclarativeBase to register structural table metadata
    and facilitate automated schema drift generation via Alembic migrations.
    """


class Sensor(Base):
    """Represents a physical IoT sensor node deployed across the urban framework.

    Maps structural geospatial locations and aggregates high-frequency analytics.

    Attributes:
        id (int): Primary key for sensor node identification. Autoincremented.
        name (str): Unique name of the physical location (e.g., 'Parcul Central').
        latitude (float | None): Geo-spatial GPS latitude coordinates for mapping.
        longitude (float | None): Geo-spatial GPS longitude coordinates for mapping.
        telemetry (list[CityStat]): One-to-Many relational collection mapping
            child telemetry metrics.
    """

    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )

    latitude: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    # Relationship configuration enforcing full life-cycle parent-child bound deletion
    telemetry: Mapped[list[CityStat]] = relationship(
        back_populates="sensor",
        cascade="all, delete-orphan",
    )


class CityStat(Base):
    """Represents historical time-series telemetry data captured from deployed sensor nodes.

    Designed for analytical metrics collection (temperature, noise, air quality, traffic).

    Attributes:
        id (int): Primary key identifying the explicit metric ledger entry.
        sensor_id (int): Foreign key link enforcing relational integrity against
            the parent Sensor table.
        temperature (float | None): Dynamic thermal metrics captured from ambient.
        noise_level (float | None): Acoustic threshold tracking noise pollution.
        traffic_load (float | None): Urban density score representing congestion.
        air_quality (float | None): Micro-particles rating matrix analyzing air.
        soil_moisture (float | None): Sub-surface moisture level metric for parks.
        timestamp (datetime): Absolute server time of measurement capture.
            Automated database-level generation.
        sensor (Sensor): Reference back to the associated parent Sensor object.
    """

    __tablename__ = "city_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    sensor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sensors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    temperature: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    noise_level: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    traffic_load: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    air_quality: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    soil_moisture: Mapped[float | None] = mapped_column(
        REAL,
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    sensor: Mapped[Sensor] = relationship(
        back_populates="telemetry",
    )

    __table_args__ = (
        # Composite Index optimizing multi-column spatial-temporal
        # analytical dashboard interogations
        Index(
            "idx_city_stats_sensor_timestamp",
            "sensor_id",
            "timestamp",
        ),
    )


class Setting(Base):
    """Defines configurable warning and safety limit thresholds per IoT node instance.

    Acts as an evaluation baseline to trigger system alerts whenever telemetries exceed bounds.

    Attributes:
        sensor_id (int): Primary key and Foreign key binding settings strictly
            to one unique sensor node.
        temp_limit (float): Upper boundary threshold defining thermal alerts.
        noise_limit (float): Upper boundary threshold defining sound alerts.
        air_limit (float): Lower boundary threshold defining poor air alerts.
        soil_limit (float): Lower boundary threshold defining drought alerts.
    """

    __tablename__ = "settings"

    sensor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sensors.id", ondelete="CASCADE"),
        primary_key=True,
    )

    temp_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=32.0,
    )

    noise_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=75.0,
    )

    air_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=80.0,
    )

    soil_limit: Mapped[float] = mapped_column(
        REAL,
        nullable=False,
        default=35.0,
    )


class User(Base):
    """Represents administrative operators authorized to configure the infrastructure.

    Attributes:
        username (str): Primary identifier for authentication. Single system
            unique ledger pointer.
        name (str | None): Human display name of the system operator.
        password (str): Securely hashed secret key value verifying session requests.
    """

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        TEXT,
        primary_key=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        TEXT,
        nullable=True,
    )

    password: Mapped[str] = mapped_column(
        TEXT,
        nullable=False,
    )
