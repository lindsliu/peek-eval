# Peek — evaluation harness

A small, honest eval for the Peek pipeline. It answers the only question that
matters for a tool whose whole promise is *"faithful, cited, no hallucination"*:
**does it actually keep that promise — and where does it break?**

It runs the full pipeline (Scout → Writer → Critic → Reviser) over a curated set
of companies, has an LLM-as-judge grade every brief on a faithfulness rubric,
and A/Bs two models. Out comes a scorecard and a ranked list of what to fix.

---

## What it measures

Every final brief is scored 1–5 on five things, by a judge that only sees the
brief and the Scout's sources (the same fact base the pipeline had):

- **Faithfulness** — does every claim trace to a cited source? No unsupported
  claims, no "citation laundering" (citing `[N]` but saying more than N does).
- **Citation accuracy** — does each `[N]` map to a real source that genuinely
  supports the exact claim?
- **Specificity** — concrete numbers and dates where the sources have them, not
  "many" and "popular".
- **Recommendation quality** — specific, time-bound, testable; not "monitor closely".
- **Overall** — holistic trustworthiness as a competitive brief.

Plus the **guardrail test**: the company set includes real-but-thin products and
one company that *does not exist*. The only correct behavior on those is to flag
*Insufficient research* rather than invent a brief. The report tracks how often
the guardrail fires correctly — this is the sharpest anti-hallucination check.

---

## How to run it

1. **Install** (needs Python 3.9+):
   ```
   pip install -r requirements.txt
   ```
2. **Add your key**: copy `.env.example` to `.env` and paste your Anthropic key.
   (Set a spend limit in the Anthropic Console first — this makes real calls.)
3. **Preview the plan and cost — always do this first:**
   ```
   python run_eval.py --dry-run
   ```
   It prints how many API calls the run will make and a rough cost/time range.
4. **Smoke-test on 2 companies** before committing to the whole thing:
   ```
   python run_eval.py --limit 2
   ```
5. **Full run:**
   ```
   python run_eval.py
   ```
6. **Read** `results/report.md`. Open `results/scores.csv` in a spreadsheet if
   you like. Dig into any brief under `results/<company>/`.

Handy flags: `--companies "Linear,Notion"` (just those), `--models "claude-sonnet-4-6"`
(skip the A/B), `--force` (re-run cached results), `--report-only` (rebuild the
report from saved results without spending anything).

---

## How it's designed (and why)

- **Scout runs once per company and the research is shared across both models.**
  Holding the sources constant means the A/B isolates one variable: how well
  each model writes, critiques, and revises *from identical facts*. It also
  halves the expensive web-search calls. (If you'd rather A/B the whole pipeline
  including Scout, that's a small change — say the word.)
- **The judge can't know more than the sources.** It grades faithfulness the way
  a careful human would: claim by claim, against the citations — not against its
  own knowledge of the company.
- **Data collection and analysis are separate.** The run saves every artifact to
  `results/`; the report is built from those files, so you can regenerate or
  tweak the analysis for free with `--report-only`.

**Honest caveats** (good to say out loud in an interview): an LLM judge is a
strong signal, not ground truth — it can miss things and has a mild bias toward
output from its own model family, so always spot-check a few briefs by hand. The
guardrail set is small. And the scores measure grounding, not whether the
strategic take is *good*.

---

## Reading it for an interview

The story isn't the scores — it's the **loop**. Run the eval, find where it
breaks (e.g. "Reviser occasionally softens a claim instead of flagging it," or
"specificity drops on thin companies"), trace it to a specific rule in a specific
agent prompt, change that rule, re-run, and show the score move. The before/after
delta is the thing that separates *"I built a multi-agent app"* from *"I built it,
measured it, found its failure modes, and fixed them."* That's what this harness
is for.
