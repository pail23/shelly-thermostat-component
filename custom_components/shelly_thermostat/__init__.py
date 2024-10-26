"""
Custom integration to integrate shelly_thermostat with Home Assistant.

For more details about this integration, please refer to
https://github.com/pail23/shelly-thermostat-component
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .coordinator import ShellyDataUpdateCoordinator
from .data import ShellyThermostatData
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration

from .api import ShellyApiClient

from .const import PLATFORMS

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import ShellyThermostatConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShellyThermostatConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = ShellyDataUpdateCoordinator(hass)
    entry.runtime_data = ShellyThermostatData(
        client=ShellyApiClient(
            entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ShellyThermostatConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ShellyThermostatConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
