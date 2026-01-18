"""
List all companies in the database.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import database
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import get_db_session, Company, Contact

def list_companies():
    """List all companies with contact counts."""
    print('ID   Company Name                        Domain                     Contacts')
    print('=' * 80)

    with get_db_session() as db:
        companies = db.query(Company).order_by(Company.name).all()

        for c in companies:
            contact_count = db.query(Contact).filter(Contact.company_id == c.id).count()
            print(f'{c.id:<4} {c.name[:35]:<35} {c.domain[:25]:<25} {contact_count:<8}')

        print('=' * 80)
        total_contacts = db.query(Contact).count()
        print(f'Total: {len(companies)} companies, {total_contacts} contacts')

if __name__ == '__main__':
    list_companies()
