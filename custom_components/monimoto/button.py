from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import MonimotoEntity


@dataclass(frozen=True, kw_only=True)
class MonimotoButtonDescription(ButtonEntityDescription):
    press_fn: Callable[[object, str], Awaitable[None]]


BUTTONS: tuple[MonimotoButtonDescription, ...] = (
    MonimotoButtonDescription(
        key="refresh_now",
        name="Refresh now",
        icon="mdi:refresh",
        entity_category=EntityCategory.DIAGNOSTIC,
        press_fn=lambda client, blename: client.async_noop(),
    ),
    MonimotoButtonDescription(
        key="start_tracking",
        name="Start tracking",
        icon="mdi:crosshairs-gps",
        press_fn=lambda client, blename: client.async_set_tracking(blename, True),
    ),
    MonimotoButtonDescription(
        key="stop_tracking",
        name="Stop tracking",
        icon="mdi:crosshairs-off",
        press_fn=lambda client, blename: client.async_set_tracking(blename, False),
    ),
    MonimotoButtonDescription(
        key="trigger_alarm",
        name="Trigger alarm",
        icon="mdi:alarm-light",
        press_fn=lambda client, blename: client.async_trigger_alarm(blename, True),
    ),
)


class MonimotoButton(MonimotoEntity, ButtonEntity):
    entity_description: MonimotoButtonDescription

    def __init__(self, coordinator, device_id: str, description: MonimotoButtonDescription) -> None:
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{self.device_slug}_{description.key}"
        self._attr_suggested_object_id = f"{self.device_slug}_{description.key}"

    async def async_press(self) -> None:
        runtime = self.coordinator.entry.runtime_data
        await self.entity_description.press_fn(runtime.client, self.device.blename)
        await runtime.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data.coordinator
    entities: list[ButtonEntity] = []

    for device_id in coordinator.data:
        for description in BUTTONS:
            entities.append(MonimotoButton(coordinator, device_id, description))

    async_add_entities(entities)
