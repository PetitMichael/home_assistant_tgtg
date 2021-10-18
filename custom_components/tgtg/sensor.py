"""Platform for sensor integration."""
from __future__ import annotations
import logging
import voluptuous as vol

from tgtg import TgtgClient

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers import config_validation as cv

DOMAIN = "tgtg"
CONF_ITEM = "item"
_LOGGER = logging.getLogger(DOMAIN)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_ITEM): cv.ensure_list,
    }
)

global tgtg_client


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""

    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    global tgtg_client
    tgtg_client = TgtgClient(email=username, password=password)

    for each_item_id in config[CONF_ITEM]:
        add_entities([TGTGSensor(each_item_id)])


class TGTGSensor(SensorEntity):
    """Representation of a Sensor."""

    global tgtg_client
    item_id = None
    store_name = None
    item_qty = None

    def __init__(self, item_id):
        """Initialize the sensor."""
        self.item_id = item_id
        self.update()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"TGTG {self.store_name}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"tgtg_{self.item_id}"

    @property
    def icon(self):
        """Return an icon."""
        return "mdi:storefront-outline"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "pcs"
        
    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.item_qty

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        global tgtg_client
        tgtg_answer = tgtg_client.get_item(item_id=self.item_id)
        self.store_name = tgtg_answer["display_name"]
        self.item_qty = tgtg_answer["items_available"]
