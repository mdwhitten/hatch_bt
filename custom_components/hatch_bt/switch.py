"""Support for Generic BT binary sensor."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, Schema
from .coordinator import GenericBTCoordinator
from .entity import GenericBTEntity
from .const import *
from .generic_bt_api.device import *

# Initialize the logger
_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Generic BT device based on a config entry."""
    coordinator: GenericBTCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HatchBTSwitch(coordinator)])

"""     platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service("turn_off", None, "turn_off")
    platform.async_register_entity_service("turn_on", None, "turn_on") """


class HatchBTSwitch(GenericBTEntity, SwitchEntity):

    def __init__(self, coordinator: GenericBTCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)


    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._device.power_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._device.power_off()
        self.async_write_ha_state()

    async def async_toggle(self, **kwargs):
        if self._device.power:
            await self._device.power_off()
        else:
            await self._device.power_on()

        self.async_write_ha_state()

    @property
    def is_on(self) -> str:
        """Return the display name of this light."""
        return self._device.power