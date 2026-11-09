# Tapo Bulbs (TPAP)

Home Assistant custom integration for Tapo bulbs (e.g. L630) whose firmware uses the TPAP
handshake, which the python-kasa bundled with Home Assistant core does not support yet.

It bundles a renamed copy of the TPAP-capable python-kasa fork
(ZeliardM/python-kasa @ e708447, based on python-kasa PR #1592, GPL-3.0-or-later) as
`custom_components/tapo_bulbs/tapo_kasa`, so the stock library used by the built-in
TP-Link integration is left untouched.

## Install
Copy `custom_components/tapo_bulbs` into `/config/custom_components`, restart Home Assistant,
then Settings -> Devices & services -> Add integration -> "Tapo Bulbs (TPAP)".
Enter the bulb IP and your TP-Link account email/password.

Status: untested against real hardware. Remove once Home Assistant core supports TPAP.
