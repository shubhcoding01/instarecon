# def analyze(profile: dict):
#     """
#     Analyze Instagram profile and assign risk level

#     Args:
#         profile (dict)

#     Returns:
#         dict → { risk_level, score, reasons }
#     """

#     score = 0
#     reasons = []

#     followers = profile.get("followers", 0)
#     following = profile.get("following", 0)
#     posts = profile.get("posts", 0)
#     bio = profile.get("bio", "").lower()

#     # -------------------------------
#     # Rule 1: Low followers
#     # -------------------------------
#     if followers < 50:
#         score += 1
#         reasons.append("Very low followers")

#     # -------------------------------
#     # Rule 2: High following
#     # -------------------------------
#     if following > 1000:
#         score += 1
#         reasons.append("Following too many users")

#     # -------------------------------
#     # Rule 3: Follower/Following ratio
#     # -------------------------------
#     if following > 0:
#         ratio = followers / following
#         if ratio < 0.1:
#             score += 1
#             reasons.append("Poor follower/following ratio")

#     # -------------------------------
#     # Rule 4: Very low posts
#     # -------------------------------
#     if posts < 3:
#         score += 1
#         reasons.append("Very few posts")

#     # -------------------------------
#     # Rule 5: Spam keywords in bio
#     # -------------------------------
#     spam_keywords = [
#         "crypto", "investment", "earn money",
#         "profit", "trading", "forex",
#         "giveaway", "dm me", "link in bio"
#     ]

#     for keyword in spam_keywords:
#         if keyword in bio:
#             score += 1
#             reasons.append(f"Spam keyword in bio: {keyword}")
#             break

#     # -------------------------------
#     # Rule 6: Empty bio
#     # -------------------------------
#     if bio.strip() == "":
#         score += 1
#         reasons.append("Empty bio")

#     # -------------------------------
#     # Final Risk Level
#     # -------------------------------
#     if score >= 4:
#         risk = "HIGH RISK"
#     elif score >= 2:
#         risk = "MEDIUM RISK"
#     else:
#         risk = "SAFE"

#     return {
#         "risk": risk,
#         "score": score,
#         "reasons": reasons
#     }


def analyze(profile: dict) -> dict:
    """
    Analyze Instagram profile and assign risk level.

    Args:
        profile (dict): Instagram profile data containing fields like
                        followers, following, posts, bio, username,
                        account_age_days, is_verified, avg_likes,
                        avg_comments, profile_pic, highlights.

    Returns:
        dict: {
            "risk": str,        # "HIGH RISK", "MEDIUM RISK", "LOW RISK", "SAFE"
            "score": int,
            "reasons": list[str],
            "flags": list[str], # short machine-readable tags
            "summary": str      # one-line human-readable summary
        }
    """

    score = 0
    reasons = []
    flags = []

    # ── Extract fields ──────────────────────────────────────────────
    followers       = profile.get("followers", 0)
    following       = profile.get("following", 0)
    posts           = profile.get("posts", 0)
    bio             = profile.get("bio", "").lower().strip()
    username        = profile.get("username", "").lower()
    account_age     = profile.get("account_age_days", None)   # int or None
    is_verified     = profile.get("is_verified", False)
    avg_likes       = profile.get("avg_likes", None)          # int or None
    avg_comments    = profile.get("avg_comments", None)       # int or None
    has_pic         = profile.get("profile_pic", False)
    highlights      = profile.get("highlights", 0)

    # ── Helper ──────────────────────────────────────────────────────
    def flag(tag: str, reason: str, points: int = 1):
        nonlocal score
        score += points
        flags.append(tag)
        reasons.append(reason)

    # ================================================================
    # SECTION 1 — Followers & Following
    # ================================================================

    if followers < 20:
        flag("VERY_LOW_FOLLOWERS", "Extremely low follower count (<20)", points=2)
    elif followers < 50:
        flag("LOW_FOLLOWERS", "Very low follower count (<50)")

    if following > 5000:
        flag("MASS_FOLLOWING", "Following an unusually large number of accounts (>5000)", points=2)
    elif following > 1000:
        flag("HIGH_FOLLOWING", "Following too many users (>1000)")

    if following > 0:
        ratio = followers / following
        if ratio < 0.05:
            flag("VERY_POOR_RATIO", "Extremely poor follower/following ratio (<0.05)", points=2)
        elif ratio < 0.1:
            flag("POOR_RATIO", "Poor follower/following ratio (<0.1)")

    # ================================================================
    # SECTION 2 — Posts & Activity
    # ================================================================

    if posts == 0:
        flag("NO_POSTS", "Account has zero posts", points=2)
    elif posts < 3:
        flag("FEW_POSTS", "Very few posts (<3)")

    # Ghost account: lots of followers, zero engagement
    if avg_likes is not None and followers > 100 and avg_likes < 5:
        flag("GHOST_ENGAGEMENT", "Suspiciously low likes despite follower count")

    if avg_comments is not None and followers > 100 and avg_comments < 1:
        flag("ZERO_COMMENTS", "Almost no comments — possible bot or ghost account")

    # ================================================================
    # SECTION 3 — Bio Analysis
    # ================================================================

    if bio == "":
        flag("EMPTY_BIO", "Bio is empty")

    SPAM_KEYWORDS = {
        # Finance scams
        "crypto", "investment", "earn money", "profit", "trading",
        "forex", "bitcoin", "passive income", "financial freedom",
        "make money", "100x", "roi",
        # Engagement bait
        "giveaway", "dm me", "link in bio", "follow back",
        "f4f", "follow for follow", "l4l",
        # Adult/scam
        "onlyfans", "18+", "exclusive content", "click the link",
        # Generic spam
        "work from home", "limited offer", "guaranteed",
    }

    matched_keywords = [kw for kw in SPAM_KEYWORDS if kw in bio]
    if len(matched_keywords) >= 3:
        flag("HEAVY_SPAM_BIO", f"Multiple spam keywords in bio: {', '.join(matched_keywords)}", points=3)
    elif matched_keywords:
        flag("SPAM_BIO", f"Spam keyword(s) in bio: {', '.join(matched_keywords)}")

    # Excessive links or emojis (common in spammy bios)
    emoji_count = sum(1 for ch in profile.get("bio", "") if ord(ch) > 0x1F300)
    if emoji_count > 10:
        flag("EMOJI_SPAM_BIO", f"Excessive emoji usage in bio ({emoji_count} emojis)")

    # ================================================================
    # SECTION 4 — Username Patterns
    # ================================================================

    import re

    # Long random digit sequences (e.g., john_4859203)
    if re.search(r'\d{5,}', username):
        flag("RANDOM_DIGITS_USERNAME", "Username contains long numeric sequence (bot pattern)")

    # Excessive underscores or dots
    if username.count("_") + username.count(".") >= 3:
        flag("PUNCTUATION_USERNAME", "Username has excessive underscores/dots (bot pattern)")

    # Very short username (1–2 chars is suspicious if not verified)
    if len(username) <= 2 and not is_verified:
        flag("SUSPICIOUSLY_SHORT_USERNAME", "Username is unusually short")

    # ================================================================
    # SECTION 5 — Account Age
    # ================================================================

    if account_age is not None:
        if account_age < 7:
            flag("VERY_NEW_ACCOUNT", "Account created less than 7 days ago", points=2)
        elif account_age < 30:
            flag("NEW_ACCOUNT", "Account is less than 30 days old")

    # ================================================================
    # SECTION 6 — Profile Completeness
    # ================================================================

    if not has_pic:
        flag("NO_PROFILE_PIC", "No profile picture set", points=1)

    if highlights == 0 and posts > 10:
        flag("NO_HIGHLIGHTS", "Active poster but no story highlights (minor signal)")

    # ================================================================
    # SECTION 7 — Verified Discount
    # ================================================================

    if is_verified:
        score = max(0, score - 3)   # verified accounts get score relief
        reasons.append("ℹ️  Verified account — score reduced by 3")

    # ================================================================
    # Final Risk Classification
    # ================================================================

    if score >= 7:
        risk = "CRITICAL RISK"
    elif score >= 4:
        risk = "HIGH RISK"
    elif score >= 2:
        risk = "MEDIUM RISK"
    elif score == 1:
        risk = "LOW RISK"
    else:
        risk = "SAFE"

    summary_map = {
        "CRITICAL RISK": "This account shows strong indicators of spam, bot, or scam activity.",
        "HIGH RISK":     "This account has several suspicious signals and should be reviewed.",
        "MEDIUM RISK":   "Some suspicious patterns detected; may be a new or inactive account.",
        "LOW RISK":      "Minor concerns only; likely a real but inactive or new account.",
        "SAFE":          "No significant risk indicators detected.",
    }

    return {
        "risk":    risk,
        "score":   score,
        "flags":   flags,
        "reasons": reasons,
        "summary": summary_map[risk],
    }