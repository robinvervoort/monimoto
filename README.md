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

## Notes

- The Monimoto API is cloud-based (`cloud_polling`). Location updates depend on the tracker reporting interval, not just the HA poll interval.
- Tracking must be enabled in the app or via this integration for real-time location updates.
