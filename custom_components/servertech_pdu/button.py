"""Representation of ServerTech buttons."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import CoordinatedServerTechEntity
from .outlet import PduOutlet


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up reboot buttons from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    pdu = coordinator.device

    outlets = pdu.outlets
    entities: list = []

    for outlet in outlets:
        entities.append(ServerTechRebootButton(outlet, coordinator))

    async_add_entities(entities)


class ServerTechRebootButton(CoordinatedServerTechEntity, ButtonEntity):
    """Representation of a scan_clients button entity."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, device: PduOutlet, coordinator) -> None:
        super().__init__(device, coordinator)
        """Initialize a servertech reboot switch button entity."""
        self._attr_name = f"Reboot ({self.device.name})"
        self._attr_unique_id = (
            f"reboot_{self.device.id}_{coordinator.device.mac_address}"
        )

    async def async_press(self) -> None:
        """Press the button."""
        self.device.reboot()
