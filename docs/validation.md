# Repository validation

Checked October 19, 2026 in a temporary Linux/WSL environment using Python 3.10.12. This is repository verification, not a current server assessment.

| Check | Result |
|---|---|
| Dependency-free unittest suite | 11 passed; 2 optional SDK tests skipped without the SDK |
| Installed-SDK unittest suite | All 13 passed with `openai-agents==0.24.0` |
| SDK tool round trip | Actual SDK with fake model invoked the capability tool and parsed structured advice; no network |
| Complete synthetic CLI request | `BLOCKED_NOT_IMPLEMENTED`; no artifacts or production actions |
| Missing-input CLI request | `NEEDS_INPUT`; missing facts retained |
| Live CLI without credential | Exit 2 and `AWAITING_AUTH`; no model call |
| Error handling | Provider exception detail/credential absent from persisted failure report |
| Source preservation | Imported hashes checked against `source-manifest.json` |
| Repository content check | Python/JSON syntax, local Markdown links, forbidden file types and selected credential patterns passed |
| Configuration syntax | Compose and CI YAML parsed locally; worker entrypoint passed `bash -n` |

The initial sync capability wrapper caused the local SDK test to hang during executor shutdown. The final SDK wrapper is an async function for this immediate, nonblocking lookup; the final suite completed normally. Temporary diagnostic processes were bounded/stopped.

Not performed: paid/live model request, account/model entitlement verification, native Windows installation, GitHub Actions execution, container image build, LXD/host configuration changes, live Warpgate client retest, reboot acceptance, native Ignition execution, actual source transformation, or field commissioning.

The original worker image build cannot be reproduced from this repository alone until its base-image recipe or reviewed replacement is recovered. See [dependencies](dependencies.md).

To repeat the checks, follow the root README and install the optional SDK snapshot only for the SDK contract tests. The content checker is deliberately bounded and does not replace review of future changes and outgoing Git history.
