from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity


class MonimotoSnoozeNumber(MonimotoEntity, NumberEntity):
    _attr_name = "Snooze duration"
    _attr_icon = "mdi:timer-sand"
    _attr_native_min_value = 60
    _attr_native_max_value = 86400
    _attr_native_step = 60
    _attr_native_unit_of_measurement = "s"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator, device_id)
        self._attr_unique_id = f"{self.device_slug}_snooze_duration"
        self._attr_suggested_object_id = f"{self.device_slug}_snooze_duration"
        self._attr_native_value = 3600

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = int(value)
        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [MonimotoSnoozeNumber(coordinator, device_id) for device_id in coordinator.data]
    )
