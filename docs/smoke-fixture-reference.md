# Relationship to ign04-smoke-fixture

The owner supplied a local clone of [WB-TFS-SCADA1/ign04-smoke-fixture](https://github.com/WB-TFS-SCADA1/ign04-smoke-fixture). The reviewed local commit was `b200c4b5d6199303d49207a35fd88e5b1ec372d9` on October 19, 2026.

That fixture tests the organization's shared container deployment controls using a harmless program. Importing its module does no work; explicit execution requires UID:GID 10001:10001 and writes one fixed message to `/data/smoke.txt`. Its ordinary CI tests do not deploy anything.

Site-Agent follows these useful conventions:

- Import-safe application modules and explicit execution.
- A dependency-free unittest suite.
- Test-only GitHub Actions with read-only contents permission and checkout credentials disabled.
- The same pinned checkout/setup-python action revisions observed in that fixture.
- Explicit separation between tests, connection checks and deployment authorization.

The smoke fixture's manual connection-check workflow calls `ign04-container-deploy` at reviewed revision `ab5ce7bf385bc0da80f9847feb1f864ce6e041fa`. Its protected environment, catalog identity, scoped secrets, image approval lock and cooldown are specific to that deployment system.

Those connection/notification workflows, secrets, CODEOWNERS and host policies have **not** been copied or activated here. The fixture README says its catalog entry remains disabled and the connection test expects rejection. Passing its smoke tests would not validate Site-Agent or authorize commissioning.

The historical Site-Agent worker uses UID 1000/GID 0 and a different SSH-worker lifecycle. It is not a drop-in application for the fixture's UID 10001 deployment contract. The SDK dependency snapshot here is a development snapshot, not approval under that framework's fourteen-day dependency/image policies.

No fixture source code was copied into the application. Workflow action pins and the testing approach were reused as organization conventions; the starter and tests are new.
