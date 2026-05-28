# Monimoto Home Assistant Integration

Unofficial Home Assistant custom integration for [Monimoto](https://monimoto.com) GPS motorcycle trackers.

## Features

For each Monimoto tracker on your account, the integration creates:

**Sensors**
- Battery percentage
- Key fob battery percentage
- Tracker temperature
- Device status
- Last message
- Last report time / last known location updated
- Regular ping interval
- SIM status, firmware, IMEI, ICCID, GSM level
- Last known latitude / longitude

**Binary sensors**
- Battery low
- Battery charging
- SIM deactivated
- Tracking enabled

**Device tracker**
- Live GPS location (shown on the Home Assistant map)

**Controls**
- *Buttons:* Refresh now, Start tracking, Stop tracking, Trigger alarm
- *Select:* Tracking mode (on/off)
- *Number:* Snooze duration (60 s – 86 400 s, step 60 s)

**Services**
- `monimoto.refresh` – force a data refresh
- `monimoto.start_tracking` – enable tracking for a device
- `monimoto.stop_tracking` – disable tracking for a device
- `monimoto.snooze` – set snooze duration for a device
- `monimoto.trigger_alarm` – trigger the alarm on a device

## Installation

### HACS (recommended)

1. Open HACS → Integrations → ⋮ → Custom repositories.
2. Add `https://github.com/robinvervoort/monimoto` as an **Integration**.
3. Search for **Monimoto** and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/monimoto` folder to your `<config>/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add integration** and search for **Monimoto**.
2. Enter your Monimoto account email address.
3. Enter the verification code you receive by email.
4. Done — your tracker(s) will appear as devices.

### Options

After setup you can change the **poll interval** (default: 900 s / 15 min) via the integration's **Configure** button.

## Troubleshooting — 417 "Update the app" error

The Monimoto API authenticates API clients using a password embedded in the official app binary. If Monimoto releases a new app version and rotates this password, the integration will receive HTTP 417 until the new password is entered.

### How to find the current API password (Android)

1. **Install [HTTPToolkit](https://httptoolkit.com/android/)** on your desktop and its companion app on your phone.  
   *(Alternative: [PCAPdroid](https://play.google.com/store/apps/details?id=com.emanuelef.remote_capture) — no certificate required.)*
2. Start intercepting, then open the Monimoto app and tap **Log in**.
3. In HTTPToolkit, find the `POST https://octopus-lb.monimoto.com/auth/login` request.
4. Copy the value of the **`Authorization`** header — it looks like `Basic YXBwL...`.
5. Decode the Base64 part (e.g. `echo "YXBwL..." | base64 -d` in a terminal). The result is `username:password`.
6. The **password** part (after the colon) is what you need.

### Entering the password in Home Assistant

When adding the integration, paste the password into the **"API password"** field. Leave it blank to use the built-in default.

## Notes

- The Monimoto API is cloud-based (`cloud_polling`). Location updates depend on the tracker reporting interval, not just the HA poll interval.
- Tracking must be enabled in the app or via this integration for real-time location updates.
