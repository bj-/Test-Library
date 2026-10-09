# REST expansion compatibility pass

The 57 REST expansion checks were adapted to the current API Test Library schema and validator.

- Each file now uses the required top-level `checks` list.
- Each `steps` item is represented as `{action: ...}` to match `check.schema.json`.
- The expansion-only `status: draft` field was removed because the current schema disallows additional properties. Draft status is documented here rather than encoded in the check object.
- Categories and tags not present in the current taxonomy were mapped to the closest existing allowed values; review these semantic mappings before treating them as final taxonomy decisions.
- Profile names were preserved and checked against the existing profile filenames/IDs.

All converted checks remain templates and must be adapted to the target API/OpenAPI contract before execution.
