from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MonimotoApiClient, MonimotoAuthError
from .const import (
    CONF_API_HOST,
    CONF_EMAIL,
    CONF_POLL_INTERVAL,
    CONF_VERIFY_SSL,
    DEFAULT_API_HOST,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    TOKEN_STORAGE_KEY,
)

_LOGGER = logging.getLogger(__name__)


class MonimotoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._user_input: dict[str, Any] | None = None
        self._uid: str | None = None
        self._email_challenge: str | None = None

    @staticmethod
    def async_get_options_flow(config_entry):
        from .options_flow import MonimotoOptionsFlow
        return MonimotoOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = dict(user_input)
            user_input[CONF_EMAIL] = user_input[CONF_EMAIL].strip().lower()
            self._user_input = user_input

            await self.async_set_unique_id(user_input[CONF_EMAIL])
            self._abort_if_unique_id_configured()

            client = MonimotoApiClient(
                async_get_clientsession(self.hass),
                email=user_input[CONF_EMAIL],
                api_host=user_input[CONF_API_HOST],
                verify_ssl=user_input[CONF_VERIFY_SSL],
            )

            try:
                challenge = await client.async_request_email_login()
            except MonimotoAuthError as err:
                _LOGGER.exception("Monimoto auth error during login request: %s", err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected Monimoto auth error: %s", err)
                errors["base"] = "cannot_connect"
            else:
                self._uid = challenge.uid
                self._email_challenge = challenge.email_challenge
                return await self.async_step_authorize()

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_API_HOST, default=DEFAULT_API_HOST): str,
                vol.Required(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
                vol.Required(CONF_VERIFY_SSL, default=True): bool,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_authorize(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        placeholders = {
            "email": self._user_input[CONF_EMAIL] if self._user_input else "",
        }

        if user_input is not None and self._user_input and self._uid and self._email_challenge:
            client = MonimotoApiClient(
                async_get_clientsession(self.hass),
                email=self._user_input[CONF_EMAIL],
                api_host=self._user_input[CONF_API_HOST],
                verify_ssl=self._user_input[CONF_VERIFY_SSL],
            )

            try:
                token = await client.async_confirm_email_code(
                    uid=self._uid,
                    email_challenge=self._email_challenge,
                    email_code=int(user_input["email_code"]),
                )
            except MonimotoAuthError as err:
                _LOGGER.exception("Monimoto auth error during confirm: %s", err)
                errors["base"] = "authorize_failed"
            except Exception as err:
                _LOGGER.exception("Unexpected Monimoto confirm error: %s", err)
                errors["base"] = "authorize_failed"
            else:
                data = dict(self._user_input)
                data[TOKEN_STORAGE_KEY] = token.as_storage_dict()
                return self.async_create_entry(title="Monimoto", data=data)

        schema = vol.Schema({vol.Required("email_code"): int})

        return self.async_show_form(
            step_id="authorize",
            data_schema=schema,
            errors=errors,
            description_placeholders=placeholders,
        )
