from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


# -----------------------------------
# LOGGING FUNCTIONS
# -----------------------------------

def log_info(message: str):
    console.print(f"[blue][INFO][/blue] {message}")


def log_success(message: str):
    console.print(f"[green][SUCCESS][/green] {message}")


def log_warning(message: str):
    console.print(f"[yellow][WARNING][/yellow] {message}")


def log_error(message: str):
    console.print(f"[red][ERROR][/red] {message}")


# -----------------------------------
# FORMAT USERNAME
# -----------------------------------

def clean_username(username: str):
    """
    Remove @ and spaces
    """
    if not username:
        return ""

    username = username.strip()

    if username.startswith("@"):
        username = username[1:]

    return username


# -----------------------------------
# SAFE EXECUTION WRAPPER
# -----------------------------------

def safe_execute(func, *args, **kwargs):
    """
    Safely execute any function
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(f"Error: {str(e)}")
        return None


# -----------------------------------
# DISPLAY RESULTS TABLE
# -----------------------------------

def display_results(results: list):
    """
    Display results in table format
    """

    if not results:
        log_warning("No results to display")
        return

    table = Table(
        title="Instagram Scan Results",
        box=box.ROUNDED
    )

    table.add_column("Username", style="cyan")
    table.add_column("Followers", justify="right")
    table.add_column("Following", justify="right")
    table.add_column("Posts", justify="right")
    table.add_column("Risk", style="bold")
    table.add_column("Score", justify="right")

    for r in results:
        # Color risk
        risk = r["risk"]

        if risk == "HIGH RISK":
            risk_color = "[red]HIGH[/red]"
        elif risk == "MEDIUM RISK":
            risk_color = "[yellow]MEDIUM[/yellow]"
        else:
            risk_color = "[green]SAFE[/green]"

        table.add_row(
            r["username"],
            str(r["followers"]),
            str(r["following"]),
            str(r["posts"]),
            risk_color,
            str(r["score"])
        )

    console.print(table)


# -----------------------------------
# PROGRESS DISPLAY
# -----------------------------------

def show_progress(current, total, username):
    """
    Show simple progress
    """
    console.print(f"[cyan][{current}/{total}][/cyan] Scanning → {username}")


# -----------------------------------
# BANNER (CLI LOOK 🔥)
# -----------------------------------

def show_banner():
    banner = """
██╗███╗   ██╗███████╗████████╗ █████╗ ██████╗ ███████╗ ██████╗ ██████╗ 
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔════╝ ██╔══██╗
██║██╔██╗ ██║███████╗   ██║   ███████║██████╔╝█████╗  ██║  ███╗██████╔╝
██║██║╚██╗██║╚════██║   ██║   ██╔══██║██╔═══╝ ██╔══╝  ██║   ██║██╔═══╝ 
██║██║ ╚████║███████║   ██║   ██║  ██║██║     ███████╗╚██████╔╝██║     
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝     

        InstaRecon - Instagram OSINT Tool
    """

    console.print(f"[magenta]{banner}[/magenta]")