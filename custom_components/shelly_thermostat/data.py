"""Custom types for shelly thermostat."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import ShellyApiClient
    from .coordinator import ShellyDataUpdateCoordinator


type ShellyThermostatConfigEntry = ConfigEntry[ShellyThermostatData]


@dataclass
class ShellyThermostatData:
    """Data for the shelly thermostat integration."""

    client: ShellyApiClient
    coordinator: ShellyDataUpdateCoordinator
    integration: Integration
