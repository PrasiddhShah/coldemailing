import time
from typing import List, Dict, Optional, Any
from config import Config


def search_contacts(
    company_domain: str,
    target_roles: List[str],
    client,
    max_results: Optional[int] = None,
    config: Optional[Config] = None,
    company_info: Optional[Dict] = None
) -> List[Dict[str, Any]]:
    """
    Search for people at target company filtered by roles (FREE operation).

    Args:
        company_domain: Company domain (e.g., 'google.com')
        target_roles: List of role types to search for
        client: ApolloClient instance
        max_results: Maximum number of contacts to return
        config: Config instance (optional)
        company_info: Company info dict with organization_id (optional)

    Returns:
        List of contact dictionaries (without emails yet)
    """
    if config is None:
        from config import load_config
        config = load_config()

    filters = map_roles_to_filters(target_roles, config)

    print(f"Searching for {', '.join(target_roles)} at {company_domain}...")

    per_page = min(config.DEFAULT_PER_PAGE, 100)
    page = 1
    all_contacts = []

    while True:
        try:
            # Use organization_ids if available (more reliable than domains)
            search_params = {
                'person_titles': filters['person_titles'],
                'person_seniorities': filters['person_seniorities'],
                'include_similar_titles': True,
                'per_page': per_page,
                'page': page
            }

            if company_info and company_info.get('organization_id'):
                search_params['organization_ids'] = [company_info['organization_id']]
            else:
                search_params['organization_domains'] = [company_domain]

            response = client.search_people(**search_params)

            people = response.get('people', [])
            if not people:
                break

            for person in people:
                contact = extract_contact_data(person)
                all_contacts.append(contact)

            pagination = response.get('pagination', {})
            total_pages = pagination.get('total_pages', 1)

            print(f"  Found {len(all_contacts)} contacts so far...")

            if max_results and len(all_contacts) >= max_results:
                all_contacts = all_contacts[:max_results]
                break

            if page >= total_pages or page >= 10:  # Limit to 10 pages max
                break

            page += 1
            time.sleep(0.3)

        except Exception as e:
            print(f"Warning: Error during search on page {page}: {str(e)}")
            break

    return all_contacts


def map_roles_to_filters(roles: List[str], config: Config) -> Dict[str, List[str]]:
    """
    Convert user-friendly roles to Apollo API filters.

    Args:
        roles: List of role types (e.g., ['recruiter', 'engineering_manager'])
        config: Config instance with TITLE_MAPPINGS

    Returns:
        Dictionary with 'person_titles' and 'person_seniorities' lists
    """
    all_titles = []
    all_seniorities = set()

    for role in roles:
        role_key = role.lower()

        if role_key in config.TITLE_MAPPINGS:
            role_config = config.TITLE_MAPPINGS[role_key]
            all_titles.extend(role_config.get('titles', []))
            all_seniorities.update(role_config.get('seniorities', []))

    return {
        'person_titles': all_titles,
        'person_seniorities': list(all_seniorities) if all_seniorities else None
    }


def extract_contact_data(person: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant contact information from Apollo API person object.

    Args:
        person: Person dictionary from Apollo API

    Returns:
        Cleaned contact dictionary
    """
    # Handle obfuscated data from search results
    first_name = person.get('first_name', '')
    last_name = person.get('last_name', person.get('last_name_obfuscated', ''))

    # Build full name from available parts
    name_parts = [first_name, last_name] if last_name else [first_name]
    name = ' '.join(filter(None, name_parts)) or person.get('name', '')

    # Get company name from organization object or direct field
    org = person.get('organization', {})
    company = org.get('name') if isinstance(org, dict) else person.get('organization_name', '')

    contact = {
        'id': person.get('id'),
        'name': name,
        'first_name': first_name,
        'last_name': last_name,
        'title': person.get('title', ''),
        'company': company,
        'location': extract_location(person),
        'linkedin_url': person.get('linkedin_url', ''),
        'seniority': person.get('seniority', ''),
        'departments': person.get('departments', []),
        'email': person.get('email'),
        'phone': extract_phone(person),
        'photo_url': person.get('photo_url', ''),
        'headline': person.get('headline', ''),
        'has_email': person.get('has_email', False),
        'has_phone': person.get('has_direct_phone') == 'Yes'
    }

    return contact


def extract_location(person: Dict[str, Any]) -> str:
    """
    Extract location information from person data.

    Args:
        person: Person dictionary

    Returns:
        Location string
    """
    city = person.get('city', '')
    state = person.get('state', '')
    country = person.get('country', '')

    location_parts = []
    if city:
        location_parts.append(city)
    if state:
        location_parts.append(state)
    elif country and country != city:
        location_parts.append(country)

    return ', '.join(location_parts) if location_parts else ''


def extract_phone(person: Dict[str, Any]) -> Optional[str]:
    """
    Extract phone number from person data.

    Args:
        person: Person dictionary

    Returns:
        Phone number string or None
    """
    phone_numbers = person.get('phone_numbers', [])
    if phone_numbers and isinstance(phone_numbers, list):
        return phone_numbers[0].get('sanitized_number') or phone_numbers[0].get('raw_number')

    return person.get('phone_number')


def paginate_results(
    client,
    initial_params: Dict[str, Any],
    max_results: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch all pages of results up to max_results.

    Args:
        client: ApolloClient instance
        initial_params: Initial search parameters
        max_results: Maximum number of results to fetch

    Returns:
        List of all contacts across pages
    """
    all_contacts = []
    page = 1

    while True:
        params = {**initial_params, 'page': page}
        response = client.search_people(**params)

        people = response.get('people', [])
        for person in people:
            all_contacts.append(extract_contact_data(person))

        pagination = response.get('pagination', {})
        total_pages = pagination.get('total_pages', 1)

        if max_results and len(all_contacts) >= max_results:
            return all_contacts[:max_results]

        if page >= total_pages:
            break

        page += 1
        time.sleep(0.5)

    return all_contacts
