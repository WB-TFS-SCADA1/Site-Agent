# Publishing to WB-TFS-SCADA1

The local repository is prepared for the organization at `https://github.com/WB-TFS-SCADA1`. That URL identifies the organization, not a specific Git remote. No remote is configured until a repository name is chosen.

The initial branch is `main`. Create an empty repository in the organization (for example `Site-Agent`), then from PowerShell:

```powershell
cd C:\Users\William.Mock\Site-Agent
git status
git log -1 --oneline
git remote add origin https://github.com/WB-TFS-SCADA1/Site-Agent.git
git push -u origin main
```

Use the actual repository URL if a different name is chosen. Start with an empty remote without another README/initial commit; otherwise reconcile the two histories intentionally. The commands above are instructions for the owner, not evidence that anything has been uploaded.

The initial commit uses `Codex <codex@local.invalid>` as the automation author because the WSL Git environment had no configured user identity. Future commits can use your normal Git identity; no global identity is changed by this handoff.

This repository contains internal infrastructure topology and design details. Select organization visibility consistent with that content. No open-source license has been assigned; the organization can choose licensing and CODEOWNERS separately.

Run `python tools/check_repo.py` and review staged changes before publishing. `.gitignore` excludes common credential files, private backups, job outputs and runtime state. The content check is a bounded pattern/file-policy check, not a guarantee that arbitrary future documents cannot contain secrets.

The included workflow runs offline tests only. It has no OpenAI key, Warpgate secret, production environment, notification action or deployment step. GitHub execution itself remains unverified until the owner pushes it.
