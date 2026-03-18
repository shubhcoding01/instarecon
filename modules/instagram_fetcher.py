import instaloader
import time
import random

# Create a global loader instance
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=False,
    download_video_thumbnails=False,
    download_geotags=False,
    save_metadata=False
)


def fetch_profile(username: str, max_retries: int = 3):
    """
    Fetch Instagram profile data

    Args:
        username (str): Instagram username
        max_retries (int): retry attempts if request fails

    Returns:
        dict or None
    """

    for attempt in range(max_retries):
        try:
            profile = instaloader.Profile.from_username(L.context, username)

            data = {
                "username": username,
                "full_name": profile.full_name,
                "followers": profile.followers,
                "following": profile.followees,
                "posts": profile.mediacount,
                "bio": profile.biography,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified,
                "profile_pic_url": profile.profile_pic_url
            }

            return data

        except instaloader.exceptions.ProfileNotExistsException:
            print(f"[ERROR] {username} → Profile does not exist")
            return None

        except instaloader.exceptions.ConnectionException:
            print(f"[ERROR] {username} → Connection issue. Retrying...")

        except Exception as e:
            print(f"[ERROR] {username} → {str(e)}")

        # Retry delay (important to avoid blocking)
        sleep_time = random.uniform(2, 5)
        time.sleep(sleep_time)

    print(f"[FAILED] {username} → Max retries reached")
    return None


def fetch_bulk_profiles(usernames: list):
    """
    Fetch multiple profiles with delay to avoid blocking

    Args:
        usernames (list)

    Returns:
        list of profile data
    """

    results = []

    print("\n[INFO] Starting profile scan...\n")

    for i, username in enumerate(usernames, start=1):
        print(f"[{i}/{len(usernames)}] Fetching → {username}")

        profile_data = fetch_profile(username)

        if profile_data:
            results.append(profile_data)

        # Delay between requests (VERY IMPORTANT)
        time.sleep(random.uniform(3, 7))

    print("\n[INFO] Scanning completed.\n")

    return results