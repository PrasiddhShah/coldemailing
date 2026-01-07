"""
Database operations for contacts, companies, searches, and emails.
"""
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, or_
from .models import Company, Contact, Search, EmailHistory, EmailDraft
from datetime import datetime


def upsert_company(db: Session, company_data: Dict[str, Any]) -> Company:
    """
    Insert or update company record.

    Args:
        db: Database session
        company_data: Dictionary with company fields

    Returns:
        Company object
    """
    stmt = insert(Company).values(
        domain=company_data['domain'],
        name=company_data['name'],
        organization_id=company_data.get('organization_id'),
        industry=company_data.get('industry'),
        website=company_data.get('website'),
        employee_count=company_data.get('employee_count')
    ).on_conflict_do_update(
        index_elements=['domain'],
        set_={
            'name': company_data['name'],
            'organization_id': company_data.get('organization_id'),
            'updated_at': func.now()
        }
    ).returning(Company)

    result = db.execute(stmt)
    db.commit()
    return result.scalar_one()


def upsert_contact(db: Session, contact_data: Dict[str, Any], company_id: int) -> Contact:
    """
    Insert or update contact record (smart merge).

    Args:
        db: Database session
        contact_data: Dictionary with contact fields
        company_id: ID of the company

    Returns:
        Contact object
    """
    # Prepare update values - only update fields that have new data
    update_values = {'updated_at': func.now()}

    # Update title if provided
    if contact_data.get('title'):
        update_values['title'] = contact_data['title']

    # Update email if new one provided (don't overwrite with None)
    if contact_data.get('email'):
        update_values['email'] = contact_data['email']
        update_values['enriched'] = True
        update_values['enriched_at'] = func.now()
        update_values['has_email'] = True

    # Update phone if provided
    if contact_data.get('phone'):
        update_values['phone'] = contact_data['phone']
        update_values['has_phone'] = True

    # Update other fields
    for field in ['linkedin_url', 'location', 'seniority', 'departments', 'photo_url', 'headline']:
        if contact_data.get(field):
            update_values[field] = contact_data[field]

    stmt = insert(Contact).values(
        company_id=company_id,
        apollo_id=contact_data.get('id'),
        first_name=contact_data['first_name'],
        last_name=contact_data.get('last_name'),
        title=contact_data.get('title'),
        email=contact_data.get('email'),
        phone=contact_data.get('phone'),
        linkedin_url=contact_data.get('linkedin_url'),
        location=contact_data.get('location'),
        seniority=contact_data.get('seniority'),
        departments=contact_data.get('departments'),
        photo_url=contact_data.get('photo_url'),
        headline=contact_data.get('headline'),
        enriched=contact_data.get('email') is not None,
        enriched_at=datetime.now() if contact_data.get('email') else None,
        has_email=contact_data.get('email') is not None,
        has_phone=contact_data.get('phone') is not None
    ).on_conflict_do_update(
        constraint='unique_contact',
        set_=update_values
    ).returning(Contact)

    result = db.execute(stmt)
    db.commit()
    return result.scalar_one()


def create_search(db: Session, company_id: int, roles: List[str],
                  limit: int, total_found: int) -> Search:
    """
    Create a search record.

    Args:
        db: Database session
        company_id: Company ID
        roles: List of roles searched
        limit: Search limit
        total_found: Total contacts found

    Returns:
        Search object
    """
    search = Search(
        company_id=company_id,
        roles=roles,
        search_limit=limit,
        total_found=total_found
    )
    db.add(search)
    db.commit()
    db.refresh(search)
    return search


def get_company_by_domain(db: Session, domain: str) -> Optional[Company]:
    """Get company by domain."""
    return db.query(Company).filter(Company.domain == domain).first()


def get_contacts_by_company(db: Session, company_id: int,
                           enriched_only: bool = False) -> List[Contact]:
    """Get all contacts for a company."""
    query = db.query(Contact).filter(Contact.company_id == company_id)
    if enriched_only:
        query = query.filter(Contact.enriched == True)
    return query.all()


def get_unenriched_contacts(db: Session, company_id: int) -> List[Contact]:
    """Get contacts without emails."""
    return db.query(Contact).filter(
        Contact.company_id == company_id,
        Contact.enriched == False
    ).all()


def search_contacts(db: Session, query: str, limit: int = 50) -> List[Contact]:
    """
    Full-text search contacts by name or title.

    Args:
        db: Database session
        query: Search query
        limit: Max results

    Returns:
        List of matching contacts
    """
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.title.ilike(f'%{query}%')
        )
    ).limit(limit).all()


def create_email_history(db: Session, email_data: Dict[str, Any]) -> EmailHistory:
    """
    Create email history record.

    Args:
        db: Database session
        email_data: Email details

    Returns:
        EmailHistory object
    """
    email_record = EmailHistory(
        contact_id=email_data['contact_id'],
        draft_id=email_data.get('draft_id'),
        to_email=email_data['to_email'],
        subject=email_data['subject'],
        body=email_data['body'],
        status=email_data.get('status', 'sent'),
        resume_attached=email_data.get('resume_attached', False),
        resume_path=email_data.get('resume_path'),
        smtp_provider=email_data.get('smtp_provider'),
        sent_at=datetime.now() if email_data.get('status') == 'sent' else None
    )
    db.add(email_record)
    db.commit()
    db.refresh(email_record)
    return email_record


def check_email_sent(db: Session, contact_id: int) -> bool:
    """Check if contact has been emailed."""
    return db.query(EmailHistory).filter(
        EmailHistory.contact_id == contact_id,
        EmailHistory.status == 'sent'
    ).first() is not None


def get_company_stats(db: Session, company_id: int) -> Dict[str, Any]:
    """
    Get statistics for a company.

    Returns:
        Dictionary with stats
    """
    total_contacts = db.query(func.count(Contact.id)).filter(
        Contact.company_id == company_id
    ).scalar()

    enriched = db.query(func.count(Contact.id)).filter(
        Contact.company_id == company_id,
        Contact.enriched == True
    ).scalar()

    searches = db.query(func.count(Search.id)).filter(
        Search.company_id == company_id
    ).scalar()

    return {
        'total_contacts': total_contacts or 0,
        'enriched_contacts': enriched or 0,
        'total_searches': searches or 0
    }


def get_all_companies(db: Session) -> List[Company]:
    """Get all companies."""
    return db.query(Company).order_by(Company.name).all()


def export_contacts_to_dict(contacts: List[Contact]) -> List[Dict[str, Any]]:
    """
    Convert Contact objects to dictionaries (for JSON export/API response).

    Args:
        contacts: List of Contact objects

    Returns:
        List of contact dictionaries
    """
    return [{
        'id': c.apollo_id or c.id,
        'name': c.full_name,
        'first_name': c.first_name,
        'last_name': c.last_name,
        'title': c.title,
        'company': c.company.name if c.company else None,
        'company_domain': c.company.domain if c.company else None,
        'location': c.location,
        'email': c.email,
        'phone': c.phone,
        'linkedin_url': c.linkedin_url,
        'seniority': c.seniority,
        'departments': c.departments,
        'photo_url': c.photo_url,
        'headline': c.headline,
        'enriched': c.enriched,
        'has_email': c.has_email,
        'has_phone': c.has_phone
    } for c in contacts]
