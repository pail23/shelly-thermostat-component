"""DataUpdateCoordinator for shelly thermostat."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from .api import ShellyThermostatApiClientError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ShellyThermostatConfigEntry


SCAN_INTERVAL = timedelta(seconds=30)


class ShellyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: ShellyThermostatConfigEntry

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.platforms = []

        super().__init__(hass, LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except ShellyThermostatApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_set_target_temperature(self, target_temperature: float) -> None:
        await self.config_entry.runtime_data.client.async_set_target_temperature(
            target_temperature
        )
        await self.async_request_refresh()

    async def async_set_hvac_mode(self, mode: str) -> None:
        await self.config_entry.runtime_data.client.async_set_hvac_mode(mode)
        await self.async_request_refresh()
