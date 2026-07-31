# Licensing and redistribution notice

This repository may contain original build scripts and patch descriptions, but
must not contain a device's full eMMC backup, device-unique EFS/NV data,
Qualcomm firmware blobs, SIM information, subscription URLs, or private keys.

This project follows the use statement in the OpenStick README at commit
`4be50dbf89834b9bff49b4f364aa25ec9f1a36c1`: the project is publicly available,
but commercial use is prohibited. OpenStick identifies commercial use as:

- selling system images or derivatives that are otherwise freely available;
- charging for artifacts built through the related build system; or
- large-scale sale of devices carrying OpenStick Linux.

Upstream statement:

https://github.com/OpenStick/OpenStick/blob/4be50dbf89834b9bff49b4f364aa25ec9f1a36c1/README.md

Qualcomm firmware is separately licensed material. The QTI license linked by
the upstream firmware repository governs its use and redistribution:

https://github.com/HandsomeMod/qcom-firmware/blob/main/LICENSE

No Qualcomm firmware blob is stored in this repository or included in public
Actions artifacts. A local build that explicitly adds such material is outside
the public release path and remains subject to the QTI license. Every other
incorporated component remains subject to its own license.
