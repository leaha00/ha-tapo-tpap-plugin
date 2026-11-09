"""Config flow for Tapo Bulbs (TPAP)."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.device_registry import format_mac

from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DOMAIN
from .tapo_kasa import Credentials, Discover
from .tapo_kasa.exceptions import AuthenticationError, KasaException

_LOGGER = logging.getLogger(__name__)


class TapoBulbsFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        placeholders = {"detail": ""}
        if user_input is not None:
            dev = None
            try:
                dev = await Discover.discover_single(
                    user_input[CONF_HOST],
                    credentials=Credentials(user_input[CONF_USERNAME], user_input[CONF_PASSWORD]),
                )
                if dev is None:
                    _LOGGER.error("Discovery returned no device for %s", user_input[CONF_HOST])
                    placeholders["detail"] = "Discovery got no response from the bulb (UDP 20002)."
                    errors["base"] = "cannot_connect"
                else:
                    await dev.update()
                    await self.async_set_unique_id(format_mac(dev.mac))
                    self._abort_if_unique_id_configured(updates=user_input)
                    title = dev.alias or dev.model
                    return self.async_create_entry(title=title, data=user_input)
            except AuthenticationError as err:
                _LOGGER.exception("Authentication failed for %s", user_input[CONF_HOST])
                placeholders["detail"] = f"{type(err).__name__}: {err}"
                errors["base"] = "invalid_auth"
            except KasaException as err:
                _LOGGER.exception("Could not connect to %s", user_input[CONF_HOST])
                placeholders["detail"] = f"{type(err).__name__}: {err}"
                errors["base"] = "cannot_connect"
            except Exception as err:  # noqa: BLE001
                _LOGGER.exception("Unexpected error for %s", user_input[CONF_HOST])
                placeholders["detail"] = f"{type(err).__name__}: {err}"
                errors["base"] = "unknown"
            finally:
                if dev is not None:
                    await dev.disconnect()
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors, description_placeholders=placeholders)
