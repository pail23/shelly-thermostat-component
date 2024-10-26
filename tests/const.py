"""Constants for integration_blueprint tests."""

from homeassistant.const import CONF_HOST, CONF_SCAN_INTERVAL

# Mock config data to be used across multiple tests
MOCK_CONFIG = {CONF_HOST: "localhost", CONF_SCAN_INTERVAL: "27"}
