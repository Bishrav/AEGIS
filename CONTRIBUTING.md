# Contributing to AEGIS

## Branches

- `main` is always expected to be releasable.
- Use focused branches such as `feat/normalization-service` or `fix/event-deduplication`.
- Keep one architectural concern per pull request.

## Pull requests

Every pull request should include:

- Problem and scope.
- Architecture or schema impact.
- Tests and commands run.
- Screenshots, traces, benchmark output, or model metrics when relevant.
- Documentation and ADR updates when behavior or design changes.

## Commit style

Use Conventional Commits, for example:

```text
feat(ingestion): add hydrology source adapter
test(schema): cover event.v1 validation failures
docs(architecture): record provider adapter decision
```

