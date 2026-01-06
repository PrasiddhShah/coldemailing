#!/usr/bin/env python3
"""
Check Apollo account status and plan details.
"""

import requests
from config import load_config

def check_account():
    """Check account status and available endpoints."""

    config = load_config()
    api_key = config.APOLLO_API_KEY

    print("\n" + "="*60)
    print("APOLLO ACCOUNT STATUS CHECK")
    print("="*60)
    print(f"API Key (last 8): ...{api_key[-8:]}")
    print()

    headers = {
        'accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    # Try different endpoints to see which ones work
    endpoints_to_test = [
        {
            'name': 'Email Account Info',
            'url': 'https://api.apollo.io/v1/email_accounts',
            'method': 'GET'
        },
        {
            'name': 'Account Info',
            'url': 'https://api.apollo.io/v1/auth/health',
            'method': 'GET'
        },
        {
            'name': 'People Search (mixed_people)',
            'url': 'https://api.apollo.io/api/v1/mixed_people/search',
            'method': 'POST',
            'data': {'q_keywords': 'engineer', 'per_page': 1}
        },
        {
            'name': 'People Search (people/search)',
            'url': 'https://api.apollo.io/v1/people/search',
            'method': 'POST',
            'data': {'q_keywords': 'engineer', 'per_page': 1}
        },
        {
            'name': 'Organization Search',
            'url': 'https://api.apollo.io/v1/organizations/search',
            'method': 'POST',
            'data': {'q_organization_name': 'Google', 'per_page': 1}
        }
    ]

    print("Testing available endpoints...")
    print("-" * 60)

    for endpoint in endpoints_to_test:
        print(f"\n{endpoint['name']}:")
        print(f"  URL: {endpoint['url']}")

        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers, timeout=10)
            else:
                response = requests.post(
                    endpoint['url'],
                    headers=headers,
                    json=endpoint.get('data', {}),
                    timeout=10
                )

            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                print("  [SUCCESS] Endpoint is accessible!")
                data = response.json()
                # Print some info about the response
                if 'pagination' in data:
                    print(f"  Results: {data['pagination'].get('total_entries', 0)} total")
                elif 'email_accounts' in data:
                    print(f"  Email accounts: {len(data.get('email_accounts', []))}")

            elif response.status_code == 401:
                print("  [ERROR] Invalid API key")

            elif response.status_code == 403:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', '')
                    print(f"  [BLOCKED] {error_msg}")
                except:
                    print("  [BLOCKED] Access forbidden")

            elif response.status_code == 404:
                print("  [NOT FOUND] Endpoint doesn't exist")

            else:
                print(f"  [ERROR] Unexpected status: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"  Message: {error_data.get('error', error_data)}")
                except:
                    print(f"  Response: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("  [ERROR] Request timed out")
        except Exception as e:
            print(f"  [ERROR] {str(e)}")

    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    print()
    print("If you're on the Basic plan but still getting blocked:")
    print()
    print("1. Check your Apollo account at https://app.apollo.io/")
    print("   - Go to Settings > Plans & Billing")
    print("   - Verify you're on Basic/Professional plan")
    print()
    print("2. Regenerate API key:")
    print("   - Go to Settings > Integrations > API")
    print("   - Delete old API key")
    print("   - Create new master API key")
    print("   - Make sure 'Master API Key' is selected (not User API)")
    print()
    print("3. Check API access settings:")
    print("   - Some plans require enabling API access")
    print("   - Contact Apollo support if issue persists")
    print()
    print("4. Verify billing:")
    print("   - Make sure payment went through")
    print("   - Plan might need 24-48 hours to activate")
    print()
    print("="*60 + "\n")

if __name__ == '__main__':
    check_account()
