# Tapo Bulbs (TPAP)

A Home Assistant integration that adds support for Tapo devices using the newer TPAP encryption, which the built-in TP-Link integration reports as "Unsupported device".

It is a copy of the built-in TP-Link integration (Home Assistant 2026.11.0) running on a bundled python-kasa 0.12.0 with TPAP support, so you get the same entities as the built-in integration: lights with effects and presets, switches, sensors, numbers, selects, buttons and so on.

## Supported devices

- Tapo smart bulbs, e.g. L630, with all the usual entities
- Other Tapo devices using TPAP are expected to work but are untested

Cameras and robot vacuums are not included.

## Install

1. In HACS, add `https://github.com/leaha00/ha-tapo-trap-plugin` as a custom repository (type: Integration).
2. Download **Tapo Bulbs (TPAP)** and restart Home Assistant.
3. Go to Settings -> Devices & services -> Add integration -> **Tapo Bulbs (TPAP)**.
4. Enter the device's IP address, then your TP-Link / Tapo account email and password.

Devices are added by IP address. Automatic discovery is turned off so devices are not duplicated with the built-in TP-Link integration.

## Requirements

- Home Assistant 2026.11.0 or newer.
- The device must be added to your Tapo app under the same TP-Link account whose email and password you enter here. Devices that are not bound to that account reject the login.
- Entries created by the older 0.1.x versions are converted automatically on first load.

## Credits and licence

Integration code is derived from the Home Assistant core `tplink` integration (Apache-2.0). The bundled library is python-kasa with the TPAP work from ZeliardM's fork / python-kasa PR #1592 (GPL-3.0-or-later). Remove this integration once Home Assistant core supports TPAP.
