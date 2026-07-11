"""Build the human-readable report and CSV from saved eval results.

This does NO API calls — it only reads results/scores.json (written by
run_eval.py) and turns it into:
  - results/report.md   a readable scorecard with the A/B table and fix list
  - results/scores.csv  one row per (company, model) for spreadsheets

You can re-run this any time without spending anything:
    python run_eval.py --report-only
"""

import csv
import json
import os
from collections import defaultdict

METRICS = [
    ("faithfulness", "Faithfulness"),
    ("citation_accuracy", "Citation accuracy"),
    ("specificity", "Specificity"),
    ("recommendation_quality", "Recommendation"),
    ("overall", "Overall"),
]


def _mean(nums):
    nums = [n for n in nums if isinstance(n, (int, float))]
    return round(sum(nums) / len(nums), 2) if nums else None


def _score(record, metric):
    try:
        return record["judge"][metric]["score"]
    except Exception:
        return None


def build_report(outdir):
    scores_path = os.path.join(outdir, "scores.json")
    if not os.path.exists(scores_path):
        raise SystemExit("No results/scores.json found. Run the eval first.")

    with open(scores_path, encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    models = data["models"]
    run_meta = data.get("meta", {})

    # ---- CSV: one row per (company, model) ------------------------------
    csv_path = os.path.join(outdir, "scores.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["company", "bucket", "model", "faithfulness", "citation_accuracy",
             "specificity", "recommendation_quality", "overall",
             "expected_flag", "flagged_correctly"]
        )
        for r in records:
            g = r["judge"].get("guardrail", {}) if r.get("judge") else {}
            w.writerow([
                r["company"], r["bucket"], r["model"],
                _score(r, "faithfulness"), _score(r, "citation_accuracy"),
                _score(r, "specificity"), _score(r, "recommendation_quality"),
                _score(r, "overall"),
                g.get("expected_flag"), g.get("flagged_correctly"),
            ])

    # ---- aggregate per model --------------------------------------------
    per_model = {m: defaultdict(list) for m in models}
    for r in records:
        m = r["model"]
        if not r.get("judge"):
            continue
        for key, _ in METRICS:
            s = _score(r, key)
            if s is not None:
                per_model[m][key].append(s)

    # ---- guardrail results (thin/fake) ----------------------------------
    guardrail = {m: {"correct": 0, "total": 0} for m in models}
    for r in records:
        if not r.get("judge"):
            continue
        g = r["judge"].get("guardrail", {})
        if g.get("expected_flag"):
            guardrail[r["model"]]["total"] += 1
            if g.get("flagged_correctly"):
                guardrail[r["model"]]["correct"] += 1

    # ---- collect fixes ---------------------------------------------------
    fixes = []
    for r in records:
        if not r.get("judge"):
            continue
        for fx in r["judge"].get("overall", {}).get("top_fixes", []):
            fixes.append((r["company"], r["model"], fx))

    # ---- write the markdown report --------------------------------------
    lines = []
    lines.append("# Peek — evaluation report\n")
    if run_meta.get("timestamp"):
        lines.append(f"_Run: {run_meta['timestamp']} · judge: "
                     f"{run_meta.get('judge_model', '?')} · scout: "
                     f"{run_meta.get('scout_model', '?')}_\n")
    lines.append(
        "Scores are 1–5 (5 best), assigned by an LLM-as-judge that only sees the "
        "brief and the Scout's sources. Treat them as a strong signal to "
        "investigate, not gospel — always spot-check a few by hand.\n"
    )

    # A/B summary table
    lines.append("## Model comparison (average scores)\n")
    header = "| Metric | " + " | ".join(models) + " |"
    sep = "|" + "---|" * (len(models) + 1)
    lines.append(header)
    lines.append(sep)
    for key, label in METRICS:
        row = [label]
        for m in models:
            row.append(str(_mean(per_model[m][key])))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # guardrail
    lines.append("## Guardrail (thin & fake companies)\n")
    lines.append(
        "Did the pipeline correctly flag *Insufficient research* instead of "
        "inventing a brief? This is the anti-hallucination test.\n"
    )
    for m in models:
        g = guardrail[m]
        if g["total"]:
            lines.append(f"- **{m}**: {g['correct']}/{g['total']} flagged correctly")
        else:
            lines.append(f"- **{m}**: no guardrail cases in this run")
    lines.append("")

    # per-company detail
    lines.append("## Per-company scores\n")
    by_company = defaultdict(dict)
    bucket_of = {}
    for r in records:
        by_company[r["company"]][r["model"]] = _score(r, "overall")
        bucket_of[r["company"]] = r["bucket"]
    lines.append("| Company | Bucket | " + " | ".join(f"{m} (overall)" for m in models) + " |")
    lines.append("|" + "---|" * (len(models) + 2))
    for company, scores in by_company.items():
        row = [company, bucket_of[company]]
        for m in models:
            row.append(str(scores.get(m, "—")))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ranked fix list
    lines.append("## What to fix (from the judge)\n")
    lines.append(
        "Every specific fix the judge suggested, grouped by company. Look for "
        "the same issue showing up across multiple companies — that points at a "
        "prompt to change, not a one-off.\n"
    )
    fixes_by_company = defaultdict(list)
    for company, model, fx in fixes:
        fixes_by_company[company].append(f"({model}) {fx}")
    if not fixes_by_company:
        lines.append("_No fixes recorded — either the briefs were clean or the "
                     "judge output didn't parse. Check the raw judge.json files._\n")
    for company, items in fixes_by_company.items():
        lines.append(f"**{company}**")
        for it in items:
            lines.append(f"- {it}")
        lines.append("")

    # where to dig
    lines.append("## Raw artifacts\n")
    lines.append(
        "Every agent's output is saved under `results/<company>/` so you can read "
        "exactly what each stage produced:\n"
        "- `scout.md` — the shared research notes\n"
        "- `<model>/draft.md`, `critique.md`, `final.md` — the pipeline stages\n"
        "- `<model>/judge.json` — the judge's full scoring for that brief\n"
    )

    report_path = os.path.join(outdir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path, csv_path
