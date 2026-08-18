## Summary

Describe the problem and the smallest change that solves it.

## Risk and validation

- [ ] I ran `python3 scripts/verify-locks.py`.
- [ ] I ran `python3 scripts/validate-layout.py`.
- [ ] I added or updated relevant tests and documentation.
- [ ] I described build or HIL evidence, or explained why it is not required.
- [ ] I confirmed this change does not add credentials, private keys, device
      backups, Qualcomm private firmware, NV/EFS, IMEI, calibration data, or
      subscription URLs.
- [ ] I confirmed the allowed write targets remain exactly p12 `boot` and p14
      `rootfs`, or clearly marked this PR as blocked pending maintainer review.

## Release impact

State whether this changes firmware bytes, partition behavior, signing,
recovery instructions, or only source documentation/automation.
