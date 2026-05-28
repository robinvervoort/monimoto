from __future__ import annotations

from dataclasses import dataclass
import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MonimotoApiClient, TokenData
from .const import (
    CONF_API_HOST,
    CONF_EMAIL,
    CONF_VERIFY_SSL,
    DOMAIN,
    PLATFORMS,
    SERVICE_REFRESH,
    SERVICE_SNOOZE,
    SERVICE_START_TRACKING,
    SERVICE_STOP_TRACKING,
    SERVICE_TRIGGER_ALARM,
    TOKEN_STORAGE_KEY,
)
from .coordinator import MonimotoCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeData:
    client: MonimotoApiClient
    coordinator: MonimotoCoordinator


async def _async_save_token_if_changed(hass: HomeAssistant, entry: ConfigEntry) -> None:
    runtime: RuntimeData = entry.runtime_data
    token = runtime.client.token
    if not token:
        return
    new_data = dict(entry.data)
    new_data[TOKEN_STORAGE_KEY] = token.as_storage_dict()
    hass.config_entries.async_update_entry(entry, data=new_data)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)

    client = MonimotoApiClient(
        session,
        email=entry.data[CONF_EMAIL],
        api_host=entry.data[CONF_API_HOST],
        verify_ssl=entry.data[CONF_VERIFY_SSL],
    )

    token_data = entry.data.get(TOKEN_STORAGE_KEY)
    if token_data:
        try:
            client.set_token(TokenData.from_storage_dict(token_data))
        except Exception as err:
            _LOGGER.warning("Invalid stored token data, ignoring it: %s", err)

    coordinator = MonimotoCoordinator(hass, entry, client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        _LOGGER.exception("Monimoto first refresh failed")
        raise

    entry.runtime_data = RuntimeData(client=client, coordinator=coordinator)
    await _async_save_token_if_changed(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_handle_refresh(call: ServiceCall) -> None:
        runtime: RuntimeData = entry.runtime_data
        await runtime.coordinator.async_request_refresh()
        await _async_save_token_if_changed(hass, entry)

    async def async_handle_start_tracking(call: ServiceCall) -> None:
        runtime: RuntimeData = entry.runtime_data
        blename = call.data["blename"]
        await runtime.client.async_set_tracking(blename, True)
        await runtime.coordinator.async_request_refresh()
        await _async_save_token_if_changed(hass, entry)

    async def async_handle_stop_tracking(call: ServiceCall) -> None:
        runtime: RuntimeData = entry.runtime_data
        blename = call.data["blename"]
        await runtime.client.async_set_tracking(blename, False)
        await runtime.coordinator.async_request_refresh()
        await _async_save_token_if_changed(hass, entry)

    async def async_handle_snooze(call: ServiceCall) -> None:
        runtime: RuntimeData = entry.runtime_data
        blename = call.data["blename"]
        duration_sec = call.data["duration_sec"]
        await runtime.client.async_set_snooze(blename, duration_sec)
        await runtime.coordinator.async_request_refresh()
        await _async_save_token_if_changed(hass, entry)

    async def async_handle_trigger_alarm(call: ServiceCall) -> None:
        runtime: RuntimeData = entry.runtime_data
        blename = call.data["blename"]
        await runtime.client.async_trigger_alarm(blename, True)
        await runtime.coordinator.async_request_refresh()
        await _async_save_token_if_changed(hass, entry)

    hass.services.async_register(DOMAIN, SERVICE_REFRESH, async_handle_refresh)
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_TRACKING,
        async_handle_start_tracking,
        schema=vol.Schema({vol.Required("blename"): str}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_TRACKING,
        async_handle_stop_tracking,
        schema=vol.Schema({vol.Required("blename"): str}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SNOOZE,
        async_handle_snooze,
        schema=vol.Schema(
            {
                vol.Required("blename"): str,
                vol.Required("duration_sec"): int,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_ALARM,
        async_handle_trigger_alarm,
        schema=vol.Schema({vol.Required("blename"): str}),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
    hass.services.async_remove(DOMAIN, SERVICE_START_TRACKING)
    hass.services.async_remove(DOMAIN, SERVICE_STOP_TRACKING)
    hass.services.async_remove(DOMAIN, SERVICE_SNOOZE)
    hass.services.async_remove(DOMAIN, SERVICE_TRIGGER_ALARM)
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
