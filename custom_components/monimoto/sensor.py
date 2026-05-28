from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity
from .models import MonimotoDevice


@dataclass(frozen=True, kw_only=True)
class MonimotoSensorDescription(SensorEntityDescription):
    value_fn: Callable[[MonimotoDevice], object]


SENSORS: tuple[MonimotoSensorDescription, ...] = (
    MonimotoSensorDescription(
        key="battery_percentage",
        name="Battery percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.battery_percentage,
    ),
    MonimotoSensorDescription(
        key="key_battery",
        name="Key battery",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.key_battery,
    ),
    MonimotoSensorDescription(
        key="temperature",
        name="Tracker temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.temperature,
    ),
    MonimotoSensorDescription(
        key="sim_status",
        name="SIM status",
        icon="mdi:sim",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.sim_status_label,
    ),
    MonimotoSensorDescription(
        key="firmware",
        name="Firmware",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.fw_version,
    ),
    MonimotoSensorDescription(
        key="device_status",
        name="Device status",
        icon="mdi:shield-lock",
        value_fn=lambda d: d.device_status_label,
    ),
    MonimotoSensorDescription(
        key="last_message",
        name="Last message",
        icon="mdi:message-text",
        value_fn=lambda d: d.last_report.message_text if d.last_report else None,
    ),
    MonimotoSensorDescription(
        key="last_report_time",
        name="Last report time",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.last_report.timestamp if d.last_report else None,
    ),
    MonimotoSensorDescription(
        key="last_known_location_updated_at",
        name="Last known location updated",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.last_known_location_updated_at,
    ),
    MonimotoSensorDescription(
        key="regular_ping_interval_min",
        name="Regular ping interval",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.regular_ping_interval_min,
    ),
    MonimotoSensorDescription(
        key="imei",
        name="IMEI",
        icon="mdi:barcode",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.imei,
    ),
    MonimotoSensorDescription(
        key="iccid",
        name="ICCID",
        icon="mdi:sim",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.iccid,
    ),
    MonimotoSensorDescription(
        key="gsm_level",
        name="GSM level",
        icon="mdi:signal",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.last_report.gsm_level if d.last_report else None,
    ),
    MonimotoSensorDescription(
        key="last_latitude",
        name="Last latitude",
        icon="mdi:latitude",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.last_report.latitude if d.last_report else d.latitude,
    ),
    MonimotoSensorDescription(
        key="last_longitude",
        name="Last longitude",
        icon="mdi:longitude",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.last_report.longitude if d.last_report else d.longitude,
    ),
)


class MonimotoSensor(MonimotoEntity, SensorEntity):
    entity_description: MonimotoSensorDescription

    def __init__(self, coordinator, device_id: str, description: MonimotoSensorDescription) -> None:
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{self.device_slug}_{description.key}"
        self._attr_suggested_object_id = f"{self.device_slug}_{description.key}"

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.device)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[SensorEntity] = []

    for device_id in coordinator.data:
        for description in SENSORS:
            entities.append(MonimotoSensor(coordinator, device_id, description))

    async_add_entities(entities)
