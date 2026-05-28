from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity


class MonimotoTracker(MonimotoEntity, TrackerEntity):
    _attr_name = "Location"
    _attr_icon = "mdi:map-marker"

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{self.device_slug}_location"
        self._attr_suggested_object_id = f"{self.device_slug}_location"

    @property
    def latitude(self):
        if self.device.last_report and self.device.last_report.latitude is not None:
            return self.device.last_report.latitude
        return self.device.latitude

    @property
    def longitude(self):
        if self.device.last_report and self.device.last_report.longitude is not None:
            return self.device.last_report.longitude
        return self.device.longitude

    @property
    def source_type(self):
        if self.latitude is not None and self.longitude is not None:
            return SourceType.GPS
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [MonimotoTracker(coordinator, device_id) for device_id in coordinator.data]
    )
