"""Platform for light integration."""
from __future__ import annotations

import logging

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ColorMode, PLATFORM_SCHEMA,
                                            LightEntity)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from typing import Any

from .const import DOMAIN, Schema
from .coordinator import HatchBTUpdateCoordinator
from .entity import HatchBTEntity
from .const import *
from .generic_bt_api.device import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Generic BT device based on a config entry."""
    coordinator: HatchBTUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HatchBTLight(coordinator)], update_before_add=True)


class HatchBTLight(HatchBTEntity, LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, coordinator: HatchBTUpdateCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._name = "Hatch Bluetooth Light"

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def color_mode(self):
        return ColorMode.RGB
    
    @property
    def supported_color_modes(self):
        return [ColorMode.RGB]

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._device.brightness

    @property
    def rgb_color(self):
        return self._device.color

    @property
    def is_on(self) -> bool | None:
        _LOGGER.debug("Power property read")
        """Return true if light is on."""
        return self._device.power

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        color = kwargs.get(ATTR_RGB_COLOR, self.rgb_color)
        brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)

        await self._device.set_color_brightness(color, brightness)
        if not self._device.power:
            await self._device.power_on()

        # Update the data
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        if self._device.power:
            await self._device.power_off()

        # Update the data
        await self.coordinator.async_request_refresh()
