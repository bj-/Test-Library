# Coverage analysis from real OpenAPI contracts

## Summary
- Operations inventoried: **35**
- Generated candidate checks: **48**
- Clarification items after deduplication: **66**
- Missing OpenAPI security declarations: **20**
- Explicit security contradictions: **1**

## Contracts

### Bff Admin API documentation
- Operations: 24
- Operations with security declared: 4
- Operations without security declared: 20
- Operations with anonymous alternative: 0

### API мобильного клиента
- Operations: 11
- Operations with security declared: 11
- Operations without security declared: 0
- Operations with anonymous alternative: 1

## High-priority findings

1. **Bff Admin API:** access is reviewed per operation. Operations without an OpenAPI `security` declaration remain unresolved individually; do not infer that they are public or protected until each operation is confirmed.
2. **Mobile API `onStart`:** `security` contains `{}` as an alternative, which permits anonymous access, while the description says a missing/invalid `api-key` returns 403.
3. **Mobile document endpoints:** security alternatives mean `Api-Key + Bearer` OR `Api-Key` only. Ownership/installation binding remains unconfirmed; do not treat installation ID as a proven isolation boundary.
4. **Role model and mobile isolation:** role model and region/installation isolation remain unknown by request; related checks are candidates blocked on owner clarification, not confirmed policy.

## Clarification queue

- **contract_security_gap** · `AuthController_login` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `AuthController_logout` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **needs_clarification** · `AuthController_changePassword` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **needs_clarification** · `AuthController_deleteSession` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `ComponentTypesController_getTypes` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ComponentTypesController_getTypes` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getScreens` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getScreens` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getCurrentVersions` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getCurrentVersions` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getVersions` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getVersions` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `LayoutsController_getVersions` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getScreen` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getScreen` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `LayoutsController_getScreen` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getNodes` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getNodes` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `LayoutsController_getNodes` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_getLanguages` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_getLanguages` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `LayoutsController_getLanguages` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `LayoutsController_toggleLanguage` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_toggleLanguage` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_toggleLanguage` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `LayoutsController_updateComponent` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_updateComponent` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_updateComponent` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `LayoutsController_saveTranslation` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_saveTranslation` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_saveTranslation` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `LayoutsController_validate` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_validate` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `LayoutsController_validate` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_validate` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `LayoutsController_publish` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_publish` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_publish` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `LayoutsController_archive` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `LayoutsController_archive` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `LayoutsController_archive` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `ContentController_getSources` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ContentController_getSources` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `ContentController_getItems` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ContentController_getItems` · Confirm whether resource ownership applies and how the principal/installation_id is bound to the resource.
- **needs_clarification** · `ContentController_getItems` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_security_gap** · `ContentController_createItem` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ContentController_createItem` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `ContentController_createItem` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `ContentController_updateItem` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ContentController_updateItem` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `ContentController_updateItem` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `ContentController_removeItem` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `ContentController_removeItem` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `ContentController_removeItem` · Role/permission model is unknown. Confirm whether roles/scopes exist and specify the minimum privilege, or explicitly document that any authenticated principal may perform this action.
- **contract_security_gap** · `AuditController_getEntries` · OpenAPI does not declare a security requirement. Confirm this endpoint is intentionally public or add the actual cookie/Bearer/API-key security requirement.
- **needs_clarification** · `AuditController_getEntries` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **contract_contradiction** · `onStart` · OpenAPI security includes an empty alternative {}, which permits anonymous access, while description says missing/invalid api-key returns 403. Confirm intended behavior and fix either security declaration or description.
- **needs_clarification** · `onStart` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **owner_confirmation_required** · `onStart` · API owner must resolve whether api-key is mandatory. OpenAPI permits anonymous access via security alternative {}, while the description says missing/invalid api-key returns 403. Keep the definitive expected result blocked until confirmed.
- **needs_clarification** · `getUnsignedDocuments` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `acceptDocuments` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `getDocumentsHistory` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `getOnboardingStory` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `getWidgetStories` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.
- **needs_clarification** · `getFaqStories` · Confirm whether regional/tenant isolation applies and identify the trusted tenant/region context. Do not assume installation_id or locale is a tenant boundary.

## Generated candidates

- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGIN-INVALID-CREDENTIALS` — Login rejects invalid credentials [Smoke, CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-MISSING-OR-INVALID-COOKI` — Cookie-authenticated endpoint rejects missing/invalid session [Smoke, CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-LOGOUT-ROLE-MODEL-UNRESOLVED` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-MISSING-OR-INVAL` — Cookie-authenticated endpoint rejects missing/invalid session [Smoke, CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-WRONG-CURRENT-PA` — Password change verifies current password [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-CHANGEPASSWORD-ROLE-MODEL-UNRES` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-MISSING-OR-INVALID` — Cookie-authenticated endpoint rejects missing/invalid session [Smoke, CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-GETSESSIONS-CROSS-ACCOUNT-SESSI` — Session endpoint enforces session ownership [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-MISSING-OR-INVALI` — Cookie-authenticated endpoint rejects missing/invalid session [Smoke, CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-CROSS-ACCOUNT-SES` — Session endpoint enforces session ownership [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUTHCONTROLLER-DELETESESSION-ROLE-MODEL-UNRESO` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-COMPONENTTYPESCONTROLLER-GETTYPES-OPERATION-AC` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREENS-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETCURRENTVERSIONS-OPERATION` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETVERSIONS-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETSCREEN-OPERATION-ACCESS-P` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETNODES-OPERATION-ACCESS-PO` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-GETLANGUAGES-OPERATION-ACCES` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-OPERATION-ACC` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-TOGGLELANGUAGE-ROLE-MODEL-UN` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-OPERATION-AC` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-UPDATECOMPONENT-ROLE-MODEL-U` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-OPERATION-AC` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-SAVETRANSLATION-ROLE-MODEL-U` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-OPERATION-ACCESS-PO` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-VALIDATE-ROLE-MODEL-UNRESOLV` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-OPERATION-ACCESS-POL` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-PUBLISH-ROLE-MODEL-UNRESOLVE` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-OPERATION-ACCESS-POL` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-LAYOUTSCONTROLLER-ARCHIVE-ROLE-MODEL-UNRESOLVE` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETSOURCES-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-GETITEMS-OPERATION-ACCESS-PO` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-CREATEITEM-ROLE-MODEL-UNRESO` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-UPDATEITEM-ROLE-MODEL-UNRESO` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-OPERATION-ACCESS` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-CONTENTCONTROLLER-REMOVEITEM-ROLE-MODEL-UNRESO` — Confirm minimum privilege policy for sensitive operation [CI, Regression, Release]
- `REAL-BFF-ADMIN-API-AUDITCONTROLLER-GETENTRIES-OPERATION-ACCESS-PO` — Confirm operation-specific authentication and authorization policy [CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-ONSTART-ANONYMOUS-VS-API-KEY` — Startup endpoint matches the documented API-key policy [CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-SENDCODE-INVALID-API-KEY` — Authentication endpoint rejects invalid credentials [Smoke, CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-VERIFYCODE-INVALID-API-KEY` — Authentication endpoint rejects invalid credentials [Smoke, CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-REFRESH-EXPIRED-OR-INVALID-REFRESH-TOKEN` — Authentication endpoint rejects invalid credentials [Smoke, CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-LOGOUT-MISSING-EXPIRED-OR-REFRESH-TOKEN` — Logout requires a valid access token [Smoke, CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-GETUNSIGNEDDOCUMENTS-GUEST-VS-AUTHENTICATE` — Guest and authenticated document access follow distinct policies [CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-GUEST-VS-AUTHENTICATED` — Guest and authenticated document access follow distinct policies [Smoke, CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-ACCEPTDOCUMENTS-CROSS-PRINCIPAL-OR-STALE-R` — Document acceptance is bound to the correct principal and revision [CI, Regression, Release]
- `REAL-MOBILE-CLIENT-API-GETDOCUMENTSHISTORY-GUEST-VS-AUTHENTICATED` — Guest and authenticated document access follow distinct policies [CI, Regression, Release]

## Interpretation

Generated checks are reviewable candidates, not executed tests. A `needs_clarification` item is a blocker for a definitive expected result. Coverage counts are generated candidates, not runtime pass coverage.
