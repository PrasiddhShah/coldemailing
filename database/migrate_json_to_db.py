"""
Migrate existing JSON contact files to PostgreSQL database.

Usage:
    python -m database.migrate_json_to_db
    OR from project root: python database/migrate_json_to_db.py
"""
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import get_db_session, init_db, test_connection
from database.db_operations import upsert_company, upsert_contact
from config import load_config


def migrate_json_files(json_dir='outputs'):
    """
    Import all JSON files from outputs directory into database.

    Args:
        json_dir: Directory containing JSON files
    """
    config = load_config()

    # Test database connection first
    if not test_connection():
        print("[ERROR] Database connection failed!")
        print("Please check your DATABASE_URL in .env file")
        return

    # Initialize database
    print("Initializing database tables...")
    init_db()

    # Find all JSON files
    json_path = Path(json_dir)
    if not json_path.exists():
        print(f"[ERROR] Directory {json_dir} does not exist")
        return

    json_files = list(json_path.glob('*.json'))
    if not json_files:
        print(f"No JSON files found in {json_dir}/")
        return

    print(f"\nFound {len(json_files)} JSON files")
    print("=" * 60)

    total_companies = 0
    total_contacts = 0
    total_errors = 0

    with get_db_session() as db:
        for json_file in json_files:
            try:
                print(f"\n[FILE] Processing: {json_file.name}")

                # Load JSON file
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract metadata
                metadata = data.get('metadata', {})
                contacts_data = data.get('contacts', [])

                if not contacts_data:
                    print(f"  [WARN] No contacts in file, skipping")
                    continue

                # Get company info from metadata or first contact
                company_name = metadata.get('company')
                company_domain = metadata.get('company_domain')

                if not company_domain and contacts_data:
                    # Try to get from first contact
                    company_domain = contacts_data[0].get('company_domain')
                    company_name = contacts_data[0].get('company') or company_name

                if not company_domain:
                    print(f"  [WARN] No company domain found, skipping")
                    continue

                # Upsert company
                company = upsert_company(db, {
                    'domain': company_domain,
                    'name': company_name or company_domain.split('.')[0].title()
                })
                total_companies += 1

                print(f"  [OK] Company: {company.name} ({company.domain})")

                # Upsert contacts
                contact_count = 0
                for contact_data in contacts_data:
                    try:
                        # Map JSON fields to database fields
                        db_contact = {
                            'id': contact_data.get('id') or contact_data.get('apollo_id'),
                            'first_name': contact_data.get('first_name', ''),
                            'last_name': contact_data.get('last_name'),
                            'title': contact_data.get('title'),
                            'email': contact_data.get('email'),
                            'phone': contact_data.get('phone'),
                            'linkedin_url': contact_data.get('linkedin_url'),
                            'location': contact_data.get('location'),
                            'seniority': contact_data.get('seniority'),
                            'departments': contact_data.get('departments'),
                            'photo_url': contact_data.get('photo_url'),
                            'headline': contact_data.get('headline')
                        }

                        upsert_contact(db, db_contact, company.id)
                        contact_count += 1
                        total_contacts += 1

                    except Exception as e:
                        print(f"    [ERROR] Error importing contact: {e}")
                        total_errors += 1

                print(f"  [OK] Imported {contact_count} contacts")

            except Exception as e:
                print(f"  [ERROR] Error processing file: {e}")
                total_errors += 1

    # Summary
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"[OK] Companies imported: {total_companies}")
    print(f"[OK] Contacts imported:  {total_contacts}")
    if total_errors > 0:
        print(f"[ERROR] Errors:             {total_errors}")
    print("=" * 60)
    print("\n[DONE] Migration complete!")
    print("\nNext steps:")
    print("1. Verify data: python -c 'from database import *; from models import *; with get_db_session() as db: print(f\"Companies: {db.query(Company).count()}, Contacts: {db.query(Contact).count()}\")'")
    print("2. Start server: python server_db.py")


def verify_migration():
    """
    Verify migration by counting records.
    """
    from database.models import Company, Contact, Search

    print("\nVerifying database...")

    with get_db_session() as db:
        company_count = db.query(Company).count()
        contact_count = db.query(Contact).count()
        search_count = db.query(Search).count()

        print(f"\n[INFO] Database Status:")
        print(f"  - Companies: {company_count}")
        print(f"  - Contacts:  {contact_count}")
        print(f"  - Searches:  {search_count}")

        if company_count > 0:
            print(f"\n[INFO] Sample Companies:")
            companies = db.query(Company).limit(5).all()
            for c in companies:
                contact_count = db.query(Contact).filter(Contact.company_id == c.id).count()
                print(f"  - {c.name} ({c.domain}): {contact_count} contacts")


if __name__ == "__main__":
    print("=" * 60)
    print("JSON TO POSTGRESQL MIGRATION")
    print("=" * 60)

    # Run migration
    migrate_json_files()

    # Verify
    print()
    verify_migration()
