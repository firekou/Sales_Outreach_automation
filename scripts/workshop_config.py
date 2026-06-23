#!/usr/bin/env python3
"""
Workshop Config — Fill This In
================================
This is the ONLY file you need to edit.
Everything else runs automatically once you fill in the three sections below.

After editing, run:
    python run_pipeline.py

Questions? See SETUP.md in the repo root.
"""

# ════════════════════════════════════════════════════════════════════════
# SECTION 1 — WHO ARE YOU?
# Your account identity: how you'll appear in every outreach message.
# ════════════════════════════════════════════════════════════════════════

# Short lowercase identifier — no spaces, no special characters.
# This is used as the --account flag internally. Examples: "sarah", "james", "minh_hk"
MY_ACCOUNT_KEY = "yourname"

MY_ACCOUNT = {
    # Your name as it appears in messages
    "display_name": "Your Full Name",

    # Your role and company — shown in your LinkedIn persona
    # Example: "Head of Growth, Acme AI"
    "title": "Your Role, Company Name",

    # 1–2 sentences describing how you want to sound in outreach messages.
    # The AI will match this tone when writing connection requests and value messages.
    # Example: "Warm and analytical. You speak peer-to-peer, never like a vendor.
    #           You lead with a genuine observation about their work before anything else."
    "style_hint": (
        "Warm and direct. You speak as a peer, not a vendor. "
        "You lead with curiosity and specific observations, never with a pitch."
    ),

    # Job titles of the people you want to reach.
    # These shape how the AI frames value messages.
    "icp_focus": [
        "Founder", "Co-Founder", "CEO",
        "Marketing Manager", "Head of Growth",
        "Agency Owner", "Creative Director",
    ],

    # Max connection requests per day. Keep at 20 for safety (LinkedIn's limit is ~25–30).
    "daily_limit": 20,

    # Time window for sending (local time). Format: "HH:MM–HH:MM"
    "send_window": "09:00–10:00",
}


# ════════════════════════════════════════════════════════════════════════
# SECTION 2 — WHERE ARE YOU TARGETING?
# Pick the countries you want to search in.
#
# Common LinkedIn geo IDs:
#
#   EAST ASIA
#     Taiwan          104187078
#     Japan           101355337
#     South Korea     105149562
#     Hong Kong       103291313
#     Singapore       102454443
#
#   SOUTHEAST ASIA
#     Vietnam         104195383
#     Thailand        105072991
#     Malaysia        102454443   (note: same as Singapore in older API versions)
#     Indonesia       102478060
#     Philippines     103121230
#
#   LATAM
#     Mexico          103323778
#     Argentina       100446943
#     Colombia        100877388
#     Chile           104621616
#     Peru            102927786
#     Brazil          106057199
#
#   EUROPE
#     Spain           105646813
#     Germany         101282230
#     France          105015875
#     UK              101165590
#
# You can combine multiple geos in one list.
# ════════════════════════════════════════════════════════════════════════

MY_GEOS = [
    104187078,  # Taiwan
    101355337,  # Japan
    105149562,  # South Korea
    103291313,  # Hong Kong
    102454443,  # Singapore
]


# ════════════════════════════════════════════════════════════════════════
# SECTION 3 — WHAT KIND OF PEOPLE ARE YOU LOOKING FOR?
# Define your search combos. Each combo = one LinkedIn search query.
#
# Tips:
#   • 2–3 focused combos beat 6 broad ones
#   • "limit" = max leads per combo. Use 10–20 for testing, 60–80 for full runs
#   • "functions" must match LinkedIn's exact category names — full list in SETUP.md
#   • "seniority_levels" must match exactly:
#       "Owner/Partner", "CXO", "Vice President", "Director",
#       "Experienced Manager", "Entry Level Manager", "Strategic",
#       "Senior", "Entry Level", "In Training"
#   • "posted_on_linkedin": "true" filters to people active in the last 30 days
# ════════════════════════════════════════════════════════════════════════

MY_SEARCH_COMBOS = [

    # ── Combo A: Startup Founders & CEOs (East Asia) ───────────────────
    {
        "name":     "East Asia: Startup Founders & CEOs",
        "code":     "ws_A",
        "priority": "P1",
        "input": {
            "geo_codes":          MY_GEOS,
            "title_keywords":     [
                "Founder", "Co-Founder", "CEO", "CTO",
                "Startup", "Entrepreneur", "Managing Director",
            ],
            "company_headcounts": ["1-10", "11-50"],
            "functions":          ["Entrepreneurship", "Business Development", "Information Technology"],
            "seniority_levels":   ["Owner/Partner", "CXO"],
            "posted_on_linkedin": "true",
            "limit":              20,   # ← raise to 80 for full runs
        },
    },

    # ── Combo B: Marketing & Content Leaders (East Asia) ───────────────
    {
        "name":     "East Asia: Marketing & Content Leaders",
        "code":     "ws_B",
        "priority": "P1",
        "input": {
            "geo_codes":          MY_GEOS,
            "title_keywords":     [
                "Marketing Manager", "Content Creator", "Digital Marketing",
                "Growth Manager", "Brand Manager", "Content Strategist",
                "Community Manager", "Social Media Manager",
            ],
            "company_headcounts": ["1-10", "11-50", "51-200"],
            "functions":          ["Marketing"],
            "seniority_levels":   ["Experienced Manager", "Director", "Owner/Partner", "Senior"],
            "posted_on_linkedin": "true",
            "limit":              20,
        },
    },

    # ── Combo C: Vietnam — Founders & Agency Owners ────────────────────
    # Remove or replace this combo if you're not targeting Vietnam.
    {
        "name":     "Vietnam: Founders & Agency Owners",
        "code":     "ws_C",
        "priority": "P2",
        "input": {
            "geo_codes":          [104195383],  # Vietnam only
            "title_keywords":     [
                "Founder", "CEO", "Agency Owner",
                "Director", "Managing Director",
            ],
            "company_headcounts": ["1-10", "11-50"],
            "functions":          ["Entrepreneurship", "Marketing", "Business Development"],
            "seniority_levels":   ["Owner/Partner", "CXO", "Director"],
            "posted_on_linkedin": "true",
            "limit":              20,
        },
    },

]
