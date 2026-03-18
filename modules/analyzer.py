def analyze(profile: dict):
    """
    Analyze Instagram profile and assign risk level

    Args:
        profile (dict)

    Returns:
        dict → { risk_level, score, reasons }
    """

    score = 0
    reasons = []

    followers = profile.get("followers", 0)
    following = profile.get("following", 0)
    posts = profile.get("posts", 0)
    bio = profile.get("bio", "").lower()

    # -------------------------------
    # Rule 1: Low followers
    # -------------------------------
    if followers < 50:
        score += 1
        reasons.append("Very low followers")

    # -------------------------------
    # Rule 2: High following
    # -------------------------------
    if following > 1000:
        score += 1
        reasons.append("Following too many users")

    # -------------------------------
    # Rule 3: Follower/Following ratio
    # -------------------------------
    if following > 0:
        ratio = followers / following
        if ratio < 0.1:
            score += 1
            reasons.append("Poor follower/following ratio")

    # -------------------------------
    # Rule 4: Very low posts
    # -------------------------------
    if posts < 3:
        score += 1
        reasons.append("Very few posts")

    # -------------------------------
    # Rule 5: Spam keywords in bio
    # -------------------------------
    spam_keywords = [
        "crypto", "investment", "earn money",
        "profit", "trading", "forex",
        "giveaway", "dm me", "link in bio"
    ]

    for keyword in spam_keywords:
        if keyword in bio:
            score += 1
            reasons.append(f"Spam keyword in bio: {keyword}")
            break

    # -------------------------------
    # Rule 6: Empty bio
    # -------------------------------
    if bio.strip() == "":
        score += 1
        reasons.append("Empty bio")

    # -------------------------------
    # Final Risk Level
    # -------------------------------
    if score >= 4:
        risk = "HIGH RISK"
    elif score >= 2:
        risk = "MEDIUM RISK"
    else:
        risk = "SAFE"

    return {
        "risk": risk,
        "score": score,
        "reasons": reasons
    }