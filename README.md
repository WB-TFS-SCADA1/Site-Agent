# Site-Agent

Infrastructure and an OpenAI Agents SDK starter for preparing Ignition site commissioning artifacts.

The remote workspace was deployed and assessed on **October 13, 2026**. This repository was assembled on **October 19, 2026**. The agent starter runs offline and has an optional live planning path. **It does not yet build Ignition artifacts or commission a site.** No live server was revalidated while preparing this repository.

The intended first product is a validated Edge backup, focused project ZIP, and review evidence for a human to import. Later production automation is described in the historical design, but has not been implemented here.

## What is included

| Directory | Purpose | Status |
|---|---|---|
| `worker/` | Dockerfile, Compose, SSH settings, startup script | Exact October 13 source; known hardening findings remain |
| `host/` | Dedicated SSH ingress firewall and systemd ordering | Exact October 13 source; specific to IGN04 |
| `client/` | Operator command/file-transfer client through Warpgate | Ported with configurable user and endpoint settings |
| `agent/` | Request schema, offline report, optional Agents SDK planner | New starter; no production adapters |
| `docs/` | Architecture, deployment, operations, security, authentication and roadmap | Current handoff plus historical references |
| `tools/` | Portable content and provenance checks | Local checks; no external connections |

## Try the offline starter

Python 3.10 or later is sufficient. No dependencies, account, credentials or network access are needed.

From PowerShell at the repository root:

```powershell
$env:PYTHONPATH = "$PWD\agent\src"
New-Item -ItemType Directory -Force outputs | Out-Null
python -m site_agent --request agent/examples/site-request.json --output outputs/example-plan.json
python -W error -m unittest discover -s agent/tests -v
python tools/check_repo.py
```

From Bash/WSL:

```sh
export PYTHONPATH="$PWD/agent/src"
mkdir -p outputs
python3 -m site_agent --request agent/examples/site-request.json --output outputs/example-plan.json
python3 -W error -m unittest discover -s agent/tests -v
python3 tools/check_repo.py
```

The example prints `BLOCKED_NOT_IMPLEMENTED` and writes an honest planning report with no deliverables. Use a new output filename for each run. Exit code zero means report generation succeeded; it never means commissioning succeeded. The SDK contract tests skip when optional dependencies are absent.

See [the agent guide](agent/README.md) for live mode, dependency installation and output semantics.

## Start reading here

- [Current status and verification](docs/status.md)
- [Architecture](docs/architecture.md)
- [Deployment prerequisites and recovery](docs/deployment.md)
- [Operations and Warpgate client](docs/operations.md)
- [Authentication choices](docs/authentication.md)
- [Security findings](docs/security-assessment.md) and [hardening backlog](docs/hardening-plan.md)
- [External dependencies and missing base image](docs/dependencies.md)
- [Implementation roadmap](docs/roadmap.md)
- [Comparison with the organization's smoke fixture](docs/smoke-fixture-reference.md)
- [Publishing to the organization](docs/publishing.md)

The full [September 23 commissioning design](docs/reference/commissioning-design-20260923.md) records the larger intended system. Its chroot/service and production-adapter proposals are not evidence that those components exist in the October 13 Docker/LXD deployment.

## Repository scope

This is an internal infrastructure handoff and contains internal host names, addresses, identifiers and historical design context. It contains no supplied credentials, private keys, raw connection transcripts, site backups, vendor runtimes or generated releases. Keep private inputs and results in ignored directories.

The original worker image depends on a local base image whose build recipe was not available. This repo therefore does not yet recreate the entire deployed environment from a clean host. The dependency inventory identifies what must be recovered.

CI runs offline checks only. The repository has no deployment workflow, remote connection workflow, notification integration or production credentials.
