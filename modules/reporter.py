import csv
import json
import os


def ensure_data_folder():
    """
    Ensure 'data' folder exists
    """
    if not os.path.exists("data"):
        os.makedirs("data")


# -----------------------------------
# CSV REPORT
# -----------------------------------
def save_csv(results, filename="data/results.csv"):
    """
    Save results to CSV file
    """

    ensure_data_folder()

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Username",
            "Followers",
            "Following",
            "Posts",
            "Risk",
            "Score",
            "Reasons"
        ])

        # Data rows
        for r in results:
            writer.writerow([
                r["username"],
                r["followers"],
                r["following"],
                r["posts"],
                r["risk"],
                r["score"],
                ", ".join(r["reasons"])
            ])

    print(f"[INFO] CSV report saved → {filename}")


# -----------------------------------
# JSON REPORT
# -----------------------------------
def save_json(results, filename="data/results.json"):
    """
    Save results to JSON file
    """

    ensure_data_folder()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"[INFO] JSON report saved → {filename}")


# -----------------------------------
# TXT REPORT (ONLY SUSPICIOUS)
# -----------------------------------
def save_txt_suspicious(results, filename="data/suspicious.txt"):
    """
    Save only HIGH/MEDIUM risk accounts
    """

    ensure_data_folder()

    with open(filename, "w", encoding="utf-8") as f:

        for r in results:
            if r["risk"] in ["HIGH RISK", "MEDIUM RISK"]:
                f.write(f"{r['username']} → {r['risk']}\n")

    print(f"[INFO] Suspicious accounts saved → {filename}")


# -----------------------------------
# MAIN REPORT FUNCTION
# -----------------------------------
def generate_reports(results):
    """
    Generate all reports
    """

    save_csv(results)
    save_json(results)
    save_txt_suspicious(results)