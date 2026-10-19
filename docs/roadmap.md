# Implementation roadmap

The first milestone is reproducible local artifact preparation and human import. Production automation remains later work.

| Milestone | Required outcome |
|---|---|
| Repository handoff | Preserve deployment sources, known findings, design and runnable offline starter |
| Recover build dependencies | Identify/rebuild the base image; pin ignProjects and required native dependencies |
| Harden and reverify workspace | Resolve key/identity/storage/confinement findings and record live acceptance |
| Resolve model access | Owner-approved API credential/model and tested network path; synthetic authenticated SDK run |
| Connect controlled build tools | Typed coordinator adapters for selected-source acquisition and private-copy transformation |
| Validate artifacts | Static checks plus exact-final-file native lab evidence; no model assertions as proof |
| Deliver pilot bundle | Authenticated request/review/download, source/output hashes and manual import instructions |
| Later commissioning | Separately reviewed IPC bootstrap, installation, licensing, metadata and other production adapters |

The larger design requires durable jobs, idempotency, ownership, authenticated initiation and restart/replay handling. The starter's JSON reports are not a substitute for those services.

Before enabling live tool execution, write tests for rejected scope, wrong donor/target, missing/ambiguous fields, invalid native evidence, credential leakage, cancelled jobs and resumed operations. Integrate existing validators rather than treating a model's explanation as validation.

The organization's `ign04-container-deploy` framework may eventually provide deployment controls. Evaluate it through its reviewed interface; do not assume this historical SSH worker fits its application catalog or image policy without changes.
