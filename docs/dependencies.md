# External dependencies and provenance

## Missing base image and enclosing setup

`worker/Dockerfile` starts from `site-agent-base:codex-sdk-0.156.1`. The original image exists according to the October 13 deployment record, but its Dockerfile, immutable image digest and original dependency lock were not present in the supplied worker source directory. No substitute image was invented for this port.

Recover its recipe/digest from the original builder, or build and validate a new base as a separate change. The existing worker recipe assumes an `agent` account and `/usr/bin/tini` already exist. It installs additional tools but does not create the entire base.

LXD installation, storage-pool setup, rootless Docker installation, the full jail profile/device configuration and Warpgate target creation are also external prerequisites. The repository captures the dedicated worker, guard and client, not an entire host configuration backup.

## ignProjects toolchain

The original read-only mount points at `/opt/site-agent/ignProjects`. The local source checkout observed during this handoff was at commit `3728ab348fce36ba42ea144fc265bdec91c4caf6`; that does not prove the deployed mount is at the same revision or that the working tree exactly matches the commit.

The relevant external files are:

- `ignProjects/README.md` and `ignProjects/AGENTS.md`
- `ignProjects/docs/site-cloning.md`
- `ignProjects/docs/gateway-backup-workflow.md`
- `ignProjects/docs/publishing-verification.md`
- `ignProjects/docs/database/site-equipment.md`
- `ignProjects/docs/database/catalog/ignitiondb-20260906T175452Z.md`
- `ignProjects/tools/ignition_site.py` and `ignition_site_release.py`
- `ignProjects/tools/examples/booster-site-spec.example.json`

This is an existing substantial toolchain with source/version-specific profiles, dependencies and tests. Copying a couple of entry-point scripts would not make it portable. It has therefore not been partially vendored or silently assigned an invented Git remote. Obtain a reviewed source distribution/checkout and exact reference from its owner before integrating it.

The documented original profile is tied to a supplied Ignition Edge 8.1.39 backup and exact module/source artifacts. It is not a general arbitrary-donor commissioning engine. Private backups, selected immutable resources, vendor distributions and native acceptance evidence remain separate inputs.

Production exchange remains manual for that toolchain. Native checks require disposable OS isolation with no external routes. Its database restrictions and full resource-assembly requirements remain applicable when integrating it.

## Historical design references

The imported full design also referenced `SCADA_Notes_Report.md` and `docs/linux-ignition-edge-zip-upgrade.md` in the original workspace. Those broader internal operational documents and schema snapshots are not copied into this infrastructure repository. Relative links in the historical design point here and retain their original source path inline.

The design includes proposed operations, future service identities, example values and a production roadmap. The deployed worker and new starter implement only the pieces listed in [status](status.md).

## Preserved and adapted files

`source-manifest.json` records source-relative filenames, original hashes, destination hashes and transformations. Worker/host files are preserved byte-for-byte. The client removes the hard-coded personal username, accepts explicit connection settings, validates transfer paths before connecting, and suppresses potentially sensitive exception details. The full design has an added status banner and repaired dependency links. The assessment is a findings-only extract.

The original hardening manifest refers to filenames in its original flat source directory. Those historical hashes remain evidence of that capture, not a manifest of this repository's layout.
