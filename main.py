from modules.scanner import load_and_validate
from modules.instagram_fetcher import fetch_bulk_profiles
from modules.analyzer import analyze
from modules.reporter import generate_reports

from utils.helpers import (
    log_info,
    log_success,
    log_error,
    show_banner,
    display_results
)


def main():

    # -----------------------------------
    # Banner
    # -----------------------------------
    show_banner()

    log_info("Starting InstaRecon scan...")

    # -----------------------------------
    # Load usernames
    # -----------------------------------
    usernames = load_and_validate("data/usernames.txt")

    if not usernames:
        log_error("No valid usernames found. Exiting...")
        return

    log_info(f"Total usernames loaded: {len(usernames)}")

    # -----------------------------------
    # Fetch Instagram profiles
    # -----------------------------------
    profiles = fetch_bulk_profiles(usernames)

    if not profiles:
        log_error("No profiles fetched. Exiting...")
        return

    # -----------------------------------
    # Analyze profiles
    # -----------------------------------
    final_results = []

    log_info("Analyzing profiles...\n")

    for profile in profiles:

        result = analyze(profile)

        combined = {
            "username": profile["username"],
            "followers": profile["followers"],
            "following": profile["following"],
            "posts": profile["posts"],
            "risk": result["risk"],
            "score": result["score"],
            "reasons": result["reasons"]
        }

        final_results.append(combined)

    # -----------------------------------
    # Display Results
    # -----------------------------------
    display_results(final_results)

    # -----------------------------------
    # Generate Reports
    # -----------------------------------
    generate_reports(final_results)

    # -----------------------------------
    # Done
    # -----------------------------------
    log_success("Scan completed successfully!")


# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    main()