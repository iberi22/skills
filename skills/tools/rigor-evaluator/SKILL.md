---
name: rigor-evaluator
description: Use when you need a quick heuristic rigor score (10 criteria, 0-2 each) for the features in a .gitcore/features.json file, to decide which features are ready to ship.
license: MIT
---

# rigor-evaluator

Node CLI that scores every feature in a `features.json` against 10 rigor
criteria (0-2 each, max 20) and writes a JSON report.

## Criteria

1. Completitud SRS (IEEE 830 sections)
2. Contrato de datos (types, endpoints)
3. Acceptance criteria (happy, edge, error)
4. Escenarios de falla
5. Trazabilidad (requirements to code/tests)
6. Dependencias mesh
7. Cobertura de permisos (**hard: must be 2**)
8. Modelo de amenaza (**hard: must be 2**)
9. Offline/particion
10. Cobertura de tests

## PASS rule

A feature passes when all hold:

- total >= 14 of 20
- criterion 7 = 2 and criterion 8 = 2
- no criterion scores 0

## Invocation

```sh
node scripts/rigor-eval.js
node scripts/rigor-eval.js --features ./.gitcore/features.json --output ./rigor-report.json
node scripts/rigor-eval.js --help
```

Flags (only these exist):

- `--features <path>`: input. Default `.gitcore/features.json`, relative to the cwd.
- `--output <path>`: report. Default `rigor-report.json`, relative to the cwd.
- `--help`, `-h`: print usage and exit 0 (read-only).

Exits 1 if the input file is missing, is not valid JSON, or has no `features` array.

## Input

A JSON object with a `features` array. Fields read per feature: `id`, `name`,
`module`, `stage`, `status`, `maturity`, `implementation_percentage`, `gaps[]`,
`dependencies[]`. Optional top-level `protocol` is echoed to stdout.

## Output

Writes JSON with `schema_version`, `generated_at`, `summary` (features passed/failed,
pass rate, overall score), `pass_conditions`, `criteria_definitions`, and `features[]`.
Each feature entry has `total_score`, `passed`, `errors[]`, and per-criterion `criteria[]`.

Stdout prints one line per feature (`Score: x/20 | PASS: SI|NO`) and a global summary.

## Limits

- Scores are **heuristics** derived from metadata fields (stage, module, percentage,
  gap text, dependency count, and feature id prefix). It does not read SRS documents,
  contracts, or test files, so it cannot verify them.
- Some rules are hard-coded to specific ids (`RF-001`, `RF-002`, `RF-004`, `RF-005`)
  and to module names (`authz`, `governance`, `identity`, `protocol`, `sync`,
  `presence`, `mesh`, `tests`). Features with other naming get the generic branch.
- A feature with `stage` `specced` and an `RF-` id receives fixed scores. Treat
  the output as a triage signal, not an audit.
- Overwrites the output file without asking.
