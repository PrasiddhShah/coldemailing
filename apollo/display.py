from typing import List, Dict, Any, Optional
from tabulate import tabulate


def show_contact_preview(contacts: List[Dict[str, Any]], max_display: int = 50) -> None:
    """
    Display preview table of contacts.

    Args:
        contacts: List of contact dictionaries
        max_display: Maximum number of contacts to display in table
    """
    if not contacts:
        print("\nNo contacts found.")
        return

    table_data = []
    for idx, contact in enumerate(contacts[:max_display], start=1):
        location = contact.get('location', '')
        if len(location) > 25:
            location = location[:22] + '...'

        title = contact.get('title', '')
        if len(title) > 40:
            title = title[:37] + '...'

        table_data.append([
            idx,
            contact.get('name', 'N/A'),
            title,
            location
        ])

    headers = ['#', 'Name', 'Title', 'Location']

    print("\n" + tabulate(table_data, headers=headers, tablefmt='grid'))

    if len(contacts) > max_display:
        print(f"\n... and {len(contacts) - max_display} more contacts")


def show_summary(
    total: int,
    company: str,
    roles: List[str],
    enriched: bool = False
) -> None:
    """
    Print summary of search results.

    Args:
        total: Total number of contacts found
        company: Company name
        roles: List of target roles
        enriched: Whether contacts have been enriched with emails
    """
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Company: {company}")
    print(f"Total contacts found: {total}")
    print(f"Target roles: {', '.join(roles)}")
    if enriched:
        print("Status: Emails enriched")
    else:
        print("Status: Basic data only (no emails yet)")
    print(f"{'='*60}\n")


def confirm_enrichment(count: int, estimated_credits: Optional[int] = None) -> bool:
    """
    Ask user to confirm email enrichment.

    Args:
        count: Number of contacts to enrich
        estimated_credits: Estimated credits to be consumed

    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n{'='*60}")
    print("EMAIL ENRICHMENT CONFIRMATION")
    print(f"{'='*60}")
    print(f"Contacts to enrich: {count}")

    if estimated_credits:
        print(f"Estimated credit cost: ~{estimated_credits} credits")
    else:
        print(f"Estimated credit cost: ~{count} credits")

    print("\nThis will consume Apollo API credits.")
    print(f"{'='*60}")

    while True:
        response = input("\nProceed with email enrichment? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def show_progress(current: int, total: int, message: str = "Processing") -> None:
    """
    Show simple progress indicator.

    Args:
        current: Current progress count
        total: Total items
        message: Progress message
    """
    percentage = (current / total) * 100 if total > 0 else 0
    bar_length = 40
    filled_length = int(bar_length * current // total) if total > 0 else 0

    bar = '#' * filled_length + '-' * (bar_length - filled_length)

    print(f'\r{message}: |{bar}| {current}/{total} ({percentage:.1f}%)', end='', flush=True)

    if current >= total:
        print()


def show_enrichment_progress(contacts_enriched: int, total_contacts: int) -> None:
    """
    Show progress during email enrichment.

    Args:
        contacts_enriched: Number of contacts enriched so far
        total_contacts: Total contacts to enrich
    """
    show_progress(contacts_enriched, total_contacts, "Enriching emails")


def print_error(message: str) -> None:
    """
    Print error message with formatting.

    Args:
        message: Error message to display
    """
    print(f"\nERROR: {message}\n")


def print_warning(message: str) -> None:
    """
    Print warning message with formatting.

    Args:
        message: Warning message to display
    """
    print(f"\nWARNING: {message}\n")


def print_success(message: str) -> None:
    """
    Print success message with formatting.

    Args:
        message: Success message to display
    """
    print(f"\nSUCCESS: {message}\n")


def print_info(message: str) -> None:
    """
    Print info message with formatting.

    Args:
        message: Info message to display
    """
    print(f"\nINFO: {message}\n")
