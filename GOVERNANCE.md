# Project governance

## Scope

UFI001B OpenWrt maintains a reproducible, reviewable firmware build and a safe
flashing boundary for Qualcomm MSM8916 devices using the UFI001B PCB. The public
project does not redistribute device-unique data or proprietary Qualcomm
firmware.

## Maintainer

[@quintinmong](https://github.com/quintinmong) is the current core maintainer
and has write access to the repository. The maintainer is responsible for:

- triaging Issues and reviewing pull requests;
- keeping dependency locks and CI workflows healthy;
- approving releases and checking their provenance;
- deciding when hardware-in-the-loop validation is required;
- protecting the partition and private-data boundaries documented in
  `SECURITY.md` and `docs/FLASH-AND-RECOVERY.md`.

A public GitHub identity is sufficient for participation. Contributors are not
required to publish a legal name or private contact information.

## Decisions and contributions

Routine fixes are decided through public Issues and pull requests. Changes to
partition layout, boot behavior, firmware inputs, signing, or flashing require
an explicit risk assessment and relevant automated or hardware evidence.
Unresolved safety concerns take precedence over release schedules.

The maintainer may invite recurring contributors to help triage or review after
they demonstrate sound technical judgment and respect for the project's safety
and privacy boundaries. Write access is granted deliberately and can be removed
if those boundaries are violated.

## Releases

Releases must identify the source commit and build run, publish checksums and
build metadata, and clearly distinguish an unsigned pull-request candidate from
a signed release build or a hardware-validated historical baseline. GitHub's
automatic source archives must never be described as flashable firmware.

## Security and conduct

Security reports follow `SECURITY.md`. Community participation follows
`CODE_OF_CONDUCT.md`. Governance changes are reviewed like other repository
changes and recorded in Git history.
