# The eval set. Three buckets, chosen to test different things:
#
#   normal  — well-covered products. Tests everyday quality: are the claims
#             cited, specific, and faithful when there's plenty of real material?
#
#   thin    — real but lightly-covered products. Tests restraint: does the
#             pipeline stay grounded when there isn't much to find, instead of
#             padding with plausible-sounding filler?
#
#   fake    — invented products that do not exist. This is the sharpest test.
#             The ONLY correct behavior is to flag "Insufficient research"
#             rather than hallucinate a company into existence. If Peek writes a
#             confident brief about a company that isn't real, that's the worst
#             possible failure — and this bucket catches it.
#
# `expect_flag = True` means: we expect the brief to contain an
# "Insufficient research" flag (the guardrail firing correctly).

COMPANIES = [
    # --- normal: rich, real coverage -------------------------------------
    {"name": "Linear",     "bucket": "normal", "expect_flag": False},
    {"name": "Notion",     "bucket": "normal", "expect_flag": False},
    {"name": "Figma",      "bucket": "normal", "expect_flag": False},
    {"name": "Vercel",     "bucket": "normal", "expect_flag": False},
    {"name": "Perplexity", "bucket": "normal", "expect_flag": False},
    {"name": "Retool",     "bucket": "normal", "expect_flag": False},
    {"name": "Airtable",   "bucket": "normal", "expect_flag": False},
    # ButterflyMX: added as a regression case. Its 2025 QR Code Intercom is a
    # low-cost, down-market product — so any recommendation that calls small
    # properties an "untapped opening" is contradicting the brief's own facts.
    {"name": "ButterflyMX", "bucket": "normal", "expect_flag": False},

    # --- thin: real, but sparse recent coverage --------------------------
    {"name": "Val Town",         "bucket": "thin", "expect_flag": False},
    {"name": "Fathom Analytics", "bucket": "thin", "expect_flag": False},

    # --- fake: does not exist. Must be flagged, never fabricated ----------
    {"name": "Nimbus Flowdeck",  "bucket": "fake", "expect_flag": True},
]
