# Authentication choices

The original requirement was a local **OpenAI Agents SDK** application. Lack of a valid API credential and authentication/network problems prevented a successful model run. This repository does not resolve that historical blocker.

| Runtime | Contract | Handoff choice |
|---|---|---|
| Python Agents SDK (`openai-agents`) | Your application owns the agent loop/tools; documented OpenAI setup uses a Platform API key | Implemented as an optional planning starter |
| Codex SDK (`@openai/codex-sdk`) | Programmatic local Codex tasks with the Codex runtime | Alternative to evaluate; not implemented here |
| Hosted Agents API | Managed remote agent runtime | Not the selected architecture |

A ChatGPT/Codex account is not itself the Platform API key expected by this starter. The original base-image name includes Codex SDK; that does not identify the Python Agents SDK or prove usable authentication.

Current official documentation, checked October 19, supports ChatGPT sign-in and API-key sign-in for Codex. It also describes Enterprise Codex access tokens for trusted non-interactive local workflows when administrators grant the relevant permission. That is an account-dependent Codex route, not proof of subscription authentication for a general Agents SDK application. It also does not prove the route was available or reachable during the original setup.

If subscription-funded automation is the priority, evaluate Codex SDK separately with the owner: exact workspace entitlement, supported unattended use, permitted tools, protected credential storage, token refresh/revocation, and required outbound destinations. Preserve the same artifact-only scope while doing that evaluation.

For this starter's live path, use a scoped Platform credential and an explicitly selected available model. Begin with the bundled synthetic request. Missing credentials produce `AWAITING_AUTH`. Network, model access and account billing remain prerequisites. Never substitute a browser cookie or a Codex OAuth token for `OPENAI_API_KEY`.

Sources:

- [Agents SDK quickstart](https://developers.openai.com/api/docs/guides/agents/quickstart)
- [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)
- [Codex authentication](https://learn.chatgpt.com/docs/auth)

These sources establish product distinctions, not this organization's permissions or firewall configuration. The original design's model name is retained in `.env.example` as configuration guidance, without an account-availability claim.
