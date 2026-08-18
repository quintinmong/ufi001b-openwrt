# Licensing and redistribution notice

Except where a file or directory says otherwise, original code authored for
this repository is offered under GPL-2.0-only. This default does not relicense
third-party material. See `LICENSE`, `THIRD_PARTY_NOTICES.md`, and the SPDX
identifier in each applicable source file.

Copyright (C) 2026 quintinmong for original project portions only. This notice
does not claim copyright in third-party material.

The OpenStick README at commit
`4be50dbf89834b9bff49b4f364aa25ec9f1a36c1` contains a community request against
commercial use. This repository records that provenance but does not treat the
request as an additional license restriction on GPL-covered code. Imposing such
a restriction would conflict with the rights already granted by the GPL.

This repository must not contain a device's full eMMC backup, device-unique
EFS/NV data, Qualcomm firmware blobs, SIM information, subscription URLs,
private signing keys, or other credentials.

Qualcomm firmware is separately licensed proprietary material. Its upstream
license governs any independently obtained copy:

https://github.com/HandsomeMod/qcom-firmware/blob/fc0ce66ecb7dcc1293c1e29cad2d7f566221efca/LICENSE

No Qualcomm firmware blob is stored in this repository or included in public
Actions artifacts or Releases. A local build that explicitly adds such
material is outside the public release path and remains subject to the QTI
license. Public binary releases must follow `SOURCE-COMPLIANCE.md`.
