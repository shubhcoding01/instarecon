import os

def load_usernames(file_path: str):
    """
    Load usernames from a file.

    Args:
        file_path (str): Path to usernames file

    Returns:
        list: Cleaned list of usernames
    """

    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return []

    usernames = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                username = line.strip()

                # Skip empty lines
                if not username:
                    continue

                # Remove @ if user entered @username
                if username.startswith("@"):
                    username = username[1:]

                usernames.append(username)

        # Remove duplicates
        usernames = list(set(usernames))

        return usernames

    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")
        return []


def validate_username(username: str):
    """
    Validate Instagram username format.

    Rules:
    - Only letters, numbers, underscores, periods
    - Length between 1 and 30

    Returns:
        bool
    """

    if not username:
        return False

    if len(username) > 30:
        return False

    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._"

    for char in username:
        if char not in allowed_chars:
            return False

    return True


def filter_valid_usernames(usernames: list):
    """
    Filter only valid usernames

    Args:
        usernames (list)

    Returns:
        list
    """

    valid = []
    invalid = []

    for username in usernames:
        if validate_username(username):
            valid.append(username)
        else:
            invalid.append(username)

    if invalid:
        print("\n[WARNING] Invalid usernames skipped:")
        for u in invalid:
            print(f" - {u}")

    return valid


def load_and_validate(file_path: str):
    """
    Combined function:
    Load + validate usernames

    Returns:
        list of valid usernames
    """

    usernames = load_usernames(file_path)

    if not usernames:
        print("[INFO] No usernames found.")
        return []

    usernames = filter_valid_usernames(usernames)

    print(f"[INFO] Loaded {len(usernames)} valid usernames.")

    return usernames