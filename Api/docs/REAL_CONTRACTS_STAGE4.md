# Stage 4 — analysis of real contracts

Input contracts are preserved in `examples/real-contracts/`. Access models in the same folder are deliberately conservative. Admin endpoints lacking security are marked for per-operation review; role model and mobile isolation remain unknown; POST /onStart is blocked on API-owner confirmation.

Run the generator prototype against synthetic/demo inputs as before; for the supplied real contracts, review `build/real-contract-coverage/REAL_CONTRACT_COVERAGE_REPORT.md`, `operation_inventory.json`, `clarification_questions.json`, and generated candidates under `checks/generated/real-contracts/`.

The generated candidates are schema-shaped YAML records and should be reviewed before execution. They are not evidence of runtime behavior.
