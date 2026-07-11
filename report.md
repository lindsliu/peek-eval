# Peek — evaluation report

_Run: 2026-07-04 13:26 · judge: claude-opus-4-8 · scout: claude-sonnet-4-6_

Scores are 1–5 (5 best), assigned by an LLM-as-judge that only sees the brief and the Scout's sources. Treat them as a strong signal to investigate, not gospel — always spot-check a few by hand.

## Model comparison (average scores)

| Metric | claude-sonnet-4-6 | claude-opus-4-8 |
|---|---|---|
| Faithfulness | 5.0 | 5.0 |
| Citation accuracy | 5.0 | 5.0 |
| Specificity | 5.0 | 5.0 |
| Recommendation | 4.0 | 5.0 |
| Overall | 5.0 | 5.0 |

## Guardrail (thin & fake companies)

Did the pipeline correctly flag *Insufficient research* instead of inventing a brief? This is the anti-hallucination test.

- **claude-sonnet-4-6**: no guardrail cases in this run
- **claude-opus-4-8**: no guardrail cases in this run

## Per-company scores

| Company | Bucket | claude-sonnet-4-6 (overall) | claude-opus-4-8 (overall) |
|---|---|---|---|
| ButterflyMX | normal | 5 | 5 |

## What to fix (from the judge)

Every specific fix the judge suggested, grouped by company. Look for the same issue showing up across multiple companies — that points at a prompt to change, not a one-off.

**ButterflyMX**
- (claude-sonnet-4-6) Recommendation: tighten the pricing paragraph — it collapses into a run-on with dangling clauses; split into clean sentences and cut the vague 'contested ground that is narrowing' phrase.
- (claude-sonnet-4-6) Gaps & Weaknesses: fix the redundant phrasing 'A recurring privacy complaint: a privacy concern arises because...' — state it once.
- (claude-sonnet-4-6) Consider adding one line on the Brivo/Verkada enterprise-encroachment angle from [8], since it's a relevant competitive dynamic the notes support and the final omits.
- (claude-opus-4-8) Minor: Gaps & Weaknesses repeats the '[11] intuitive directory/responsive support' point twice — consolidate to avoid redundancy.
- (claude-opus-4-8) Optional: the 'sidewalk to sofa' feature quote in Key Features could cite [7] explicitly where the phrase originates (it does cite [7], fine — just ensure the quoted phrase attribution is clear).

## Raw artifacts

Every agent's output is saved under `results/<company>/` so you can read exactly what each stage produced:
- `scout.md` — the shared research notes
- `<model>/draft.md`, `critique.md`, `final.md` — the pipeline stages
- `<model>/judge.json` — the judge's full scoring for that brief
