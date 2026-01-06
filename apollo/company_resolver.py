import re
from urllib.parse import urlparse
from typing import Dict, Optional
import validators


def resolve_company_input(user_input: str, client) -> Dict[str, str]:
    """
    Convert user input (name/URL/domain) to company information.

    Args:
        user_input: Company name, URL, or domain
        client: ApolloClient instance

    Returns:
        Dictionary with keys: 'domain', 'organization_id', 'name'

    Raises:
        ValueError: If company cannot be resolved
    """
    user_input = user_input.strip()

    if is_url(user_input):
        domain = extract_domain_from_url(user_input)
        return {
            'domain': domain,
            'organization_id': None,
            'name': domain_to_name(domain)
        }

    elif is_domain(user_input):
        domain = user_input.lower()
        # Try to resolve domain to an organization ID for better search results
        # We can reuse the name search or try to find a direct domain lookup
        # For now, let's treat the domain as a name query which Apollo handles reasonably well
        # OR better: use the domain but if we find an org, return its ID.
        
        # We will attempt to find the org details even if we have the domain
        # This ensures we get the 'organization_id' which is better for people search
        org_data = search_company_by_name(domain, client)
        if org_data:
             return org_data
        
        # Fallback if API lookup fails but it looks like a domain
        return {
            'domain': domain,
            'organization_id': None,
            'name': domain_to_name(domain)
        }

    else:
        company_data = search_company_by_name(user_input, client)
        if not company_data:
            raise ValueError(
                f"Could not find company '{user_input}'. "
                "Please try providing the company's domain (e.g., 'google.com') instead."
            )
        return company_data


def extract_domain_from_url(url: str) -> str:
    """
    Parse URL and extract domain.

    Args:
        url: URL string (e.g., 'https://www.google.com/about')

    Returns:
        Domain string (e.g., 'google.com')
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path

    domain = domain.replace('www.', '')

    return domain.lower()


def is_url(text: str) -> bool:
    """
    Check if text looks like a URL.

    Args:
        text: Input text

    Returns:
        True if text appears to be a URL
    """
    return (
        text.startswith(('http://', 'https://')) or
        text.startswith('www.') or
        (validators.url('https://' + text) and '/' in text)
    )


def is_domain(text: str) -> bool:
    """
    Check if text looks like a domain name.

    Args:
        text: Input text

    Returns:
        True if text appears to be a domain
    """
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$'

    if re.match(domain_pattern, text):
        return True

    return '.' in text and not ' ' in text and len(text.split('.')[-1]) >= 2


def domain_to_name(domain: str) -> str:
    """
    Convert domain to a friendly company name.

    Args:
        domain: Domain string (e.g., 'google.com')

    Returns:
        Company name (e.g., 'Google')
    """
    name = domain.split('.')[0]

    name = name.replace('-', ' ').replace('_', ' ')

    return name.title()


def search_company_by_name(name: str, client) -> Optional[Dict[str, str]]:
    """
    Search Apollo API for company by name using organization search.

    Args:
        name: Company name to search for
        client: ApolloClient instance

    Returns:
        Dictionary with company info, or None if not found
    """
    try:
        # Use the organization search endpoint (v1, not mixed_companies)
        endpoint = f"{client.base_url}/v1/organizations/search"
        data = {
            'q_organization_name': name,
            'per_page': 5
        }

        response = client.session.post(endpoint, json=data)
        result = response.json()

        organizations = result.get('organizations', [])

        if not organizations:
            return None

        top_match = organizations[0]

        domain = top_match.get('primary_domain') or top_match.get('website_url', '')
        if domain:
            domain = extract_domain_from_url(domain)

        return {
            'domain': domain,
            'organization_id': top_match.get('id'),
            'name': top_match.get('name', name)
        }

    except Exception as e:
        print(f"Warning: Error searching for company: {str(e)}")
        return None


def validate_domain(domain: str) -> bool:
    """
    Validate domain format.

    Args:
        domain: Domain string

    Returns:
        True if valid domain format
    """
    return is_domain(domain)
