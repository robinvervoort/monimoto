from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


def _dt_from_unix(value: int | float | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=UTC)


def _dt_from_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        return None


@dataclass(slots=True)
class MonimotoReport:
    timestamp: datetime | None
    message_text: str | None
    latitude: float | None
    longitude: float | None
    battery_percent: int | None
    battery_temperature: int | None
    gsm_level: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "MonimotoReport":
        coords = (
            data.get("location", {})
            .get("gps", {})
            .get("coordinates", {})
        )
        battery = data.get("battery", {})
        network = data.get("network", {})

        return cls(
            timestamp=_dt_from_unix(data.get("time")),
            message_text=data.get("message_text"),
            latitude=coords.get("latitude"),
            longitude=coords.get("longitude"),
            battery_percent=battery.get("level_percent"),
            battery_temperature=battery.get("temperature"),
            gsm_level=network.get("gsm_level"),
            raw=data,
        )


@dataclass(slots=True)
class MonimotoDevice:
    device_id: str
    blename: str
    name: str
    imei: str | None
    iccid: str | None
    uid: str | None
    battery_percentage: int | None
    battery_low: bool | None
    battery_charging: bool | None
    battery_faulty: bool | None
    temperature: int | None
    sim_status_label: str | None
    sim_is_deactivated: bool | None
    fw_version: str | None
    modem_fw_version: str | None
    device_status: int | None
    device_status_label: str | None
    tracking: int | None
    regular_ping_interval_min: int | None
    key_battery: int | None
    latitude: float | None
    longitude: float | None
    last_known_location_updated_at: datetime | None
    last_report: MonimotoReport | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "MonimotoDevice":
        keys = data.get("keys") or []
        first_key = keys[0] if keys else {}

        last_known = data.get("last_known_location", {})
        coords = (
            last_known.get("location", {})
            .get("gps", {})
            .get("coordinates", {})
        )

        embedded_reports = data.get("reports") or []
        last_report = (
            MonimotoReport.from_api(embedded_reports[0])
            if embedded_reports
            else None
        )

        blename = data.get("blename", "")
        return cls(
            device_id=blename or data.get("imei") or data.get("uid") or "unknown",
            blename=blename,
            name=data.get("mm_name") or blename or "Monimoto",
            imei=data.get("imei"),
            iccid=data.get("iccid"),
            uid=data.get("uid"),
            battery_percentage=data.get("battery_percentage"),
            battery_low=data.get("battery_low"),
            battery_charging=data.get("battery_charging"),
            battery_faulty=data.get("battery_faulty"),
            temperature=data.get("temperature"),
            sim_status_label=data.get("sim_status_label"),
            sim_is_deactivated=data.get("sim_is_deactivated"),
            fw_version=data.get("fw_version"),
            modem_fw_version=data.get("modem_fw_version"),
            device_status=data.get("device_status"),
            device_status_label=data.get("device_status_label"),
            tracking=data.get("tracking"),
            regular_ping_interval_min=data.get("regular_ping_interval_min"),
            key_battery=first_key.get("battery"),
            latitude=coords.get("latitude"),
            longitude=coords.get("longitude"),
            last_known_location_updated_at=_dt_from_iso(
                last_known.get("updated_at")
            ),
            last_report=last_report,
            raw=data,
        )
