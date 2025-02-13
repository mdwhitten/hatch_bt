from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from .entity import HatchBTEntity
from .coordinator import HatchBTUpdateCoordinator
from .const import DOMAIN
from .hatch_bt_device.const import PyHatchBabyRestSound


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HatchBTMediaPlayer(coordinator)], True)


class HatchBTMediaPlayer(HatchBTEntity, MediaPlayerEntity):

    _previous_sound: PyHatchBabyRestSound

    def __init__(self, coordinator: HatchBTUpdateCoordinator) -> None:
        """Initialize the Device."""
        super().__init__(coordinator)

        self._name = "Sound"
        _previous_sound = self._device.sound

    @property
    def name(self):
        return self._name

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
        )

    @property
    def device_class(self) -> MediaPlayerDeviceClass | None:
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def source_list(self) -> list[str] | None:
        return [sound.name.capitalize() for sound in PyHatchBabyRestSound]

    async def async_set_volume_level(self, volume: float) -> None:
        await self._device.set_volume(int(255 * volume))
        self.async_write_ha_state()

    async def async_select_source(self, source: str) -> None:
        source_number = [
            val for val in PyHatchBabyRestSound if val.name == source.lower()
        ][0]
        self._previous_sound = PyHatchBabyRestSound(source_number)
        await self._device.set_sound(source_number)
        self.async_write_ha_state()

    @property
    def state(self) -> MediaPlayerState | None:
        if self._device.power is False:
            return MediaPlayerState.OFF

        if self._device.sound == PyHatchBabyRestSound.none:
            return MediaPlayerState.IDLE

        return MediaPlayerState.PLAYING

    @property
    def source(self) -> str | None:
        return self._device.sound.name.capitalize()

    @property
    def volume_level(self) -> float | None:
        return float(self._device.volume / 255)

    async def async_media_stop(self) -> None:
        self._previous_sound = self._device.sound
        await self._device.set_sound(PyHatchBabyRestSound.none)
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        if previous_sound := getattr(self, "_previous_sound"):
            await self._device.set_sound(previous_sound)
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        if self._device.power:
            await self._device.power_off()
            # Update this individual state, then the rest of the states
            self.async_write_ha_state()
            # Update the data
            await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        if not self._device.power:
            await self._device.power_on()
            # Update this individual state, then the rest of the states
            self.async_write_ha_state()
            # Update the data
            await self.coordinator.async_request_refresh()