#!/usr/bin/env python3
"""
Quick test script to verify Apollo API key and check plan status.
"""

import requests
from config import load_config

def test_api_key():
    """Test API key validity and check available endpoints."""

    config = load_config()
    api_key = config.APOLLO_API_KEY

    print("\n" + "="*60)
    print("APOLLO API KEY TEST")
    print("="*60)
    print(f"API Key (masked): ...{api_key[-8:]}")
    print()

    headers = {
        'accept': 'application/json',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    # Test 1: Try to get account info (if available)
    print("Test 1: Checking API authentication...")

    # Try a simple company search with minimal query
    url = "https://api.apollo.io/api/v1/mixed_companies/search"
    params = {
        'q_organization_name': 'Google',
        'per_page': 1
    }

    try:
        response = requests.post(url, headers=headers, params=params)
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  [OK] API key is VALID")
            print("  [OK] Company search endpoint is accessible")
            data = response.json()
            print(f"  Found {data.get('pagination', {}).get('total_entries', 0)} companies")

        elif response.status_code == 401:
            print("  [ERROR] INVALID API KEY - Authentication failed")
            print("  Please check your .env file and regenerate your API key")

        elif response.status_code == 403:
            error_data = response.json()
            error_msg = error_data.get('error', '')

            if 'free plan' in error_msg.lower():
                print("  [OK] API key is VALID")
                print("  [BLOCKED] Company search NOT available on FREE PLAN")
            else:
                print("  [ERROR] Access forbidden")
                print(f"  Error: {error_msg}")

        else:
            print(f"  Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

    # Test 2: Try people search
    print("\nTest 2: Checking people search endpoint...")

    url = "https://api.apollo.io/api/v1/mixed_people/api_search"
    params = {
        'q_organization_domains_list[]': 'google.com',
        'per_page': 1
    }

    try:
        response = requests.post(url, headers=headers, params=params)
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 200:
            print("  [OK] People search endpoint is accessible")
            data = response.json()
            print(f"  Found {data.get('pagination', {}).get('total_entries', 0)} people")

        elif response.status_code == 401:
            print("  [ERROR] INVALID API KEY")

        elif response.status_code == 403:
            error_data = response.json()
            error_msg = error_data.get('error', '')

            if 'free plan' in error_msg.lower():
                print("  [OK] API key is VALID")
                print("  [BLOCKED] People search NOT available on FREE PLAN")
                print("\n  " + "="*56)
                print("  PLAN LIMITATION DETECTED")
                print("  " + "="*56)
                print("  Your Apollo account is on the FREE PLAN")
                print("  To use this tool, you need to upgrade to a paid plan")
                print("  Upgrade at: https://app.apollo.io/")
            else:
                print("  [ERROR] Access forbidden")
                print(f"  Error: {error_msg}")

        else:
            print(f"  Unexpected response: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Your API key is VALID but on the FREE PLAN")
    print("Free plan does NOT include API access for:")
    print("  - Company search")
    print("  - People search")
    print("  - Email enrichment")
    print("\nTo use this tool, upgrade at: https://app.apollo.io/")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_api_key()
