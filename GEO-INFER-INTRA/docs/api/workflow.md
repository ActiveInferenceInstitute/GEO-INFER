# Workflow API

## Implementation status

The workflow package under `GEO-INFER-INTRA/src/geo_infer_intra/core/workflow/`
currently contains only its package marker (`__init__.py`). It does not expose a
workflow service, REST server, client library, persistence layer, or CLI.

Consequently, the REST endpoints and JavaScript client examples that were
previously documented on this page were proposals rather than supported API.
They have been removed to avoid presenting an unimplemented interface as
available functionality.

## Current workflow guidance

Use the workflow pages as conceptual guidance for composing existing GEO-INFER
modules and scripts:

- [Workflow patterns](../workflows/index.md)
- [Active inference workflows](../workflows/active_inference_workflows.md)
- [Architecture overview](../architecture/overview.md)
- [Examples directory](../../../GEO-INFER-EXAMPLES/README.md)

For a runnable integration, start with an example under
`GEO-INFER-EXAMPLES/examples/` or a module-specific example and verify it with
the repository's test and validation commands.

## Planned API work

If a workflow service becomes an implementation priority, the API should be
specified and implemented together: resource schemas, authentication,
execution semantics, persistence, error responses, and a tested client. Until
those pieces exist in this repository, they remain open design work rather
than public API contracts.
