"""Provides the DataUpdateCoordinator."""
from __future__ import annotations

import asyncio
import contextlib
import logging

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import ActiveBluetoothDataUpdateCoordinator
from homeassistant.core import CoreState, HomeAssistant, callback
from bleak.backends.device import BLEDevice

import async_timeout
from bleak import BleakError
from datetime import timedelta
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .generic_bt_api.device import HatchBTDevice

# from .generic_bt_api.device import HatchBTDevice
from .const import DOMAIN, DEVICE_STARTUP_TIMEOUT_SECONDS

_LOGGER = logging.getLogger(__name__)

class HatchBTUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, logger: logging.Logger, device: HatchBTDevice, ble_device: BLEDevice,
            device_name: str, base_unique_id: str | None
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="hatchbabyrest",
            update_interval=timedelta(seconds=30),
        )
        self._device = device
        self.ble_device = ble_device
        self.device_name = device_name
        self.base_unique_id = base_unique_id

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                await self._device.update()
        except TimeoutError as exc:
            raise UpdateFailed(
                "Connection timed out while fetching data from device"
            ) from exc
        except BleakError as exc:
            raise UpdateFailed("Failed getting data from device") from exc

        return self._device
