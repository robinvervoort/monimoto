from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity


class MonimotoTrackingSelect(MonimotoEntity, SelectEntity):
    _attr_name = "Tracking mode"
    _attr_icon = "mdi:map-marker-path"
    _attr_options = ["off", "on"]
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{self.device_slug}_tracking_mode"
        self._attr_suggested_object_id = f"{self.device_slug}_tracking_mode"

    @property
    def current_option(self) -> str:
        return "on" if self.device.tracking else "off"

    async def async_select_option(self, option: str) -> None:
        runtime = self.coordinator.entry.runtime_data
        await runtime.client.async_set_tracking(self.device.blename, option == "on")
        await runtime.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [MonimotoTrackingSelect(coordinator, device_id) for device_id in coordinator.data]
    )
