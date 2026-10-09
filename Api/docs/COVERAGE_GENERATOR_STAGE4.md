# Stage 4 — OpenAPI access-control coverage generator

## Purpose

`tools/generate_coverage.py` reads an OpenAPI 3.x document and an access-model YAML file. It emits candidate checks, a dimension-by-operation matrix, a machine-readable report, and a human-readable report. It never calls the target API.

## Requirements

- Python 3.10+
- `PyYAML` (`pip install pyyaml`)

## Run

```bash
python tools/generate_coverage.py \
  --openapi examples/openapi.sample.yaml \
  --access-model examples/access-model.sample.yaml \
  --out build/coverage
```

PowerShell:

```powershell
python tools/generate_coverage.py `
  --openapi examples/openapi.sample.yaml `
  --access-model examples/access-model.sample.yaml `
  --out build/coverage
```

Outputs:

- `generated_checks/*.yaml` — candidate checks using the library's check shape;
- `coverage_matrix.json` — operation/dimension/case mapping;
- `coverage_report.json` — summary, questions, contradictions, and matrix;
- `coverage_report.md` — review-friendly report.

## Access model in OpenAPI

Use the operation-level `x-access-control` extension:

```yaml
x-access-control:
  resource: project
  ownership: required          # required | not_applicable | unknown
  tenant_isolation: required   # required | not_applicable | unknown
  roles: [project-admin]
  scopes: [projects:write]
  action: update
```

OpenAPI `security` / `components.securitySchemes` is used as the authentication signal. Operation-level `security: []` overrides global security and indicates no OpenAPI security requirement. For public operations, document the intent explicitly with `x-access-control.public: true` where needed.

## Rules and safety boundaries

1. **No silent policy invention.** Unknown ownership, tenant isolation, or roles/scopes creates a clarification item.
2. **Applicability is not execution.** A generated candidate is not evidence that a test ran or passed.
3. **Risk weighting.** Cross-tenant access is P0 by default; authn/authz/ownership and insufficient roles/scopes are P1. Adjust through reviewed policy if the actual threat model warrants it.
4. **Profiles.** Deterministic P0/P1 candidates target CI, Regression, and Release. Critical access boundaries may also target Smoke. Lower-priority or broader candidates target Regression/Nightly. Final inclusion must be reconciled with the repository's existing profile selector and tag semantics.
5. **Expected status is contract-specific.** 401/403/404 are not hard-coded as universal expected responses in generated steps; set exact response assertions based on API contract and anti-enumeration policy.
6. **Safe test data.** Use isolated test tenants and synthetic accounts only. Generator never sends requests.

## Current limitations

- Supports OpenAPI 3.x YAML/JSON and direct operation objects; local `#/components/...` refs are resolved for operation objects only.
- `x-access-control` is a project convention, not a standard OpenAPI field.
- Role inheritance, ABAC/ReBAC expressions, token revocation propagation windows, and resource graph semantics require explicit modeling or extension.
- Generated IDs are deterministic; check for collisions when merging output with manually authored checks.
- Profile assignments are emitted as metadata; run through the repository's selector/validator before adopting.

## Recommended CI pipeline

1. Lint OpenAPI.
2. Run generator and fail on contradictions or unresolved P0 policy questions (once thresholds are configured).
3. Validate generated YAML against `schema/check.schema.json` and taxonomy.
4. Compute coverage deltas versus the prior report.
5. Review new or removed cells and approve policy changes.
6. Execute selected checks only in a controlled test environment.
