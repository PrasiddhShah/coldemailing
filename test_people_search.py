#!/usr/bin/env python3
"""
Test the actual People Search endpoint used by the tool.
"""

import requests
from config import load_config

def test_people_search():
    """Test the mixed_people/api_search endpoint."""

    config = load_config()
    api_key = config.APOLLO_API_KEY

    print("\n" + "="*60)
    print("TESTING PEOPLE SEARCH API (mixed_people/api_search)")
    print("="*60)
    print(f"API Key (last 8): ...{api_key[-8:]}")
    print()

    headers = {
        'accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    # Test the actual endpoint our tool uses
    url = "https://api.apollo.io/api/v1/mixed_people/api_search"

    # Simple search for recruiters at Google
    params = {
        'q_organization_domains_list[]': 'google.com',
        'person_titles[]': 'Recruiter',
        'per_page': 5
    }

    print("Testing: Search for Recruiters at Google")
    print(f"Endpoint: {url}")
    print()

    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)

        print(f"Status Code: {response.status_code}")
        print()

        if response.status_code == 200:
            print("[SUCCESS] People Search API is WORKING!")
            print()

            data = response.json()
            people = data.get('people', [])
            pagination = data.get('pagination', {})

            print(f"Total Results: {pagination.get('total_entries', 0)}")
            print(f"Results on this page: {len(people)}")
            print()

            if people:
                print("Sample contacts found:")
                print("-" * 60)
                for i, person in enumerate(people[:3], 1):
                    print(f"{i}. {person.get('name', 'N/A')}")
                    print(f"   Title: {person.get('title', 'N/A')}")
                    print(f"   Company: {person.get('organization_name', 'N/A')}")
                    print(f"   Location: {person.get('city', 'N/A')}, {person.get('state', 'N/A')}")
                    print()

                print("="*60)
                print("SUCCESS! Your Apollo API is fully functional!")
                print("="*60)
                print()
                print("You can now use the cold emailing tool:")
                print('  python apollo_contacts.py "google.com" --roles recruiter --limit 10 --skip-enrichment')
                print()

        elif response.status_code == 403:
            error_data = response.json()
            error_msg = error_data.get('error', '')

            print("[BLOCKED] Still getting free plan error:")
            print(f"  {error_msg}")
            print()
            print("The plan upgrade might need time to activate (24-48 hours)")
            print("Or you may need to regenerate your API key")

        else:
            print(f"[ERROR] Unexpected response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {error_data}")
            except:
                print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"[ERROR] {str(e)}")

    print()

if __name__ == '__main__':
    test_people_search()
