"""Constants for integration_blueprint."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Base component constants
NAME = "Shelly Thermostat"
MANUFACTURER = "Shelly"
DOMAIN = "shelly_thermostat"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ISSUE_URL = "https://github.com/pail23/shelly-thermostat-component/issues"

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_HOST_NAME = ""


# Platforms
CLIMATE = "climate"
PLATFORMS = [CLIMATE]


# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
