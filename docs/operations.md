# Operations

## Connect using the operator client

Install `client/requirements.txt` in a separate virtual environment. The ported client requires `--username` or `WARPGATE_USERNAME` instead of a hard-coded personal account. It also supports `--origin`, `--target`, `--ssh-port` and `--known-hosts`. The defaults retain the historical Warpgate origin and target.

Supply the Warpgate API token using the hidden prompt, `--token-file`, or `WARPGATE_API_TOKEN`. Keep token files outside Git and restrict their permissions. Server trust must already exist in known_hosts or the supplied verified file; the client rejects unknown host keys.

```sh
python client/worker_client.py --username YOUR_AUTHORIZED_USERNAME --command 'id; pwd; hostname'
python client/worker_client.py --username YOUR_AUTHORIZED_USERNAME --upload ./input.zip /workspace/work/input.zip
python client/worker_client.py --username YOUR_AUTHORIZED_USERNAME --download /workspace/work/result.zip ./result.zip
```

The client creates a 30-minute, single-use ticket and revokes it after the connection. Commands begin in `/workspace/work`. Direct interactive SSH normally starts in `/home/agent`. The API contract is the one used in the original deployment; compatibility with other Warpgate versions is not established.

Transfer paths must lexically fall under `/workspace/work` or `/home/agent`; this check is not a symlink-confinement boundary. The operator already has shell access. Host mounts, permissions and network policy provide the isolation.

The operator client changes in this repository were checked locally, not retested through Warpgate. Ticket expiry/revocation and a local command timeout are **not proven to terminate a remote background job**.

## Restart behavior

The original setup enabled LXD jail autostart, `siteagent` linger, the rootless Docker service, and worker restart policy `unless-stopped`. No whole-host reboot was tested.

After a normal restart, obtain a fresh ticket. If the jail was manually stopped, an administrator can start `site-agent-jail`, allow rootless Docker to initialize, and run Compose in the recorded deployment directory using the correct user/daemon. The original command details are retained in the historical handoff.

If LXD fails after a reboot, inspect `site-agent-worker-ingress.service` because the dependency is required. Avoid resetting unrelated host firewall rules or restarting Ignition as a worker-recovery step.

## Data and cleanup

Persistent home/work volumes survive worker replacement. Copy only selected inputs into writable staging and preserve originals. Raw project backups can contain credentials and stay out of this repository. Use per-job cleanup with recorded ownership; do not use `docker compose down -v` as normal cleanup.

The existing log driver rotates three 10 MiB files. Persistent storage has no verified per-worker quota. Log rotation does not address volume exhaustion.
