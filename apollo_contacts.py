#!/usr/bin/env python3
"""
Apollo Cold Emailing Tool
Find recruiter, manager, and executive contacts at target companies.
"""

import argparse
import sys
from config import load_config, validate_api_key, mask_api_key
from apollo.api_client import ApolloClient, ApolloAPIError, AuthenticationError
from apollo.company_resolver import resolve_company_input
from apollo.contact_search import search_contacts
from apollo.enrichment import enrich_contacts
from apollo.export import export_to_json
from apollo.display import (
    show_contact_preview,
    show_summary,
    confirm_enrichment,
    print_error,
    print_success,
    print_info,
    print_warning
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Apollo API Cold Email Contact Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Search for recruiters at Google
  python apollo_contacts.py "Google" --roles recruiter

  # Search for engineering managers and CTOs at a URL
  python apollo_contacts.py "https://www.stripe.com" --roles engineering_manager cto

  # Search by domain with output file
  python apollo_contacts.py "shopify.com" --roles recruiter --output shopify_recruiters.json

  # Limit results to 20 contacts
  python apollo_contacts.py "Meta" --roles engineering_manager --limit 20

  # Skip email enrichment (free search only)
  python apollo_contacts.py "Apple" --roles cto --skip-enrichment
        '''
    )

    parser.add_argument(
        'company',
        help='Company name, URL, or domain (e.g., "Google", "https://stripe.com", "shopify.com")'
    )

    parser.add_argument(
        '--roles', '-r',
        nargs='+',
        choices=['recruiter', 'engineering_manager', 'cto', 'all'],
        default=['recruiter'],
        help='Target roles to search for (default: recruiter)'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output JSON filename (default: auto-generated with timestamp)'
    )

    parser.add_argument(
        '--output-dir',
        default='outputs',
        help='Output directory for JSON files (default: outputs)'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Maximum number of contacts to find'
    )

    parser.add_argument(
        '--skip-enrichment',
        action='store_true',
        help='Skip email enrichment - export basic data only (free, no credits used)'
    )

    parser.add_argument(
        '--auto-confirm', '-y',
        action='store_true',
        help='Skip confirmation prompt for enrichment'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output with debug information'
    )

    return parser.parse_args()


def main():
    """Main execution flow."""
    args = parse_args()

    try:
        print("\n" + "="*60)
        print("APOLLO COLD EMAILING TOOL")
        print("="*60 + "\n")

        config = load_config()

        validate_api_key(config.APOLLO_API_KEY)

        if args.verbose:
            print(f"API Key: {mask_api_key(config.APOLLO_API_KEY)}")
            print(f"API Base URL: {config.API_BASE_URL}\n")

        client = ApolloClient(config.APOLLO_API_KEY, config.API_BASE_URL)

        print(f"Resolving company: {args.company}")
        company_info = resolve_company_input(args.company, client)
        print(f"Found: {company_info['name']} ({company_info['domain']})\n")

        if 'all' in args.roles:
            roles = ['recruiter', 'engineering_manager', 'cto']
        else:
            roles = args.roles

        print(f"Searching for {', '.join(roles)} contacts...")
        contacts = search_contacts(
            company_domain=company_info['domain'],
            target_roles=roles,
            client=client,
            max_results=args.limit,
            config=config,
            company_info=company_info
        )

        if not contacts:
            print_warning(f"No contacts found matching criteria at {company_info['name']}.")
            print_info("Try:")
            print("  - Using different roles (--roles recruiter engineering_manager cto)")
            print("  - Removing the --limit flag to get all results")
            print("  - Checking if the company domain is correct")
            return 1

        print(f"\nFound {len(contacts)} contacts")

        show_contact_preview(contacts)

        show_summary(
            total=len(contacts),
            company=company_info['name'],
            roles=roles,
            enriched=False
        )

        enriched = False
        if not args.skip_enrichment:
            if args.auto_confirm:
                proceed = True
                print_info("Auto-confirming email enrichment (--auto-confirm flag set)")
            else:
                proceed = confirm_enrichment(len(contacts))

            if proceed:
                print("\nEnriching contacts with emails (this will consume credits)...")
                contacts = enrich_contacts(contacts, client, show_progress=True)
                enriched = True
                print("\nEmail enrichment complete")
            else:
                print_info("Skipping email enrichment. Exporting basic contact data only.")
        else:
            print_info("Email enrichment skipped (--skip-enrichment flag set)")

        print("\nExporting to JSON...")
        output_path = export_to_json(
            contacts=contacts,
            output_path=args.output,
            output_dir=args.output_dir,
            company_name=company_info['name'],
            company_domain=company_info['domain'],
            target_roles=roles,
            enriched=enriched
        )

        print_success(f"Successfully exported {len(contacts)} contacts to: {output_path}")

        if enriched:
            email_count = sum(1 for c in contacts if c.get('email'))
            print(f"  - Contacts with emails: {email_count}/{len(contacts)}")

        print("\n" + "="*60)
        print("DONE")
        print("="*60 + "\n")

        return 0

    except AuthenticationError as e:
        print_error(str(e))
        print_info("Please check your .env file and ensure APOLLO_API_KEY is set correctly.")
        return 1

    except ValueError as e:
        print_error(str(e))
        return 1

    except ApolloAPIError as e:
        print_error(f"Apollo API error: {str(e)}")
        return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130

    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
