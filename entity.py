from __future__ import annotations

import logging

from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ServerTechPDUDataUpdateCoordinator
from .outlet import PduOutlet


_LOGGER = logging.getLogger(__name__)


class CoordinatedServerTechEntity(
    CoordinatorEntity[ServerTechPDUDataUpdateCoordinator]
):
    """Common base class for all ServerTech entities"""

    def __init__(self, device, coordinator: ServerTechPDUDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self.device = device
        self._attr_name = self.device.name
        self._attr_unique_id = f"{self.device.id}"

    @property
    def device_info(self) -> DeviceInfo | None:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.device.mac_address)},
            name=self.coordinator.device.name,
            manufacturer="ServerTech",
        )
