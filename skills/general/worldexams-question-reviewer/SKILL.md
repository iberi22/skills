---
name: worldexams-question-reviewer
description: Review and validate WorldExams question bundles. Detects errors, scores quality, and applies regeneration policy. Report-only; never edits or commits bundles or generator prompts.
---

# WorldExams Question Reviewer

Automatic bundle review. Each batch runs as a sub-agent that applies the full validation protocol.

The reviewer only reports. It never edits generator prompts or bundles, and it never commits. The author of a bundle and its reviewer must be different parties.

## Trigger

This skill runs when:
- The cron job `worldexams-bundle-review` starts a review sub-agent.
- Someone asks manually: `Review bundle [ID]`.
- A bulk audit is requested: `Review all bundles for [country]`.

## Review workflow

### PHASE 1: Bundle discovery

1. Identify the bundle path.
2. Read the frontmatter for metadata:
   - `id`, `country`, `grade`, `subject`, `topic`, `period`
   - `bundle_size`, `protocol_version`

### PHASE 2: Structural validation

Run the checks in order:

1. **Valid frontmatter**
   - All required fields present.
   - ID format: `CO-[AREA]-[GRADE]-P[N]-[TOPIC]-[###]-MASTERY`.
   - `bundle_size` matches the number of questions in the file.

2. **Question structure**
   - Each question has: ID, Bloom level, ICFES tag, Expected_Success, stem, 4 options, 1 correct answer, feedback, explanation.
   - Consistent format across questions.

3. **Unique IDs**
   - No duplicate IDs.
   - No repeated question IDs within the same bundle.

### PHASE 3: Content validation (per question)

Apply this checklist to each question:

```
PER-QUESTION CHECKLIST:
□ Is the stem clear and unambiguous?
□ Is the context useful (not decorative)?
□ Are the 4 options homogeneous in category and register?
□ Is there exactly one correct answer?
□ Are the distractors plausible (they represent real errors)?
□ No "all of the above" / "none of the above"?
□ No grammatical clues (the correct option stands out by form)?
□ Is the explanation pedagogically correct?
□ Is there useful feedback per option?
□ Is the language appropriate for the grade?
□ Free of word salad?
□ Free of pseudo-technical jargon?
□ Free of grandiose jargon with no function?
□ Free of words repeated artificially?
□ Free of unnecessary morbid or sensationalist context?
```

### PHASE 4: Psychometric validation

1. **Progressive difficulty**: early questions are easier (recognition), later ones harder (evaluation/transfer).
2. **Discrimination**: distractors represent different, plausible errors.
3. **Expected success rate**: compare `expected_success_rate` in the frontmatter with each question's `Expected_Success` field.

### PHASE 5: Decision

| Condition | Decision |
|-----------|----------|
| 0 errors | ✅ `ACEPTAR`: bundle ready for production |
| 1 error | ⚠️ `CORREGIR_PUNTUAL`: regenerate that specific question |
| 2+ errors | 🔴 `REGENERAR_BUNDLE`: regenerate the whole bundle |
| Systematic errors (critical pattern) | 🔴 `REGENERAR_BUNDLE` + flag `CONTAMINATION` |

## Regeneration rules

**Regenerate the whole bundle if:**
- 2+ questions carry `[CRITICAL FAILURE]`.
- 2+ questions have an ambiguous or non-unique key.
- A systematic pattern of absurd distractors appears.
- Broad curricular misalignment.
- Inconsistent bundle structure.

**Fix a single question if:**
- 1 question has a local error (stem, option, or feedback).
- Frontmatter format error.
- Duplicate ID.

The reviewer recommends these actions. The generator performs them.

## Review record

Each review produces one record, returned in the report. Nothing is stored by this skill.

```json
{
  "bundle_id": "CO-MAT-11-ALGEBRA-001-MASTERY",
  "revision_id": "rev_20260402_001",
  "timestamp": "2026-04-02T18:00:00Z",
  "reviewer": "agent",
  "total_questions": 20,
  "errors_found": 0,
  "warnings": 0,
  "decision": "ACEPTAR",
  "questions_reviewed": [
    {
      "question_id": "CO-MAT-11-ALGEBRA-001-v1",
      "status": "ok",
      "errors": []
    }
  ],
  "flags": [],
  "next_review": "2026-04-09"
}
```

## Validation commands

```bash
# Structure validation
node saberparatodos/scripts/validate_content.js --scope=colombia --grade=11

# Quality audit
node saberparatodos/scripts/audit_question_quality.js --scope=colombia --grade-min=3 --grade-max=11

# Review a specific bundle
node scripts/review-bundle.js --bundle=CO-MAT-11-ALGEBRA-001-MASTERY
```

## Sub-agent output format

```
📋 BUNDLE REVIEW: [ID]
Country: [CO/MX/AR/CL/PE/BR]
Grade: [N]
Subject: [name]
Topic: [topic]
Bundle size: [N] questions

═══════════════════════════════════════
RESULT: [✅ ACEPTAR / ⚠️ CORREGIR_PUNTUAL / 🔴 REGENERATE]
═══════════════════════════════════════

SUMMARY:
- Questions reviewed: [N]
- Errors found: [N]
- Warnings: [N]
- Review time: [X] min

QUESTIONS WITH ERRORS:
1. [ID] - [error_type] - [description]
2. [ID] - [error_type] - [description]

REQUIRED ACTIONS (for the generator or owner):
- [list of actions]
```

## Flag system

| Flag | Meaning | Recommended action |
|------|---------|--------------------|
| `CONTAMINATION` | Bundle contains copied or invalid content | Regenerate and purge cache |
| `LOW_QUALITY` | Bundle with qualityScore < 40 | Regenerate and mark |
| `OUTDATED` | Not reviewed in > 30 days | Include in the next batch |
| `PREMIUM_READY` | Passed validation and ready for sale | Eligible for premium publication (owner decision) |

## Batch configuration

- **Batch size**: 10 bundles per run.
- **Frequency**: every 6 hours (cron job).
- **Priority**: bundles without a recent review (> 7 days).
- **Country per batch**: rotating (CO → MX → AR → CL → PE → BR).

## Behavior rules

- Do not modify the bundle during review.
- Do not edit generator prompts, bundles, or repository files. Do not commit.
- Only report errors and decisions.
- If something is ambiguous, mark `CORREGIR_PUNTUAL` and explain why.
- For regeneration, the report carries the full brief; the generator sub-agent acts on it.
