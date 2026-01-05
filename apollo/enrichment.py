import time
from typing import List, Dict, Any
from apollo.display import show_enrichment_progress, print_warning


def enrich_contacts(
    contacts: List[Dict[str, Any]],
    client,
    show_progress: bool = True,
    batch_delay: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Enrich contact data with emails and phone numbers (COSTS CREDITS).

    Args:
        contacts: List of contact dictionaries
        client: ApolloClient instance
        show_progress: Whether to show progress indicator
        batch_delay: Delay between requests in seconds

    Returns:
        List of enriched contacts with email/phone data
    """
    enriched_contacts = []
    total = len(contacts)

    for idx, contact in enumerate(contacts, start=1):
        try:
            enriched_data = enrich_person(contact, client)

            contact_with_email = {**contact, **enriched_data}
            enriched_contacts.append(contact_with_email)

            if show_progress:
                show_enrichment_progress(idx, total)

            if idx < total:
                time.sleep(batch_delay)

        except Exception as e:
            print_warning(f"Failed to enrich contact {contact.get('name', 'Unknown')}: {str(e)}")

            enriched_contacts.append(contact)

            if show_progress:
                show_enrichment_progress(idx, total)

    return enriched_contacts


def enrich_person(contact: Dict[str, Any], client) -> Dict[str, Any]:
    """
    Enrich a single person's data with email and phone.

    Args:
        contact: Contact dictionary
        client: ApolloClient instance

    Returns:
        Dictionary with enriched data (email, phone, etc.)
    """
    person_id = contact.get('id')
    first_name = contact.get('first_name')
    last_name = contact.get('last_name')
    organization_name = contact.get('company')

    response = client.enrich_person(
        person_id=person_id,
        first_name=first_name,
        last_name=last_name,
        organization_name=organization_name,
        reveal_personal_emails=True,
        reveal_phone_number=False  # Requires webhook_url
    )

    return extract_email_data(response)


def extract_email_data(enrichment_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse enrichment API response and extract email/phone data.

    Args:
        enrichment_response: API response from people/match endpoint

    Returns:
        Dictionary with extracted data
    """
    person = enrichment_response.get('person', {})

    email = person.get('email')

    personal_emails = person.get('personal_emails', [])
    personal_email = personal_emails[0] if personal_emails else None

    phone_numbers = person.get('phone_numbers', [])
    phone = None
    if phone_numbers:
        phone = phone_numbers[0].get('sanitized_number') or phone_numbers[0].get('raw_number')

    linkedin_url = person.get('linkedin_url')

    enriched_data = {}

    if email:
        enriched_data['email'] = email
    if personal_email:
        enriched_data['personal_email'] = personal_email
    if phone:
        enriched_data['phone'] = phone
    if linkedin_url:
        enriched_data['linkedin_url'] = linkedin_url

    if person.get('headline'):
        enriched_data['headline'] = person.get('headline')
    if person.get('photo_url'):
        enriched_data['photo_url'] = person.get('photo_url')

    return enriched_data


def batch_enrich(
    contacts: List[Dict[str, Any]],
    client,
    batch_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Process enrichment in batches to manage rate limits.

    Note: Apollo's bulk enrichment endpoint may not be available for all plans.
    This function currently processes one at a time with batching for future use.

    Args:
        contacts: List of contact dictionaries
        client: ApolloClient instance
        batch_size: Number of contacts per batch

    Returns:
        List of enriched contacts
    """
    enriched_contacts = []
    total = len(contacts)

    for i in range(0, total, batch_size):
        batch = contacts[i:i + batch_size]

        for contact in batch:
            try:
                enriched_data = enrich_person(contact, client)
                enriched_contacts.append({**contact, **enriched_data})
            except Exception as e:
                print_warning(f"Failed to enrich {contact.get('name')}: {str(e)}")
                enriched_contacts.append(contact)

        if i + batch_size < total:
            time.sleep(1)

    return enriched_contacts
