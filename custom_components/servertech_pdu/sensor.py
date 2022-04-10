from __future__ import annotations
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    POWER_WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ServerTechPDUDataUpdateCoordinator
from .entity import CoordinatedServerTechEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities: list[ServerTechPduSensor] = []
    parent = coordinator.device

    description = SensorEntityDescription(
        key='current_power_w',
        native_unit_of_measurement=POWER_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        name="Active Power",
    )

    _LOGGER.info("SETTING UP SENSOR")
    entities = [ServerTechPduSensor(parent, coordinator, description)]

    async_add_entities(entities)


class ServerTechPduSensor(CoordinatedServerTechEntity, SensorEntity):
    def __init__(
        self,
        device,
        coordinator: ServerTechPDUDataUpdateCoordinator,
        description,
    ) -> None:
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{self.device.mac_address}_{self.entity_description.key}"
        )

    @property
    def name(self) -> str:
        return f"{self.device.name} {self.entity_description.name}"

    @property
    def native_value(self) -> float | None:
        """Return the sensors state."""
        return self.device.active_power
