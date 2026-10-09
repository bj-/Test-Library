# API access-control coverage report

- API: **Sample Tenant API**
- OpenAPI: `3.0.3`
- Operations discovered: **3**
- Generated candidates: **17**
- Requirements needing clarification: **0**
- Contradictions: **0**

## Candidate coverage by dimension

| Dimension | Candidate cells |
|---|---:|
| authentication | 6 |
| authorization | 3 |
| resource_ownership | 2 |
| tenant_isolation | 3 |
| roles_scopes | 3 |

## Candidate checks by risk priority

| Priority | Count |
|---|---:|
| P0 | 3 |
| P1 | 14 |
| P2 | 0 |
| P3 | 0 |

## Profile selection counts

| Profile | Checks selected by metadata |
|---|---:|
| Smoke | 11 |
| CI | 17 |
| Regression | 17 |
| Release | 17 |
| PR | 0 |
| Nightly | 0 |

## Questions and contradictions

No clarification questions detected by the current rules.

## Interpretation

These are generated candidate cells, not verified runtime coverage. Confirm each policy, expected status/body, test fixture, and operation-specific exception before execution.
