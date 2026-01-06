import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


def export_to_json(
    contacts: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    output_dir: str = 'outputs',
    company_name: Optional[str] = None,
    company_domain: Optional[str] = None,
    target_roles: Optional[List[str]] = None,
    enriched: bool = False
) -> str:
    """
    Save contacts to JSON file.

    Args:
        contacts: List of contact dictionaries
        output_path: Specific output file path (overrides output_dir)
        output_dir: Output directory for JSON files
        company_name: Company name for metadata
        company_domain: Company domain for metadata
        target_roles: List of target roles for metadata
        enriched: Whether contacts have been enriched with emails

    Returns:
        Full path to saved file
    """
    os.makedirs(output_dir, exist_ok=True)

    if output_path:
        if not output_path.endswith('.json'):
            output_path += '.json'
        full_path = output_path
    else:
        filename = generate_filename(company_name or company_domain or 'contacts')
        full_path = os.path.join(output_dir, filename)

    formatted_contacts = [format_contact_data(contact) for contact in contacts]

    export_data = {
        'metadata': {
            'export_date': datetime.utcnow().isoformat() + 'Z',
            'company': company_name or company_domain or 'Unknown',
            'company_domain': company_domain,
            'total_contacts': len(contacts),
            'target_roles': target_roles or [],
            'enriched': enriched
        },
        'contacts': formatted_contacts
    }

    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return full_path


def generate_filename(company_identifier: str, timestamp: bool = True) -> str:
    """
    Generate filename for JSON export.

    Args:
        company_identifier: Company name or domain
        timestamp: Whether to include timestamp in filename

    Returns:
        Filename string (e.g., 'google_contacts_2026-01-05_14-30-45.json')
    """
    safe_name = company_identifier.lower()

    safe_name = safe_name.replace(' ', '_')
    safe_name = safe_name.replace('.', '_')
    safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')

    if timestamp:
        timestamp_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{safe_name}_contacts_{timestamp_str}.json"
    else:
        filename = f"{safe_name}_contacts.json"

    return filename


def format_contact_data(contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and structure contact data for export.

    Args:
        contact: Raw contact dictionary

    Returns:
        Formatted contact dictionary
    """
    formatted = {
        'name': contact.get('name', ''),
        'first_name': contact.get('first_name', ''),
        'last_name': contact.get('last_name', ''),
        'title': contact.get('title', ''),
        'company': contact.get('company', ''),
        'company_domain': contact.get('company_domain', ''),
        'location': contact.get('location', ''),
    }

    if contact.get('email'):
        formatted['email'] = contact['email']

    if contact.get('personal_email'):
        formatted['personal_email'] = contact['personal_email']

    if contact.get('phone'):
        formatted['phone'] = contact['phone']

    if contact.get('linkedin_url'):
        formatted['linkedin_url'] = contact['linkedin_url']

    if contact.get('seniority'):
        formatted['seniority'] = contact['seniority']

    if contact.get('departments'):
        formatted['departments'] = contact['departments']

    if contact.get('headline'):
        formatted['headline'] = contact['headline']

    if contact.get('photo_url'):
        formatted['photo_url'] = contact['photo_url']

    formatted['apollo_id'] = contact.get('id')

    return formatted


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def export_to_csv(
    contacts: List[Dict[str, Any]],
    output_path: str,
    fields: Optional[List[str]] = None
) -> str:
    """
    Export contacts to CSV format (future enhancement).

    Args:
        contacts: List of contact dictionaries
        output_path: Output CSV file path
        fields: List of fields to include

    Returns:
        Path to saved CSV file
    """
    import csv

    if fields is None:
        fields = ['name', 'title', 'company', 'email', 'phone', 'location', 'linkedin_url']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()

        for contact in contacts:
            formatted = format_contact_data(contact)
            writer.writerow({field: formatted.get(field, '') for field in fields})

    return output_path
