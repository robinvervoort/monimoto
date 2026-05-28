from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity
from .models import MonimotoDevice


@dataclass(frozen=True, kw_only=True)
class MonimotoBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[MonimotoDevice], bool | None]


BINARY_SENSORS: tuple[MonimotoBinarySensorDescription, ...] = (
    MonimotoBinarySensorDescription(
        key="battery_low",
        name="Battery low",
        device_class=BinarySensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.battery_low,
    ),
    MonimotoBinarySensorDescription(
        key="battery_charging",
        name="Battery charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.battery_charging,
    ),
    MonimotoBinarySensorDescription(
        key="sim_deactivated",
        name="SIM deactivated",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.sim_is_deactivated,
    ),
    MonimotoBinarySensorDescription(
        key="tracking_enabled",
        name="Tracking enabled",
        icon="mdi:crosshairs-gps",
        value_fn=lambda d: bool(d.tracking),
    ),
)


class MonimotoBinarySensor(MonimotoEntity, BinarySensorEntity):
    entity_description: MonimotoBinarySensorDescription

    def __init__(self, coordinator, device_id: str, description: MonimotoBinarySensorDescription) -> None:
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{self.device_slug}_{description.key}"
        self._attr_suggested_object_id = f"{self.device_slug}_{description.key}"

    @property
    def is_on(self):
        return self.entity_description.value_fn(self.device)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[BinarySensorEntity] = []

    for device_id in coordinator.data:
        for description in BINARY_SENSORS:
            entities.append(MonimotoBinarySensor(coordinator, device_id, description))

    async_add_entities(entities)
