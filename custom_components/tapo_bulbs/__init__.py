"""Tapo Bulbs (TPAP): local control of Tapo bulbs using a vendored python-kasa with TPAP."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, DOMAIN, SCAN_INTERVAL_SECONDS
from .tapo_kasa import Credentials, Discover
from .tapo_kasa.exceptions import KasaException

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.LIGHT]


class TapoCoordinator(DataUpdateCoordinator):
    """Polls one bulb."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {entry.data[CONF_HOST]}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        self.device = device

    async def _async_update_data(self):
        try:
            await self.device.update()
        except KasaException as err:
            raise UpdateFailed(str(err)) from err
        return self.device


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    creds = Credentials(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    try:
        device = await Discover.discover_single(entry.data[CONF_HOST], credentials=creds)
        if device is None:
            raise ConfigEntryNotReady("No response from bulb")
        await device.update()
    except KasaException as err:
        raise ConfigEntryNotReady(str(err)) from err
    coordinator = TapoCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.device.disconnect()
    return ok
