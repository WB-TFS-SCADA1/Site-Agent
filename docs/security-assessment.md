# Security assessment summary

The October 13 assessment tested a bounded set of operations from the supplied worker account. **No escape or privilege escalation was demonstrated.** This is evidence about those tests, not proof against kernel/runtime vulnerabilities or all possible escape paths.

| Finding | Observed result | Remaining work |
|---|---|---|
| SSH service identity | Workload UID could read/write the active worker host private key by ownership/access checks | Separate SSH service and workload identities/storage; then rotate the host key |
| Group membership | Workload UID 1000 had primary/supplementary GID 0 | Use a dedicated GID and explicit reference-data permissions |
| Privilege and namespaces | Zero capability masks, no-new-privileges, seccomp; tested elevation and namespace calls denied | Preserve restrictions and verify after changes |
| Filesystem/process exposure | Tested roots stayed inside the worker; no checked control socket or dangerous device found | Review every mount and permitted input manifest |
| AppArmor | Visible label was `rootlesskit (unconfined)` | Verify enforcing workload and enclosing LXD policies |
| Network | Bounded connectivity tests did not establish full egress policy | Document/enforce destinations and verify positive/negative canaries |
| Resources | 0.5 CPU, 512 MiB, no extra swap, 128 PIDs configured | Add durable byte/inode quotas and review I/O and per-process limits |

No private key contents were read or used in the assessment. The key finding concerns the worker's service identity; it does not demonstrate exposure of Warpgate credentials or host access.

The initial deployment verification additionally reported a read-only root, read-only reference mounts, no sudo or orchestration socket, and source-restricted SSH ingress. The independent assessment had less visibility into enclosing systems; preserve that difference in evidence scope.

The original setup documentation says persistent storage has no per-worker quota and public HTTP/HTTPS egress is allowed alongside infrastructure DNS/DHCP while private destinations are blocked. The independent assessment did not establish every one of those network rules. Neither record is a current firewall audit.

The [findings extract](reference/isolation-findings-20261013.txt) retains the assessment's reasoning and evidence IDs. Raw commands and outputs remain in the original private workspace. No fixes are claimed by importing these findings into Git.
