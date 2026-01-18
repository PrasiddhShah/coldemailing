"""Database package for Apollo Cold Emailer."""
from .database import get_db, get_db_session, init_db, test_connection, engine, Base, IS_SUPABASE
from .models import Company, Contact, Search, EmailDraft, EmailHistory, Tag, ContactTag
from .db_operations import (
    upsert_company, upsert_contact, create_search,
    get_company_by_domain, get_contacts_by_company,
    get_unenriched_contacts, search_contacts,
    create_email_history, check_email_sent,
    get_company_stats, get_all_companies,
    export_contacts_to_dict
)

__all__ = [
    # Database
    'get_db', 'get_db_session', 'init_db', 'test_connection', 'engine', 'Base', 'IS_SUPABASE',
    # Models
    'Company', 'Contact', 'Search', 'EmailDraft', 'EmailHistory', 'Tag', 'ContactTag',
    # Operations
    'upsert_company', 'upsert_contact', 'create_search',
    'get_company_by_domain', 'get_contacts_by_company',
    'get_unenriched_contacts', 'search_contacts',
    'create_email_history', 'check_email_sent',
    'get_company_stats', 'get_all_companies',
    'export_contacts_to_dict'
]
