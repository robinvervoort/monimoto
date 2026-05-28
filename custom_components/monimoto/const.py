from __future__ import annotations

DOMAIN = "monimoto"
PLATFORMS = ["sensor", "binary_sensor", "device_tracker", "button", "number", "select"]

CONF_EMAIL = "email"
CONF_POLL_INTERVAL = "poll_interval"
CONF_API_HOST = "api_host"
CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_API_HOST = "https://octopus-lb.monimoto.com"
DEFAULT_POLL_INTERVAL = 900

ATTR_DEVICE_ID = "device_id"
ATTR_RAW = "raw"

TOKEN_STORAGE_KEY = "token"

ENDPOINT_AUTH_LOGIN = "/auth/login"
ENDPOINT_AUTH_CONFIRM = "/auth/confirm"
ENDPOINT_AUTH_TOKENS = "/auth/tokens"
ENDPOINT_DEVICES = "/devices"
ENDPOINT_REPORTS_TMPL = "/device/{blename}/reports"
ENDPOINT_TRACK_TMPL = "/device/{blename}/track"
ENDPOINT_SNOOZE_TMPL = "/device/{blename}/snooze"
ENDPOINT_ALARM_TMPL = "/device/{blename}/alarm"

BASIC_AUTH_USER = "app-basic-auth-octopus-prod"
BASIC_AUTH_PASS = "cBksj9Ipw2Bxn399284hd"

SERVICE_REFRESH = "refresh"
SERVICE_START_TRACKING = "start_tracking"
SERVICE_STOP_TRACKING = "stop_tracking"
SERVICE_SNOOZE = "snooze"
SERVICE_TRIGGER_ALARM = "trigger_alarm"
