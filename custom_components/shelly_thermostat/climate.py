"""Climate platform for shelly_thermostat."""
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    TEMP_CELSIUS,
    SUPPORT_TARGET_TEMPERATURE,
    ATTR_TEMPERATURE,
)

from .const import DOMAIN
from .entity import ShellyThermostatEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    description = ClimateEntityDescription(
        name=coordinator.data.get("name"), key="thermostat"
    )
    async_add_devices([ShellyThermostatClimate(coordinator, entry, description)])


class ShellyThermostatClimate(ShellyThermostatEntity, ClimateEntity):
    """integration_blueprint Sensor class."""

    def __init__(
        self,
        coordinator,
        config_entry,
        description,
    ):
        """Initialize the climate."""
        self.entity_description = description
        self._attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_OFF]
        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_supported_features = SUPPORT_TARGET_TEMPERATURE
        self._attr_max_temp = 35
        self._attr_min_temp = 5
        self._attr_target_temperature_step = 0.1
        super().__init__(coordinator, config_entry)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.data.get("temperature")

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.data.get("target_temperature")

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode.

        Need to be one of HVAC_MODE_*.
        """
        mode = self.coordinator.data.get("hvac_mode")
        if mode == "heat":
            return HVAC_MODE_HEAT
        elif mode == "cool":
            return HVAC_MODE_COOL
        elif mode == "off":
            return HVAC_MODE_OFF
        return None

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.coordinator.async_set_hvac_mode("heat")
        elif hvac_mode == HVAC_MODE_COOL:
            await self.coordinator.async_set_hvac_mode("cool")
        elif hvac_mode == HVAC_MODE_OFF:
            await self.coordinator.async_set_hvac_mode("off")

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs[ATTR_TEMPERATURE]
        await self.coordinator.async_set_target_temperature(temperature)