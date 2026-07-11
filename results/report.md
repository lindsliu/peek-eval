# Peek — evaluation report

_Run: 2026-07-11 16:41 · judge: claude-opus-4-8 · scout: claude-sonnet-4-6_

Scores are 1–5 (5 best), assigned by an LLM-as-judge that only sees the brief and the Scout's sources. Treat them as a strong signal to investigate, not gospel — always spot-check a few by hand.

## Model comparison (average scores)

| Metric | claude-sonnet-4-6 | claude-opus-4-8 |
|---|---|---|
| Faithfulness | 4.64 | 4.82 |
| Citation accuracy | 4.73 | 5.0 |
| Specificity | 5.0 | 5.0 |
| Recommendation | 4.91 | 5.0 |
| Overall | 4.64 | 4.91 |

## Guardrail (thin & fake companies)

Did the pipeline correctly flag *Insufficient research* instead of inventing a brief? This is the anti-hallucination test.

- **claude-sonnet-4-6**: 1/1 flagged correctly
- **claude-opus-4-8**: 1/1 flagged correctly

## Per-company scores

| Company | Bucket | claude-sonnet-4-6 (overall) | claude-opus-4-8 (overall) |
|---|---|---|---|
| Linear | normal | 4 | 5 |
| Notion | normal | 5 | 5 |
| Figma | normal | 4 | 4 |
| Vercel | normal | 5 | 5 |
| Perplexity | normal | 5 | 5 |
| Retool | normal | 4 | 5 |
| Airtable | normal | 5 | 5 |
| ButterflyMX | normal | 5 | 5 |
| Val Town | thin | 4 | 5 |
| Fathom Analytics | thin | 5 | 5 |
| Nimbus Flowdeck | fake | 5 | 5 |

## What to fix (from the judge)

Every specific fix the judge suggested, grouped by company. Look for the same issue showing up across multiple companies — that points at a prompt to change, not a one-off.

**Linear**
- (claude-sonnet-4-6) TL;DR: remove or resource 'compliance-heavy enterprise buyers' — no source supports it; replace with the actually-supported unserved segments (multi-team program planning, non-technical departments).
- (claude-sonnet-4-6) Recommendation: fix the '[7, 8]' citation for 'sticky PLG motion' — PLG is supported by [5], not [7]/[8].
- (claude-sonnet-4-6) Positioning: tighten the '[5, 9, 10]' citation for the start-immediately/PLG claim to [5], the source that actually states it.
- (claude-sonnet-4-6) Positioning: fix the duplicated/garbled sentence ('extending the platform beyond issue tracking... [8] — extending the platform beyond issue tracking...') into one clean clause.
- (claude-opus-4-8) Optional: in Pricing, could clarify the tension between [6]'s 'no usage meters' claim and [2]'s note that high-volume compute 'may move to usage-based pricing beyond a threshold' — the brief includes both but doesn't reconcile them for the reader.

**Notion**
- (claude-sonnet-4-6) Minor: the 'monetization gap' inference (80% users abroad vs 50%+ revenue) mixes a July 2025 user-distribution stat [9] with a 2024 revenue stat [8]; add a caveat that the two figures are from different dates/bases rather than implying a clean gap.
- (claude-sonnet-4-6) Consider noting in Recommendation that $300M+ ARR and 120M users are estimates/older-dated ([8] late 2024, [9] to 2026) so the PM doesn't treat them as current-precise.
- (claude-opus-4-8) Minor: 'Sources reviewed: 13' vs 'As of 2026-06-27' — the freshest sources are dated June/July 2026 ([3] accessed July 2026, [11] June 2026), so the as-of date slightly understates recency; align it or note the latest source date.
- (claude-opus-4-8) Optional: The Positioning section calls Notion a 'hub for all workplace communication [6]' — [6] frames this as Notion's strategy, which is fine, but could be tightened to attribute it as the company's stated strategy rather than a neutral positioning fact.

**Figma**
- (claude-sonnet-4-6) Recent Moves: change 'down approximately 40–49%' to '~40%' to match source [12]; the 49.3% figure has no cited source support.
- (claude-sonnet-4-6) Recommendation: drop or re-cite 'network effects that would be costly for enterprise teams to unwind [14]' — [14] does not support a network-effects/switching-cost claim; either cite the NDR retention data [8] as the switching-cost proxy or soften the claim.
- (claude-sonnet-4-6) Gaps & Weaknesses: remove or rephrase 'automatic seat consumption without admin notifications [3,4]' — neither source states this; use the supported claim that admins had difficulty getting seats approved [4] and that billing shifted to admin-approval-first [3].
- (claude-sonnet-4-6) Key Features #2: clarify that the 30% [8] and 60% [11] figures cover different cohorts ($100K+ ARR vs 'largest enterprise customers') rather than implying a single metric's growth.
- (claude-opus-4-8) In TL;DR and Gaps & Weaknesses, stop attributing the 'mid-market'/'price-sensitive band' framing to [11]; [11] only says Stitch is free and a direct competitive challenge. Either drop the citation on that inference or mark it as analysis.
- (claude-opus-4-8) In Positioning, either drop the 'as of Q3 2025' date on the 540,000 paid teams figure or verify — [8] does not explicitly date the 540K number.
- (claude-opus-4-8) Reconcile the [4] Dec-2024 dating with the repeated 'March 2025 pricing overhaul' framing — clarify that the forum reaction ([4]) predates or accompanies the March 2025 changes.

**Vercel**
- (claude-sonnet-4-6) Minor: the 'As of' date (2026-06-01) predates several cited sources dated later in the notes (e.g. [6] April 2026 is fine, but scout research was July 3, 2026); align the as-of date with the research date to avoid appearing stale.
- (claude-sonnet-4-6) Optional: the synthesis note claims v0 tracked $42M ARR 'as of February 2025' in the Recommendation cited to [5] — [5] says 'as of February 2025' so this is fine, but flag that this figure is dated relative to the $340M current ARR to avoid implying it's current.
- (claude-opus-4-8) Minor: TL;DR could add inline citations for the $9.3B and $340M figures to be airtight, though both are supported and cited in the body.
- (claude-opus-4-8) Optional: note that 'Vercel Ventures / AI Accelerator alumni raised $100M+' (from synthesis) was omitted — a legitimate competitive-moat signal that could strengthen the Positioning or Recent Moves section.

**Perplexity**
- (claude-sonnet-4-6) Gaps & Weaknesses: tighten the phrase 'all related to alleged unauthorized content scraping [8,9]' — [8] only specifies BBC (and Cloudflare/Wired) as scraping-related; NYT/Britannica are described as copyright suits, so qualify rather than generalize.
- (claude-sonnet-4-6) Consider noting in Pricing that Enterprise Max ($325) exceeds the consumer Max ($200), to avoid reader confusion about the '10x jump' framing which refers only to Pro-to-Max.
- (claude-opus-4-8) Minor: in Recommendation the phrase 'jumps 10x from Pro ($20) to Max ($200)' cites [1,3] — both prices are supported, so this is fine, but could note Enterprise Max $325 to complete the ladder picture.
- (claude-opus-4-8) Optional: cite the ARR trajectory ($16M→$305M, $656M target) somewhere to strengthen the 'capital-rich/fast momentum' claim with hard growth numbers.

**Retool**
- (claude-sonnet-4-6) Pricing section: remove or explicitly flag the 'AI agent features introduce consumption-based pricing' claim — no numbered source supports it; it comes only from the synthesis.
- (claude-sonnet-4-6) Pricing section: either cite the Team=$10/user/mo figure to a real source or drop the implied Team price; currently the '5x jump' math relies on a Team price not present in any numbered source.
- (claude-sonnet-4-6) Key Features #2: 'AI Assist tab (public beta as of January 2026)' — [9] is dated January 2026 but does not clearly state the beta began January 2026; soften to 'per a January 2026 review' to avoid implying a launch date.
- (claude-opus-4-8) In Recommendation and TL;DR, remove or explicitly caveat the 'AI agent features introduce consumption-based pricing layered on top' claim — no numbered source supports it; either drop it or mark it as an unverified inference rather than citing [2,3,9] alongside it.
- (claude-opus-4-8) In Gaps/Positioning, surface the G2 4.6/5 from 358 reviews [8] — it's available and strengthens the user-sentiment read.
- (claude-opus-4-8) Tighten the watch-trigger citation: attach [2,3] to the SSO-tier trigger and [9] to the code-export trigger rather than clustering all three around a sentence that also contains the unsupported pricing claim.

**Airtable**
- (claude-sonnet-4-6) Minor: in Key Features #4, the '25,000 runs/month on Team' phrasing adds 'per month' — source [2] says '25,000 automation runs' without specifying a monthly cadence; verify or drop the frequency qualifier.
- (claude-sonnet-4-6) Optional: the DeepSky 'integration depth not documented' and App Studio 'not elaborated' hedges are good but could be consolidated to keep the Key Features section tighter.
- (claude-opus-4-8) Minor: TL;DR could note that the 80% Fortune 100 / $478M ARR figures are 2024 vintage per [10] to preempt staleness questions.
- (claude-opus-4-8) Optional: the enterprise-growth range (~30% vs 40%+) could flag that these come from a single lower-authority source [11] (BusinessModelCanvasTemplate.com) whose numbers conflict with each other.

**ButterflyMX**
- (claude-sonnet-4-6) Recommendation: tighten the pricing paragraph — it collapses into a run-on with dangling clauses; split into clean sentences and cut the vague 'contested ground that is narrowing' phrase.
- (claude-sonnet-4-6) Gaps & Weaknesses: fix the redundant phrasing 'A recurring privacy complaint: a privacy concern arises because...' — state it once.
- (claude-sonnet-4-6) Consider adding one line on the Brivo/Verkada enterprise-encroachment angle from [8], since it's a relevant competitive dynamic the notes support and the final omits.
- (claude-opus-4-8) Minor: Gaps & Weaknesses repeats the '[11] intuitive directory/responsive support' point twice — consolidate to avoid redundancy.
- (claude-opus-4-8) Optional: the 'sidewalk to sofa' feature quote in Key Features could cite [7] explicitly where the phrase originates (it does cite [7], fine — just ensure the quoted phrase attribution is clear).

**Val Town**
- (claude-sonnet-4-6) Gaps & Weaknesses / Recommendation: soften the 'no Python, Go, Rust, or Ruby' claim to 'JavaScript/TypeScript only per positioning [1][12]; no other-language support documented in sources' — do not present the enumeration as a sourced fact, since the entire wedge thesis depends on it.
- (claude-sonnet-4-6) Gaps section: change 'a series of public security incidents [6]' to 'a series of embarrassing security vulnerabilities [6]' to match source wording exactly.
- (claude-sonnet-4-6) Recommendation: acknowledge that the language-gap wedge is inferred, not confirmed, so a PM knows to verify Val Town's current runtime support before committing to that positioning.
- (claude-opus-4-8) Optional: in Pricing, clarify that the $200/mo Business figure comes from an April update referencing the Teams plan pre-rebrand, since [2] rebrands Teams to Business without restating the price — a reader could momentarily conflate the two.
- (claude-opus-4-8) Optional: 'Sources reviewed: 13' is accurate but the As-of date (2026-06-10) matches the May update [10]; could note the freshest source date for clarity.

**Fathom Analytics**
- (claude-sonnet-4-6) Minor: in Positioning, the phrasing 'trusted by over one million websites ... though G2 data shows approximately 15,584 companies' is fine but could explicitly note these count different things (websites vs. companies) to avoid a PM misreading them as contradictory.
- (claude-sonnet-4-6) Optional: name Plausible and Simple Analytics as the direct peers in the Recommendation (both are in the synthesis) to sharpen the competitive-set framing for a market entrant.
- (claude-opus-4-8) Minor: in Positioning, the split description of target segments across [2] and [3] is handled well but could note the slight framing difference more explicitly.
- (claude-opus-4-8) Optional: the 'As of 2025-09-01' date slightly predates the September 2025 shipping report cited from [5]; verify consistency.

## Raw artifacts

Every agent's output is saved under `results/<company>/` so you can read exactly what each stage produced:
- `scout.md` — the shared research notes
- `<model>/draft.md`, `critique.md`, `final.md` — the pipeline stages
- `<model>/judge.json` — the judge's full scoring for that brief
