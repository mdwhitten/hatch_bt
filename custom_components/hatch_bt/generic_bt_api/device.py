"""generic bt device"""

from uuid import UUID
import asyncio
import logging
from contextlib import AsyncExitStack
import time

from bleak import BleakClient
from bleak.exc import BleakError
from .const import *

_LOGGER = logging.getLogger(__name__)


class HatchBTDevice:
    """Generic BT Device Class"""
    def __init__(self, ble_device):
        self._ble_device = ble_device
        self._client: BleakClient | None = None
        self._client_stack = AsyncExitStack()
        self._lock = asyncio.Lock()

        self._power = None
        self._volume = None
        self._sound = None
        self._brightness = None

    async def update(self):
        response = await self.read_gatt(CHAR_FEEDBACK)
        self._refresh_data(response)

    async def stop(self):
        pass

    @property
    def connected(self):
        return not self._client is None

    @property
    def power(self):
        return self._power

    async def get_client(self):
        async with self._lock:
            if not self._client:
                _LOGGER.debug("Connecting")
                try:
                    self._client = await self._client_stack.enter_async_context(BleakClient(self._ble_device, timeout=60))
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on connect", exc_info=True)
                    raise
                except BleakError as exc:
                    _LOGGER.debug("Error on connect", exc_info=True)
                    raise
            else:
                _LOGGER.debug("Connection reused")


    async def write_gatt(self, target_uuid, data):
        await self.get_client()
        uuid_str = "{" + target_uuid + "}"
        uuid = UUID(uuid_str)
        data_as_bytes = bytearray(data, "utf-8")
        _LOGGER.debug(f"Writing {data} to {target_uuid}")
        await self._client.write_gatt_char(uuid, data_as_bytes, True)

    async def read_gatt(self, target_uuid):
        await self.get_client()
        uuid_str = "{" + target_uuid + "}"
        uuid = UUID(uuid_str)
        data = await self._client.read_gatt_char(uuid)
        _LOGGER.debug(f"Read {data} from {target_uuid}")
        return data
    

    async def send_command(self, data) -> None:
        await self.write_gatt(CHAR_TX, data)
        await asyncio.sleep(.25)
        response = await self.read_gatt(CHAR_FEEDBACK)

        self._refresh_data(response)
        
    def update_from_advertisement(self, advertisement):
        pass

    def _refresh_data(self, response_data) -> None:
        """ Request updated data from the device and set the local attributes. """
        response = [hex(x) for x in response_data]

        # Make sure the data is where we think it is
        assert response[5] == "0x43"  # color
        assert response[10] == "0x53"  # audio
        assert response[13] == "0x50"  # power

        red, green, blue, brightness = [int(x, 16) for x in response[6:10]]

        sound = PyHatchBabyRestSound(int(response[11], 16))

        volume = int(response[12], 16)

        power = not bool(int("11000000", 2) & int(response[14], 16))

        self._color = (red, green, blue)
        self._brightness = brightness
        self._sound = sound
        self._volume = volume
        self._power = power

        _LOGGER.debug(f"Power state is {self._power}")
        _LOGGER.debug(f"Volume state is {self._volume}")
        _LOGGER.debug(f"Sound state is {self._sound}")
        _LOGGER.debug(f"Brightness state is {self._brightness}")
        _LOGGER.debug(f"Color state is {self._color}")


    async def power_on(self):
        command = "SI{:02x}".format(1)
        await self.send_command(command)

    async def power_off(self):
        command = "SI{:02x}".format(0)
        await self.send_command(command)

    def set_sound(self, sound):
        command = "SN{:02x}".format(sound)
        self.send_command(command)

    def set_volume(self, volume):
        command = "SV{:02x}".format(volume)
        self.send_command(command)

    def set_color(self, red: int, green: int, blue: int):
        # self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(red, green, blue, self.brightness)
        self.send_command(command)

    def set_brightness(self, brightness: int):
        # self._refresh_data()

        command = "SC{:02x}{:02x}{:02x}{:02x}".format(
            self.color[0], self.color[1], self.color[2], brightness
        )
        self.send_command(command)
