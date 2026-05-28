from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import ATTR_DEVICE_ID, ATTR_RAW, DOMAIN


class MonimotoEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id

    @property
    def device(self):
        return self.coordinator.data[self._device_id]

    @property
    def device_name(self) -> str:
        return self.device.name or "Monimoto"

    @property
    def device_slug(self) -> str:
        return slugify(self.device_name)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            manufacturer="Monimoto",
            name=self.device_name,
            model="Monimoto Tracker",
            serial_number=self.device.imei or self.device.iccid or self._device_id,
            sw_version=self.device.fw_version,
        )

    @property
    def available(self) -> bool:
        return self._device_id in self.coordinator.data and self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        return {
            ATTR_DEVICE_ID: self._device_id,
            ATTR_RAW: self.device.raw,
            "blename": self.device.blename,
            "uid": self.device.uid,
            "imei": self.device.imei,
            "iccid": self.device.iccid,
        }
