from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import aiohttp

from .const import (
    APP_USER_AGENT,
    BASIC_AUTH_PASS,
    BASIC_AUTH_USER,
    ENDPOINT_ALARM_TMPL,
    ENDPOINT_AUTH_CONFIRM,
    ENDPOINT_AUTH_LOGIN,
    ENDPOINT_AUTH_TOKENS,
    ENDPOINT_DEVICES,
    ENDPOINT_REPORTS_TMPL,
    ENDPOINT_SNOOZE_TMPL,
    ENDPOINT_TRACK_TMPL,
)
from .models import MonimotoDevice, MonimotoReport


class MonimotoApiError(Exception):
    """Base API error."""


class MonimotoAuthError(MonimotoApiError):
    """Authentication failure."""


@dataclass(slots=True)
class LoginChallenge:
    uid: str
    email_challenge: str | None
    sms_challenge: str | None


@dataclass(slots=True)
class TokenData:
    access_token: str
    refresh_token: str | None
    expires_at: datetime

    @classmethod
    def from_confirm_response(cls, data: dict[str, Any]) -> "TokenData":
        expires_at = datetime.now(tz=UTC) + timedelta(hours=7, minutes=30)
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
        )

    @classmethod
    def from_refresh_response(cls, data: dict[str, Any]) -> "TokenData":
        expires_at = datetime.now(tz=UTC) + timedelta(hours=7, minutes=30)
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
        )

    def as_storage_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at.isoformat(),
        }

    @classmethod
    def from_storage_dict(cls, data: dict[str, Any]) -> "TokenData":
        expires_at = datetime.fromisoformat(data["expires_at"])
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_at=expires_at,
        )


class MonimotoApiClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        email: str,
        api_host: str,
        verify_ssl: bool,
    ) -> None:
        self._session = session
        self._email = email.strip().lower()
        self._api_host = api_host.rstrip("/")
        self._verify_ssl = verify_ssl
        self._token: TokenData | None = None

    @property
    def token(self) -> TokenData | None:
        return self._token

    def set_token(self, token: TokenData | None) -> None:
        self._token = token

    def _basic_auth(self) -> aiohttp.BasicAuth:
        return aiohttp.BasicAuth(BASIC_AUTH_USER, BASIC_AUTH_PASS)

    def _common_headers(self) -> dict[str, str]:
        return {
            "User-Agent": APP_USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Accept-Language": "en",
            "X-App-Version": APP_VERSION,
        }

    def _bearer_headers(self) -> dict[str, str]:
        if not self._token:
            raise MonimotoAuthError("Not authenticated")
        return {
            **self._common_headers(),
            "Authorization": f"Bearer {self._token.access_token}",
        }

    async def async_request_email_login(self) -> LoginChallenge:
        url = f"{self._api_host}{ENDPOINT_AUTH_LOGIN}"
        payload = {
            "email": self._email,
            "firebase_user_id": None,
            "language": "en",
            "phone": None,
            "platform": "android",
        }
        async with self._session.post(
            url,
            json=payload,
            headers=self._common_headers(),
            auth=self._basic_auth(),
            ssl=self._verify_ssl,
        ) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise MonimotoAuthError(f"Login request failed: {resp.status} {text}")
            data = await resp.json(content_type=None)
            return LoginChallenge(
                uid=data["uid"],
                email_challenge=data.get("email_challenge"),
                sms_challenge=data.get("sms_challenge"),
            )

    async def async_confirm_email_code(
        self,
        *,
        uid: str,
        email_challenge: str,
        email_code: int,
    ) -> TokenData:
        url = f"{self._api_host}{ENDPOINT_AUTH_CONFIRM}"
        payload = {
            "email_challenge": email_challenge,
            "email_code": email_code,
            "sms_challenge": None,
            "sms_code": None,
            "uid": uid,
        }
        async with self._session.post(
            url,
            json=payload,
            headers=self._common_headers(),
            auth=self._basic_auth(),
            ssl=self._verify_ssl,
        ) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise MonimotoAuthError(f"Confirm failed: {resp.status} {text}")
            data = await resp.json(content_type=None)
            self._token = TokenData.from_confirm_response(data)
            return self._token

    async def async_refresh_token(self) -> TokenData:
        if not self._token or not self._token.refresh_token:
            raise MonimotoAuthError("No refresh token available")
        url = f"{self._api_host}{ENDPOINT_AUTH_TOKENS}"
        payload = {"refresh_token": self._token.refresh_token}
        async with self._session.post(
            url,
            json=payload,
            headers=self._common_headers(),
            auth=self._basic_auth(),
            ssl=self._verify_ssl,
        ) as resp:
            text = await resp.text()
            if resp.status >= 400:
                raise MonimotoAuthError(f"Refresh failed: {resp.status} {text}")
            data = await resp.json(content_type=None)
            self._token = TokenData.from_refresh_response(data)
            return self._token

    async def _ensure_token(self) -> None:
        if not self._token:
            raise MonimotoAuthError("Not authenticated")
        if self._token.expires_at <= datetime.now(tz=UTC):
            await self.async_refresh_token()

    async def _get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        await self._ensure_token()
        url = f"{self._api_host}{path}"
        async with self._session.get(
            url,
            headers=self._bearer_headers(),
            params=params,
            ssl=self._verify_ssl,
        ) as resp:
            text = await resp.text()
            if resp.status == 401:
                await self.async_refresh_token()
                async with self._session.get(
                    url,
                    headers=self._bearer_headers(),
                    params=params,
                    ssl=self._verify_ssl,
                ) as retry_resp:
                    retry_text = await retry_resp.text()
                    if retry_resp.status >= 400:
                        raise MonimotoAuthError(
                            f"Unauthorized after refresh: {retry_resp.status} {retry_text}"
                        )
                    return await retry_resp.json(content_type=None)
            if resp.status >= 400:
                raise MonimotoApiError(f"GET failed: {resp.status} {text}")
            return await resp.json(content_type=None)

    async def _post_json(self, path: str, payload: dict[str, Any]) -> Any:
        await self._ensure_token()
        url = f"{self._api_host}{path}"
        async with self._session.post(
            url,
            json=payload,
            headers=self._bearer_headers(),
            ssl=self._verify_ssl,
        ) as resp:
            text = await resp.text()
            if resp.status == 401:
                await self.async_refresh_token()
                async with self._session.post(
                    url,
                    json=payload,
                    headers=self._bearer_headers(),
                    ssl=self._verify_ssl,
                ) as retry_resp:
                    retry_text = await retry_resp.text()
                    if retry_resp.status >= 400:
                        raise MonimotoAuthError(
                            f"POST unauthorized after refresh: {retry_resp.status} {retry_text}"
                        )
                    return await retry_resp.json(content_type=None)
            if resp.status >= 400:
                raise MonimotoApiError(f"POST failed: {resp.status} {text}")
            return await resp.json(content_type=None)

    async def async_get_devices(self) -> list[MonimotoDevice]:
        data = await self._get_json(ENDPOINT_DEVICES)
        return [MonimotoDevice.from_api(item) for item in data]

    async def async_get_reports(self, blename: str, *, from_unix: int) -> list[MonimotoReport]:
        data = await self._get_json(
            ENDPOINT_REPORTS_TMPL.format(blename=blename),
            params={"from": from_unix},
        )
        return [MonimotoReport.from_api(item) for item in data]

    async def async_set_tracking(self, blename: str, enabled: bool) -> dict[str, Any]:
        return await self._post_json(
            ENDPOINT_TRACK_TMPL.format(blename=blename),
            {"tracking": 1 if enabled else 0},
        )

    async def async_set_snooze(self, blename: str, duration_sec: int) -> dict[str, Any]:
        return await self._post_json(
            ENDPOINT_SNOOZE_TMPL.format(blename=blename),
            {"duration_sec": duration_sec},
        )

    async def async_trigger_alarm(self, blename: str, forced_alarm: bool = True) -> dict[str, Any]:
        return await self._post_json(
            ENDPOINT_ALARM_TMPL.format(blename=blename),
            {"forced_alarm": forced_alarm},
        )

    async def async_noop(self) -> None:
        return None
