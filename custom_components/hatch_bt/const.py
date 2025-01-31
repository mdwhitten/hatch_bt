"""Constants"""
import voluptuous as vol
from enum import Enum
from enum import IntEnum

from homeassistant.helpers.config_validation import make_entity_service_schema
import homeassistant.helpers.config_validation as cv

DOMAIN = "hatch_bt"
DEVICE_STARTUP_TIMEOUT_SECONDS = 30

class Schema(Enum):
    """General used service schema definition"""

    WRITE_GATT = make_entity_service_schema(
        {
            vol.Required("target_uuid"): cv.string,
            vol.Required("data"): cv.string
        }
    )
    READ_GATT = make_entity_service_schema(
        {
            vol.Required("target_uuid"): cv.string
        }
    )
    TURN_OFF = make_entity_service_schema(
        {
            vol.Required("dummy"): cv.string
        }
    )
    TURN_ON = make_entity_service_schema(
        {
            vol.Required("dummy"): cv.string
        }
    )

COLOR_GRADIENT = (254, 254, 254)  # setting this color turns on Gradient mode
CHAR_TX = "02240002-5efd-47eb-9c1a-de53f7a2b232"
CHAR_FEEDBACK = "02260002-5efd-47eb-9c1a-de53f7a2b232"
BT_MANUFACTURER_ID = 1076


class PyHatchBabyRestSound(IntEnum):
    none = 0
    stream = 2
    noise = 3
    dryer = 4
    ocean = 5
    wind = 6
    rain = 7
    bird = 9
    crickets = 10
    brahms = 11
    twinkle = 13
    rockabye = 14