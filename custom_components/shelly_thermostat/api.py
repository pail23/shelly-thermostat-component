"""Sample API Client."""

import logging
import asyncio
import socket
import aiohttp
import async_timeout

TIMEOUT = 10
RELAY_ON = "relay_on"
RELAY_OFF = "relay_off"
DISABLED = "disabled"

HVAC_MODE_HEAT = "heat"
HVAC_MODE_COOL = "cool"
HVAC_MODE_OFF = "off"

_LOGGER: logging.Logger = logging.getLogger(__package__)


class ShellyThermostatApiClientError(Exception):
    """Exception to indicate a general API error."""


class ShellyApiClient:
    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """Sample API Client."""
        self._host = host
        self._session = session

    async def async_get_data(self) -> dict:
        result = {}
        status = await self.api_wrapper(
            "get",
            f"http://{self._host}/status",
        )
        result["status"] = status
        result["temperature"] = float(status.get("ext_temperature").get("0").get("tC"))
        result["output"] = status.get("relays")[0].get("ison")
        result["mac"] = status.get("mac")

        settings = await self.api_wrapper(
            "get",
            f"http://{self._host}/settings",
        )
        result["settings"] = settings
        temp_settings = settings.get("ext_temperature").get("0")
        overtemp_action = temp_settings["overtemp_act"]
        undertemp_action = temp_settings["undertemp_act"]
        if overtemp_action == RELAY_OFF and undertemp_action == RELAY_ON:
            result["hvac_mode"] = "heat"
        elif overtemp_action == RELAY_ON and undertemp_action == RELAY_OFF:
            result["hvac_mode"] = "cool"
        elif overtemp_action == DISABLED and undertemp_action == DISABLED:
            result["hvac_mode"] = "off"
        else:
            _LOGGER.error("Invalid thermostat configuration")
            result["hvac_mode"] = "unknown"

        overtemp_threshold = float(temp_settings["overtemp_threshold_tC"])
        undertemp_threshold = float(temp_settings["undertemp_threshold_tC"])
        result["target_temperature"] = (overtemp_threshold + undertemp_threshold) / 2

        result["name"] = settings.get("name")
        result["model"] = settings.get("device").get("type")

        return result

    """
    async def async_get_temperature(self) -> float:
        temp_status = (
            await self.api_wrapper(
                "get",
                f"http://{self._host}/status",
            )
            .get("ext_temperature")
            .get("0")
        )
        return float(temp_status["tC"])

    async def async_get_target_temperature(self) -> float:
        temp_settings = (
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings",
            )
            .get("ext_temperature")
            .get("0")
        )
        return (
            float(temp_settings["overtemp_threshold_tC"])
            + float(temp_settings["undertemp_threshold_tC"])
        ) / 2
    """

    async def async_set_target_temperature(
        self, target_temperature: float, hystersis: float = 0.4
    ) -> float:
        await self.api_wrapper(
            "get",
            f"http://{self._host}/settings/ext_temperature/0?overtemp_threshold_tC={target_temperature + hystersis / 2}",
        )
        await self.api_wrapper(
            "get",
            f"http://{self._host}/settings/ext_temperature/0?undertemp_threshold_tC={target_temperature - hystersis / 2}",
        )

    async def async_set_hvac_mode(self, mode: str) -> None:
        """Get data from the API."""
        if mode == HVAC_MODE_HEAT:
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?overtemp_act={RELAY_OFF}",
            )
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?undertemp_act={RELAY_ON}",
            )
        elif mode == HVAC_MODE_COOL:
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?overtemp_act={RELAY_ON}",
            )
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?undertemp_act={RELAY_OFF}",
            )
        elif mode == HVAC_MODE_OFF:
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?overtemp_act={DISABLED}",
            )
            await self.api_wrapper(
                "get",
                f"http://{self._host}/settings/ext_temperature/0?undertemp_act={DISABLED}",
            )

    async def api_wrapper(
        self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await self._session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await self._session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await self._session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await self._session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
