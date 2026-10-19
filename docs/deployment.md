# Deployment and recovery

The included host/worker files describe the October 13 installation. They have not been hardened or redeployed for this repository. Use this guide to recover the design and prepare a reviewed installation; it is not a clean-host installer.

## Required dependencies

1. An IGN04 administrator with the ability to manage the existing unprivileged `site-agent-jail` LXD container.
2. Rootless Docker for `siteagent`, with the user service and linger configured.
3. The existing `site-agent-base:codex-sdk-0.156.1` image, or a separately reconstructed and validated replacement. Its original build recipe/digest is unavailable here.
4. The read-only `ignProjects` checkout and private input directory expected by Compose.
5. The Warpgate target-side public key in a local `worker/authorized_keys` file. Obtain it through the administrator; no private key belongs here.
6. A reviewed host firewall rule and LXD TCP proxy for the recorded ingress path.
7. Independently verified SSH host trust and scoped Warpgate user access.

See [dependencies](dependencies.md) for the missing sources and exact limits of reproducibility.

## Build and launch outline

Perform these steps only in the selected rootless Docker environment after reviewing the security findings and mounts. The original deployed directory was `/opt/site-agent/ssh-worker-20261013` inside the jail. The local repository's `worker/` directory contains its equivalent files.

```sh
cd worker
docker image inspect site-agent-base:codex-sdk-0.156.1
docker build -t site-agent-worker:ssh-20261013 .
docker compose config
docker compose up -d --no-build
```

Compose intentionally has no automatic image pull or build configuration. It uses a prebuilt image and external read-only input paths. Running the commands against a different Docker daemon changes the deployment location; verify the selected daemon before use. Existing named volumes are part of the persistent state and must not be removed as a routine rebuild step.

## Host components

Install the reviewed `host/ingress.nft` at `/etc/site-agent-worker/ingress.nft`, its unit under `/etc/systemd/system/`, and the LXD dependency as `/etc/systemd/system/snap.lxd.daemon.service.d/site-agent-worker-ingress.conf`. The original unit was enabled before exposing the worker route. Confirm the source guard before enabling the proxy/listener.

The existing proxy named `worker-ssh` forwards the host endpoint to jail loopback. Its full LXD device definition was not captured in the portable source set; recover and review it rather than guessing the `lxc config device add` arguments.

The drop-in makes LXD require the firewall guard. A guard failure can prevent LXD from starting, affecting more than this worker. This coupling remains a hardening/recovery review item.

## Acceptance after any deployment change

Verify scoped Warpgate login, correct UID/GID and hostname, command working directory, SFTP round trip, allowed/denied ingress counters, read-only root and inputs, absent management sockets, configured limits, and persistence across recreation of only the worker. Retest key separation after implementing its fix. Host/jail reboot acceptance remains outstanding.

Native Ignition validation requires its own proven OS-isolated lab and sufficient resources. The presence of Java, bubblewrap or Xvfb in an image does not establish that the lab works or is safely isolated.
