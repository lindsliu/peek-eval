#!/usr/bin/env python3
"""Peek evaluation harness.

Runs the full Peek pipeline (Scout -> Writer -> Critic -> Reviser) over a
curated set of companies, then has an LLM-as-judge grade each final brief on a
faithfulness rubric. Compares two models (A/B) on the same inputs.

Design notes (worth knowing, and good to mention in an interview):
  * Scout runs ONCE per company (with real web search) and that research is
    shared across both models. Holding the research constant means the A/B
    isolates one thing: how well each model WRITES, CRITIQUES, and REVISES from
    identical sources. It also halves the expensive web-search calls.
  * The judge only ever sees the final brief and the Scout's sources — the same
    fact base the pipeline was supposed to stay inside. It cannot "know" more
    than the sources, so it grades faithfulness the same way a careful human
    would: claim by claim, against the citations.
  * Everything is saved to results/ as it goes, so a crash mid-run doesn't lose
    completed work, and you can rebuild the report without re-spending.

Usage:
  python run_eval.py --dry-run          # show the plan + rough cost, no API calls
  python run_eval.py --limit 2          # smoke test: first 2 companies only
  python run_eval.py                    # full run
  python run_eval.py --report-only      # rebuild report from saved results
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from companies import COMPANIES          # noqa: E402
import report as report_builder          # noqa: E402


# --------------------------------------------------------------------------
# Config (override any of these via environment variables or a .env file)
# --------------------------------------------------------------------------
def load_dotenv():
    """Tiny .env loader so there's no extra dependency."""
    path = os.path.join(HERE, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


load_dotenv()

SONNET = os.environ.get("PEEK_SONNET_MODEL", "claude-sonnet-4-6")
OPUS = os.environ.get("PEEK_OPUS_MODEL", "claude-opus-4-8")
SCOUT_MODEL = os.environ.get("PEEK_SCOUT_MODEL", SONNET)
JUDGE_MODEL = os.environ.get("PEEK_JUDGE_MODEL", OPUS)

MAX_TOKENS = {"scout": 4000, "writer": 3000, "critic": 2500, "reviser": 3000, "judge": 2000}
WEB_SEARCH_TOOL = {"type": "web_search_20250305", "name": "web_search", "max_uses": 6}


# --------------------------------------------------------------------------
# Load prompts
# --------------------------------------------------------------------------
def load_prompt(name):
    with open(os.path.join(HERE, "prompts", name + ".md"), encoding="utf-8") as f:
        return f.read()


PROMPTS = {n: load_prompt(n) for n in ("scout", "writer", "critic", "reviser")}
with open(os.path.join(HERE, "judge_prompt.md"), encoding="utf-8") as f:
    JUDGE_SYSTEM = f.read()


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# --------------------------------------------------------------------------
# Anthropic call (non-streaming), with a small retry
# --------------------------------------------------------------------------
def make_client():
    try:
        import anthropic
    except ImportError:
        sys.exit("The 'anthropic' package isn't installed. Run: pip install -r requirements.txt")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ANTHROPIC_API_KEY isn't set. Copy .env.example to .env and add your key.")
    return anthropic.Anthropic(api_key=key)


def call(client, model, system, user, max_tokens, use_web=False):
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    if use_web:
        kwargs["tools"] = [WEB_SEARCH_TOOL]

    last_err = None
    for attempt in range(3):
        try:
            resp = client.messages.create(**kwargs)
            return "".join(
                b.text for b in resp.content if getattr(b, "type", None) == "text"
            )
        except Exception as e:  # noqa: BLE001
            last_err = e
            wait = 4 * (attempt + 1)
            print(f"      ! call failed ({e}); retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"call failed after retries: {last_err}")


# --------------------------------------------------------------------------
# Pipeline stages
# --------------------------------------------------------------------------
def run_scout(client, name):
    return call(client, SCOUT_MODEL, PROMPTS["scout"],
                f"Research this product and produce your scout notes: {name}",
                MAX_TOKENS["scout"], use_web=True)


def run_downstream(client, model, name, scout):
    draft = call(client, model, PROMPTS["writer"],
                 f"Product: {name}\n\nHere are the Scout's notes (scout_notes.md):\n\n{scout}",
                 MAX_TOKENS["writer"])
    critique = call(client, model, PROMPTS["critic"],
                    f"Here is the draft one-pager (draft.md):\n\n{draft}\n\n"
                    f"---\n\nHere are the Scout's notes (scout_notes.md):\n\n{scout}",
                    MAX_TOKENS["critic"])
    final = call(client, model, PROMPTS["reviser"],
                 f"Here is the draft (draft.md):\n\n{draft}\n\n"
                 f"---\n\nHere is the critique (critique.md):\n\n{critique}\n\n"
                 f"---\n\nHere are the Scout's notes (scout_notes.md):\n\n{scout}",
                 MAX_TOKENS["reviser"])
    return draft, critique, final


def run_judge(client, company, scout, final):
    user = (
        f"Company: {company['name']}\n"
        f"Bucket: {company['bucket']}\n"
        f"Expected insufficient-research flag: {company['expect_flag']}\n\n"
        f"=== scout_notes.md ===\n{scout}\n\n"
        f"=== final.md ===\n{final}\n"
    )
    raw = call(client, JUDGE_MODEL, JUDGE_SYSTEM, user, MAX_TOKENS["judge"])
    return parse_json(raw)


def parse_json(raw):
    """Best-effort JSON extraction from the judge's reply."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
    return {"_parse_error": True, "_raw": raw[:2000]}


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------
def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    ap = argparse.ArgumentParser(description="Peek evaluation harness")
    ap.add_argument("--outdir", default=os.path.join(HERE, "results"))
    ap.add_argument("--limit", type=int, help="only the first N companies (smoke test)")
    ap.add_argument("--companies", help="comma-separated names to run (overrides the set)")
    ap.add_argument("--models", default=f"{SONNET},{OPUS}",
                    help="comma-separated pipeline models to A/B")
    ap.add_argument("--force", action="store_true", help="re-run even if results exist")
    ap.add_argument("--redo", action="store_true",
                    help="re-run writer/critic/reviser/judge on the CACHED Scout research "
                         "(use this after editing prompts — keeps research constant, no re-charge for web search)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan + cost, no API calls")
    ap.add_argument("--report-only", action="store_true", help="rebuild report from saved results")
    args = ap.parse_args()

    if args.report_only:
        rp, cp = report_builder.build_report(args.outdir)
        print(f"Rebuilt {rp}\n        {cp}")
        return

    models = [m.strip() for m in args.models.split(",") if m.strip()]

    companies = COMPANIES
    if args.companies:
        wanted = {c.strip().lower() for c in args.companies.split(",")}
        companies = [c for c in COMPANIES if c["name"].lower() in wanted]
    if args.limit:
        companies = companies[: args.limit]

    # cost / plan preview
    scout_calls = len(companies)
    downstream_calls = len(companies) * len(models) * 3
    judge_calls = len(companies) * len(models)
    total = scout_calls + downstream_calls + judge_calls
    print("=" * 64)
    print("PEEK EVAL — plan")
    print(f"  companies      : {len(companies)}  ({', '.join(c['name'] for c in companies)})")
    print(f"  pipeline models: {', '.join(models)}")
    print(f"  scout model    : {SCOUT_MODEL} (shared, with web search)")
    print(f"  judge model    : {JUDGE_MODEL}")
    print(f"  API calls      : {scout_calls} scout + {downstream_calls} downstream "
          f"+ {judge_calls} judge = {total}")
    print(f"  ~cost estimate : very roughly ${total * 0.03:.2f}–${total * 0.09:.2f} "
          f"(Opus + web search push the top end up)")
    print(f"  ~time          : ~{total * 12 // 60}–{total * 22 // 60} min (sequential)")
    print("=" * 64)
    if args.dry_run:
        print("Dry run — no API calls made. Re-run without --dry-run to execute.")
        return

    client = make_client()
    records = []

    for i, company in enumerate(companies, 1):
        name = company["name"]
        cslug = slug(name)
        cdir = os.path.join(args.outdir, cslug)
        print(f"\n[{i}/{len(companies)}] {name}  ({company['bucket']})")

        # Scout once (shared), cached to disk
        scout_path = os.path.join(cdir, "scout.md")
        if os.path.exists(scout_path) and not args.force:
            scout = open(scout_path, encoding="utf-8").read()
            print("    scout: cached")
        else:
            print("    scout: researching (web search)…")
            scout = run_scout(client, name)
            write(scout_path, scout)

        for model in models:
            mslug = slug(model)
            mdir = os.path.join(cdir, mslug)
            final_path = os.path.join(mdir, "final.md")
            judge_path = os.path.join(mdir, "judge.json")

            if os.path.exists(judge_path) and not args.force and not args.redo:
                print(f"    {model}: cached")
                judge = json.load(open(judge_path, encoding="utf-8"))
            else:
                print(f"    {model}: writer → critic → reviser…")
                draft, critique, final = run_downstream(client, model, name, scout)
                write(os.path.join(mdir, "draft.md"), draft)
                write(os.path.join(mdir, "critique.md"), critique)
                write(final_path, final)
                print(f"    {model}: judging…")
                judge = run_judge(client, company, scout, final)
                write(judge_path, json.dumps(judge, indent=2))

            records.append({
                "company": name, "bucket": company["bucket"],
                "expect_flag": company["expect_flag"], "model": model,
                "judge": judge,
            })

    # save aggregate + build report
    meta = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "scout_model": SCOUT_MODEL, "judge_model": JUDGE_MODEL,
    }
    scores = {"meta": meta, "models": models, "records": records}
    write(os.path.join(args.outdir, "scores.json"), json.dumps(scores, indent=2))

    rp, cp = report_builder.build_report(args.outdir)
    print("\n" + "=" * 64)
    print("DONE.")
    print(f"  report : {rp}")
    print(f"  csv    : {cp}")
    print(f"  raw    : {args.outdir}/<company>/…")
    print("=" * 64)


if __name__ == "__main__":
    main()
