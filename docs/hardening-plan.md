# Hardening backlog

The latest hardening artifact is a local baseline captured on October 13 at 18:25 UTC. It says `live_changes: false` and that live state was not revalidated. All items below remain open until new deployment-specific evidence exists.

1. **Separate SSH ingress from workload identity.** Move service keys out of workload reach, use distinct identities and storage, and test denied access from the workload. Rotate the worker host key after correcting the boundary and coordinate trust changes with Warpgate.
2. **Remove GID 0.** Assign a dedicated workload group; provide only the required read access to selected references. Verify file ownership and runtime behavior after migration.
3. **Enforce confinement.** Review the worker AppArmor policy and enclosing LXD settings while preserving capabilities, seccomp and no-new-privileges restrictions. Re-run the bounded namespace and elevation checks.
4. **Bound persistent storage.** Establish byte/inode quotas, retention and I/O policy. Keep existing log bounds. Do not test saturation on the shared production host.
5. **Define egress.** Separate model/authentication destinations from general public access. Enforce outside model-controlled processes and verify intended routes with approved canaries.
6. **Review exposed references and credentials.** Provide per-job selected inputs, document their contents, and keep service credentials outside model-callable file/shell access.
7. **Prove lifecycle behavior.** Verify worker/job cancellation independently of SSH ticket expiry, cleanup/recovery, and startup after an approved reboot. Review the broad LXD dependency on the worker firewall guard.
8. **Validate native lab feasibility.** Measure resources and prove OS isolation for the exact Ignition toolchain before enabling real build adapters. Use a separate VM if required by the workload/boundary requirements.

Track these as separate repository issues when the GitHub repository exists. This file supplies the initial backlog without claiming issue IDs or deployed fixes.
