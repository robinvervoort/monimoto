from __future__ import annotations

from datetime import timedelta
import logging
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MonimotoApiClient, MonimotoApiError, MonimotoAuthError
from .const import CONF_POLL_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class MonimotoCoordinator(DataUpdateCoordinator[dict[str, object]]):
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: MonimotoApiClient,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get(
                    CONF_POLL_INTERVAL,
                    entry.data[CONF_POLL_INTERVAL],
                )
            ),
        )
        self.entry = entry
        self.client = client

    async def _async_update_data(self) -> dict[str, object]:
        try:
            devices = await self.client.async_get_devices()
        except MonimotoAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except MonimotoApiError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

        enriched: dict[str, object] = {}
        from_unix = int(time.time()) - 7 * 24 * 3600

        for device in devices:
            try:
                reports = await self.client.async_get_reports(
                    device.blename,
                    from_unix=from_unix,
                )
            except (MonimotoApiError, Exception):
                reports = []

            if reports:
                device.last_report = reports[0]

            enriched[device.device_id] = device

        return enriched
