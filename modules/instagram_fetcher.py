# import instaloader
# import time
# import random

# # Create a global loader instance
# L = instaloader.Instaloader(
#     download_pictures=False,
#     download_videos=False,
#     download_video_thumbnails=False,
#     download_geotags=False,
#     save_metadata=False
# )


# def fetch_profile(username: str, max_retries: int = 3):
#     """
#     Fetch Instagram profile data

#     Args:
#         username (str): Instagram username
#         max_retries (int): retry attempts if request fails

#     Returns:
#         dict or None
#     """

#     for attempt in range(max_retries):
#         try:
#             profile = instaloader.Profile.from_username(L.context, username)

#             data = {
#                 "username": username,
#                 "full_name": profile.full_name,
#                 "followers": profile.followers,
#                 "following": profile.followees,
#                 "posts": profile.mediacount,
#                 "bio": profile.biography,
#                 "is_private": profile.is_private,
#                 "is_verified": profile.is_verified,
#                 "profile_pic_url": profile.profile_pic_url
#             }

#             return data

#         except instaloader.exceptions.ProfileNotExistsException:
#             print(f"[ERROR] {username} → Profile does not exist")
#             return None

#         except instaloader.exceptions.ConnectionException:
#             print(f"[ERROR] {username} → Connection issue. Retrying...")

#         except Exception as e:
#             print(f"[ERROR] {username} → {str(e)}")

#         # Retry delay (important to avoid blocking)
#         sleep_time = random.uniform(2, 5)
#         time.sleep(sleep_time)

#     print(f"[FAILED] {username} → Max retries reached")
#     return None


# def fetch_bulk_profiles(usernames: list):
#     """
#     Fetch multiple profiles with delay to avoid blocking

#     Args:
#         usernames (list)

#     Returns:
#         list of profile data
#     """

#     results = []

#     print("\n[INFO] Starting profile scan...\n")

#     for i, username in enumerate(usernames, start=1):
#         print(f"[{i}/{len(usernames)}] Fetching → {username}")

#         profile_data = fetch_profile(username)

#         if profile_data:
#             results.append(profile_data)

#         # Delay between requests (VERY IMPORTANT)
#         time.sleep(random.uniform(3, 7))

#     print("\n[INFO] Scanning completed.\n")

#     return results


import instaloader
import time
import random
import logging
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("instafetch")


# ──────────────────────────────────────────────
# Profile Data Model
# ──────────────────────────────────────────────
@dataclass
class ProfileData:
    username:           str
    full_name:          str
    followers:          int
    following:          int
    posts:              int
    bio:                str
    is_private:         bool
    is_verified:        bool
    profile_pic_url:    str
    profile_pic:        bool        # True if pic exists
    highlights:         int         # story highlight count
    account_age_days:   Optional[int]
    avg_likes:          Optional[float]
    avg_comments:       Optional[float]
    external_url:       Optional[str]
    fetched_at:         str         # ISO timestamp

    def to_dict(self) -> dict:
        return asdict(self)


# ──────────────────────────────────────────────
# Loader Factory
# ──────────────────────────────────────────────
def create_loader(
    session_file: Optional[str] = None,
    proxy: Optional[str] = None
) -> instaloader.Instaloader:
    """
    Create and configure an Instaloader instance.

    Args:
        session_file: Path to a saved session file (optional but recommended)
        proxy:        HTTP/HTTPS proxy URL e.g. "http://127.0.0.1:8080" (optional)

    Returns:
        instaloader.Instaloader
    """
    kwargs = dict(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        save_metadata=False,
        quiet=True,
        request_timeout=15,
    )

    if proxy:
        kwargs["proxies"] = {"https": proxy, "http": proxy}

    loader = instaloader.Instaloader(**kwargs)

    # Load session (avoids anonymous rate limits)
    if session_file and Path(session_file).exists():
        try:
            loader.load_session_from_file(session_file)
            log.info(f"Session loaded from: {session_file}")
        except Exception as e:
            log.warning(f"Could not load session: {e}")

    return loader


# ──────────────────────────────────────────────
# Engagement Sampler
# ──────────────────────────────────────────────
def _sample_engagement(
    profile: instaloader.Profile,
    sample_size: int = 10
) -> tuple[Optional[float], Optional[float]]:
    """
    Sample recent posts to compute avg likes and avg comments.

    Args:
        profile:     instaloader Profile object
        sample_size: number of recent posts to sample

    Returns:
        (avg_likes, avg_comments) or (None, None) if private/no posts
    """
    if profile.is_private or profile.mediacount == 0:
        return None, None

    likes_list = []
    comments_list = []

    try:
        posts = profile.get_posts()
        for i, post in enumerate(posts):
            if i >= sample_size:
                break
            likes_list.append(post.likes)
            comments_list.append(post.comments)
            time.sleep(random.uniform(1.0, 2.5))   # polite delay per post

    except Exception as e:
        log.warning(f"Engagement sampling failed: {e}")
        return None, None

    if not likes_list:
        return None, None

    avg_likes    = round(sum(likes_list)    / len(likes_list), 2)
    avg_comments = round(sum(comments_list) / len(comments_list), 2)

    return avg_likes, avg_comments


# ──────────────────────────────────────────────
# Single Profile Fetch
# ──────────────────────────────────────────────
def fetch_profile(
    username: str,
    loader: instaloader.Instaloader,
    max_retries: int = 3,
    sample_engagement: bool = False,
    engagement_sample_size: int = 10,
) -> Optional[ProfileData]:
    """
    Fetch a single Instagram profile.

    Args:
        username:               Target username
        loader:                 Instaloader instance
        max_retries:            Retry count on transient failures
        sample_engagement:      Whether to sample post engagement
        engagement_sample_size: How many posts to sample

    Returns:
        ProfileData or None
    """
    username = username.strip().lstrip("@").lower()

    for attempt in range(1, max_retries + 1):
        try:
            log.info(f"Fetching @{username} (attempt {attempt}/{max_retries})")
            profile = instaloader.Profile.from_username(loader.context, username)

            # ── Account age ──────────────────────────────────────────
            account_age_days = None
            try:
                creation_date = profile.profile_pic_url  # placeholder hook
                # NOTE: Instaloader does not expose creation date directly.
                # If you have another data source (e.g. scraped date),
                # compute: (datetime.now(tz=timezone.utc) - creation_date).days
            except Exception:
                pass

            # ── Highlights count ─────────────────────────────────────
            highlights_count = 0
            try:
                highlights_count = sum(1 for _ in profile.get_highlights())
            except Exception:
                pass

            # ── Engagement sampling (optional) ───────────────────────
            avg_likes, avg_comments = (None, None)
            if sample_engagement:
                avg_likes, avg_comments = _sample_engagement(
                    profile, sample_size=engagement_sample_size
                )

            return ProfileData(
                username        = profile.username,
                full_name       = profile.full_name or "",
                followers       = profile.followers,
                following       = profile.followees,
                posts           = profile.mediacount,
                bio             = profile.biography or "",
                is_private      = profile.is_private,
                is_verified     = profile.is_verified,
                profile_pic_url = profile.profile_pic_url or "",
                profile_pic     = bool(profile.profile_pic_url),
                highlights      = highlights_count,
                account_age_days= account_age_days,
                avg_likes       = avg_likes,
                avg_comments    = avg_comments,
                external_url    = profile.external_url or None,
                fetched_at      = datetime.now(tz=timezone.utc).isoformat(),
            )

        # ── Known errors ─────────────────────────────────────────────
        except instaloader.exceptions.ProfileNotExistsException:
            log.error(f"@{username} → Profile does not exist")
            return None

        except instaloader.exceptions.PrivateProfileNotFollowedException:
            log.warning(f"@{username} → Private profile (not followed)")
            # Still return partial data with what we know
            break

        except instaloader.exceptions.LoginRequiredException:
            log.error(f"@{username} → Login required. Load a session file.")
            return None

        except instaloader.exceptions.TooManyRequestsException:
            wait = 60 + random.uniform(10, 30)
            log.warning(f"Rate limited! Waiting {wait:.0f}s before retry...")
            time.sleep(wait)

        except instaloader.exceptions.ConnectionException as e:
            wait = random.uniform(5, 12)
            log.warning(f"@{username} → Connection error: {e}. Retrying in {wait:.1f}s")
            time.sleep(wait)

        except Exception as e:
            log.error(f"@{username} → Unexpected error: {e}")
            time.sleep(random.uniform(3, 7))

    log.error(f"@{username} → All {max_retries} attempts failed")
    return None


# ──────────────────────────────────────────────
# Bulk Fetch
# ──────────────────────────────────────────────
def fetch_bulk_profiles(
    usernames: list[str],
    loader: instaloader.Instaloader,
    delay_range: tuple[float, float] = (4.0, 9.0),
    max_retries: int = 3,
    sample_engagement: bool = False,
    save_to: Optional[str] = None,
) -> list[ProfileData]:
    """
    Fetch multiple profiles with safe delays and optional JSON export.

    Args:
        usernames:         List of Instagram usernames
        loader:            Instaloader instance
        delay_range:       (min_sec, max_sec) delay between requests
        max_retries:       Retry count per profile
        sample_engagement: Whether to sample post engagement
        save_to:           Optional JSON file path to auto-save results

    Returns:
        List of ProfileData
    """
    usernames = list(dict.fromkeys(u.strip().lstrip("@").lower() for u in usernames if u.strip()))

    results:  list[ProfileData] = []
    failed:   list[str]         = []

    total = len(usernames)
    log.info(f"Starting bulk scan — {total} account(s)\n")

    for i, username in enumerate(usernames, start=1):
        log.info(f"[{i}/{total}] → @{username}")

        data = fetch_profile(
            username=username,
            loader=loader,
            max_retries=max_retries,
            sample_engagement=sample_engagement,
        )

        if data:
            results.append(data)
            log.info(
                f"  ✓ {data.followers:,} followers | "
                f"{data.following:,} following | "
                f"{data.posts} posts"
            )
        else:
            failed.append(username)
            log.warning(f"  ✗ Failed to fetch @{username}")

        # Auto-save after every profile (crash-safe)
        if save_to:
            _save_json(results, save_to)

        # Adaptive delay — longer after failures
        min_d, max_d = delay_range
        if not data:
            min_d, max_d = min_d * 1.5, max_d * 2.0

        delay = random.uniform(min_d, max_d)
        log.info(f"  Waiting {delay:.1f}s before next request...\n")
        time.sleep(delay)

    # ── Summary ──────────────────────────────────────────────────────
    log.info("=" * 45)
    log.info(f"Scan complete → {len(results)}/{total} succeeded, {len(failed)} failed")
    if failed:
        log.info(f"Failed accounts: {', '.join(failed)}")
    log.info("=" * 45)

    return results


# ──────────────────────────────────────────────
# JSON Export
# ──────────────────────────────────────────────
def _save_json(profiles: list[ProfileData], path: str) -> None:
    """Save profile list to a JSON file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in profiles], f, indent=2, ensure_ascii=False)
        log.debug(f"Saved {len(profiles)} profiles → {path}")
    except Exception as e:
        log.error(f"Failed to save JSON: {e}")


def export_json(profiles: list[ProfileData], path: str) -> None:
    """Public export helper."""
    _save_json(profiles, path)
    log.info(f"Exported {len(profiles)} profiles → {path}")
    