"""Component to embed TP-Link smart home devices."""
from __future__ import annotations

from datetime import timedelta
import logging

from .pdu import ServerTechPDU

from homeassistant.core import HomeAssistant
from homeassistant.helpers.debounce import Debouncer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

REQUEST_REFRESH_DELAY = 0.35


class ServerTechPDUDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator to gather data for a specific Servertech PDU device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: ServerTechPDU,
    ) -> None:
        """Initialize DataUpdateCoordinator to gather data for specific PDU Outlet."""
        self.device = device
        update_interval = timedelta(seconds=10)
        super().__init__(
            hass,
            _LOGGER,
            name=device.name,
            update_interval=update_interval,
            # We don't want an immediate refresh since the device
            # takes a moment to reflect the state change
            request_refresh_debouncer=Debouncer(
                hass, _LOGGER, cooldown=REQUEST_REFRESH_DELAY, immediate=False
            ),
        )

    async def _async_update_data(self) -> None:
        """Fetch all device and sensor data from api."""
        try:
            # _LOGGER.info("Refreshing PDU")
            return self.device.update_all()
        except Exception as ex:
            raise UpdateFailed(ex) from ex
