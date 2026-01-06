"""
Display what job titles are searched for each role type.
"""
from config import Config

def show_titles_for_role(role_name):
    """Show all titles that will be searched for a given role."""
    config = Config()

    if role_name not in config.TITLE_MAPPINGS:
        print(f"❌ Role '{role_name}' not found!")
        print(f"Available roles: {', '.join(config.TITLE_MAPPINGS.keys())}")
        return

    role_config = config.TITLE_MAPPINGS[role_name]
    titles = role_config.get('titles', [])
    seniorities = role_config.get('seniorities', [])

    print(f"\n{'='*60}")
    print(f"Searching for: {role_name.upper()}")
    print(f"{'='*60}\n")

    print(f"Job Titles ({len(titles)} variations):")
    for i, title in enumerate(titles, 1):
        print(f"  {i}. {title}")

    print(f"\nSeniority Levels:")
    for seniority in seniorities:
        print(f"  - {seniority}")

    print(f"\nNOTE: Apollo will also search for SIMILAR titles using fuzzy matching!\n")


def show_all_roles():
    """Show all available roles and their title counts."""
    config = Config()

    print("\n" + "="*60)
    print("AVAILABLE SEARCH ROLES")
    print("="*60 + "\n")

    for role_name, role_config in config.TITLE_MAPPINGS.items():
        title_count = len(role_config.get('titles', []))
        print(f"  - {role_name:20s} -> {title_count:3d} title variations")

    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        role = sys.argv[1].lower()
        show_titles_for_role(role)
    else:
        show_all_roles()
        print("Usage: python show_search_titles.py <role_name>")
        print("Example: python show_search_titles.py recruiter\n")
