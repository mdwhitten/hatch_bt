"""Support for generic bluetooth devices."""

import logging

from homeassistant.components.bluetooth.match import BluetoothCallbackMatcher
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import HatchBTUpdateCoordinator
from .hatch_bt_device.device import HatchBTDevice


_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SWITCH, Platform.LIGHT, Platform.MEDIA_PLAYER]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Generic BT from a config entry."""
    assert entry.unique_id is not None
    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    address: str = entry.data[CONF_ADDRESS]

    scanner = bluetooth.async_get_scanner(hass)
    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper())

    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find Generic BT Device with address {address}")

    device = HatchBTDevice(ble_device)
    await device.get_client()

    if not device.connected:
        raise ConfigEntryNotReady(f"Failed to connect to: {ble_device.address}")

    try:
        coordinator = HatchBTUpdateCoordinator(hass, _LOGGER, device, ble_device, entry.title, entry.unique_id)

        await coordinator.async_config_entry_first_refresh()

        hass.data[DOMAIN][entry.entry_id] = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True
    except:
        _LOGGER.exception("Exception occured during setup; closing connection")
        await device.disconnect()
        raise

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    device: HatchBTDevice = hass.data[DOMAIN][entry.entry_id].data

    await device.disconnect()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
