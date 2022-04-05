from __future__ import annotations

import logging
from typing import Any

from .const import DOMAIN
from .entity import CoordinatedServerTechEntity
from .outlet import PduOutlet

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    pdu = coordinator.device

    outlets = pdu.outlets
    entities: list = []

    for outlet in outlets:
        entities.append(ServerTechPduSwitch(outlet, coordinator))

    async_add_entities(entities)


class ServerTechPduSwitch(CoordinatedServerTechEntity, SwitchEntity):
    """Representation of switch for the LED of a TPLink Smart Plug."""

    device: PduOutlet

    def __init__(self, device: PduOutlet, coordinator) -> None:
        super().__init__(device, coordinator)

    async def async_turn_on(self, **kwargs: Any) -> None:
        self.device.turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self.device.turn_off()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data[self.device.id]
        self.async_write_ha_state()

    # @property
    # def is_on(self) -> bool:
    #     return self.device.status == "On"
