# Validation report — Security Stage 3

- Added security checks: 33
- New directory: `checks/security/access-control/`
- Matrix: `docs/SECURITY_ACCESS_CONTROL_MATRIX.md`
- Profile selection policy: `docs/SECURITY_PROFILE_SELECTION.md`
- Taxonomy extended with: `ownership`, `tenant-isolation`, `roles-scopes`, `token-lifecycle`, `privilege-escalation`.

All new checks use the existing schema fields, category `security`, known kinds/priorities, existing profiles, and controlled tags. Validate locally with `python tools/validate_library.py .`.

Note: this is a template library. HTTP status assertions, denial-vs-concealment behavior, token revocation propagation windows, batch atomicity, and cross-tenant sharing must be set from the target API contract and security policy.
