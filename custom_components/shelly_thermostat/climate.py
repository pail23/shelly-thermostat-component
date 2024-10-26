"""Climate platform for shelly_thermostat."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import UnitOfTemperature

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    ClimateEntityDescription,
    ATTR_TEMPERATURE,
)

from homeassistant.components.climate.const import HVACMode, HVACAction

from .entity import ShellyThermostatEntity


if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import ShellyDataUpdateCoordinator
    from .data import ShellyThermostatConfigEntry


ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        name="Shelly thermostat", has_entity_name=True, key="thermostat"
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: ShellyThermostatConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        ShellyThermostatClimate(
            coordinator=entry.runtime_data.coordinator,
            entry=entry,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class ShellyThermostatClimate(ShellyThermostatEntity, ClimateEntity):
    """Shelly Thermostat climate class."""

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.COOL, HVACMode.OFF]
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_max_temp = 35
    _attr_min_temp = 5
    _attr_target_temperature_step = 0.1
    _attr_icon = "mdi:thermostat"

    def __init__(
        self,
        coordinator: ShellyDataUpdateCoordinator,
        entry: ShellyThermostatConfigEntry,
        entity_description: ClimateEntityDescription,
    ):
        """Initialize the climate."""
        self.entity_description = entity_description

        super().__init__(coordinator, entry)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.data.get("temperature")

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temperature")

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        mode = self.coordinator.data.get("hvac_mode")
        if mode == "heat":
            return HVACMode.HEAT
        elif mode == "cool":
            return HVACMode.COOL
        elif mode == "off":
            return HVACMode.OFF
        return HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        """HVAC current action."""
        output = self.coordinator.data.get("output")
        mode = self.coordinator.data.get("hvac_mode")
        if mode == "heat":
            return HVACAction.HEATING if output else HVACAction.IDLE
        elif mode == "cool":
            return HVACAction.COOLING if output else HVACAction.IDLE
        else:
            return HVACAction.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.HEAT:
            await self.coordinator.async_set_hvac_mode("heat")
        elif hvac_mode == HVACMode.COOL:
            await self.coordinator.async_set_hvac_mode("cool")
        elif hvac_mode == HVACMode.OFF:
            await self.coordinator.async_set_hvac_mode("off")

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs[ATTR_TEMPERATURE]
        await self.coordinator.async_set_target_temperature(temperature)
