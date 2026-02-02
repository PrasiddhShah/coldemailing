from sqlalchemy import Column, Integer, String, DateTime, Table, MetaData, Text, ForeignKey, Boolean
from sqlalchemy import create_engine
from dotenv import load_dotenv,find_dotenv
import os

load_dotenv(find_dotenv(), override=False)

# Create instances directly, no classes needed
engine = create_engine(os.getenv("DB_CONNECTION"))
metadata = MetaData()

companies = Table(
    'companies',
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("organization_id", Integer),
    Column("website", String(250)),
    Column("linkedin", String(250)),
    Column("logo_url", Text),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)

contacts = Table(
    'contacts',
    metadata,
    Column("id", Integer, primary_key=True),
    Column("company_id", Integer, ForeignKey("companies.id")),
    Column('first_name',String(50)),
    Column('last_name',String(50)),
    Column('email',String(50)),
    Column('title',String(50)),
    Column("linkedin",String(250)),
    Column("location",String(50)),
    Column("photo_url",Text),
    Column("enriched",Boolean),
    Column("created_at", DateTime),
    Column("updated_at", DateTime)
)
