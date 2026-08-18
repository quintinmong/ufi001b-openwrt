# Binary release source compliance

Public firmware and APK releases contain programs under multiple free-software
licenses. Every public binary release must offer equivalent access, from the
same GitHub Release, to the complete corresponding source used for that build.

The release workflow therefore requires all of the following assets:

- the boot and rootfs images and the independently installable APKs;
- `ufi001b-openwrt-corresponding-source.tar.zst`;
- `corresponding-source-SHA256SUMS`;
- `LICENSE`, `THIRD_PARTY_NOTICES.md`, `NOTICE.md`, and the immutable source
  lock file used by the build.

The corresponding-source archive is produced from the actual prepared OpenWrt
tree after feeds and package sources have been downloaded. Generated binaries,
temporary build directories, signing keys, and proprietary Qualcomm firmware
are excluded. The archive includes the OpenWrt build files, configured feeds,
local modifications, configuration, downloaded source archives, and the exact
Mihomo source archive corresponding to the distributed `v1.19.29` executable.

GitHub's automatically generated source archive for the signed release tag is
also part of the source offer and contains this repository's orchestration and
release scripts. A release must not be published if either source asset is
missing, fails its checksum, contains a private key, or contains proprietary
Qualcomm firmware.

The source offer applies for as long as the corresponding binaries remain
available. Maintainers must not delete the source assets while retaining the
binary assets.
