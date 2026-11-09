"""Light platform for Tapo Bulbs (TPAP)."""

from __future__ import annotations

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.device_registry import DeviceInfo, format_mac
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .tapo_kasa import Module


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([TapoBulb(hass.data[DOMAIN][entry.entry_id])])


class TapoBulb(CoordinatorEntity, LightEntity):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        dev = coordinator.device
        self._dev = dev
        self._light = dev.modules[Module.Light]
        self._attr_unique_id = format_mac(dev.mac)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, format_mac(dev.mac))},
            manufacturer="TP-Link",
            model=dev.model,
            name=dev.alias or dev.model,
        )
        modes = set()
        if self._light.has_feature("hsv"):
            modes.add(ColorMode.HS)
        if self._light.has_feature("color_temp"):
            modes.add(ColorMode.COLOR_TEMP)
            feat = self._light.get_feature("color_temp")
            self._attr_min_color_temp_kelvin = feat.minimum_value
            self._attr_max_color_temp_kelvin = feat.maximum_value
        if not modes:
            modes.add(ColorMode.BRIGHTNESS if self._light.has_feature("brightness") else ColorMode.ONOFF)
        self._attr_supported_color_modes = modes

    @property
    def is_on(self) -> bool:
        return self._dev.is_on

    @property
    def brightness(self):
        if self._light.has_feature("brightness"):
            return round(self._light.brightness * 255 / 100)
        return None

    @property
    def color_temp_kelvin(self):
        if self._light.has_feature("color_temp"):
            return self._light.color_temp or None
        return None

    @property
    def hs_color(self):
        if self._light.has_feature("hsv"):
            h, s, _ = self._light.hsv
            return (h, s)
        return None

    @property
    def color_mode(self):
        if ColorMode.HS in self._attr_supported_color_modes and self.color_temp_kelvin in (None, 0):
            return ColorMode.HS
        if ColorMode.COLOR_TEMP in self._attr_supported_color_modes:
            return ColorMode.COLOR_TEMP
        return next(iter(self._attr_supported_color_modes))

    async def async_turn_on(self, **kwargs) -> None:
        bri = kwargs.get(ATTR_BRIGHTNESS)
        pct = max(1, round(bri * 100 / 255)) if bri is not None else None
        if ATTR_HS_COLOR in kwargs:
            h, s = kwargs[ATTR_HS_COLOR]
            await self._light.set_hsv(int(h), int(s), pct)
        elif ATTR_COLOR_TEMP_KELVIN in kwargs:
            await self._light.set_color_temp(int(kwargs[ATTR_COLOR_TEMP_KELVIN]), brightness=pct)
        elif pct is not None:
            await self._light.set_brightness(pct)
        else:
            await self._dev.turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._dev.turn_off()
        await self.coordinator.async_request_refresh()
