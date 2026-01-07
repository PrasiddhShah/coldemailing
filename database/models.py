"""
SQLAlchemy ORM models for Apollo Cold Emailer.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey,
    JSON, func, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .database import Base


class Company(Base):
    """Company/Organization model."""
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    domain = Column(Text, unique=True, nullable=False, index=True)
    organization_id = Column(Text, index=True)  # Apollo org ID
    industry = Column(Text)
    website = Column(Text)
    employee_count = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    searches = relationship("Search", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company(name='{self.name}', domain='{self.domain}')>"


class Contact(Base):
    """Contact/Person model."""
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), index=True)
    apollo_id = Column(Text, unique=True, index=True)

    # Personal Info
    first_name = Column(Text, nullable=False)
    last_name = Column(Text)
    title = Column(Text, index=True)
    email = Column(Text, index=True)
    phone = Column(Text)

    # Professional Info
    linkedin_url = Column(Text)
    location = Column(Text)
    seniority = Column(Text, index=True)
    departments = Column(JSONB)  # Array of department names

    # Additional Info
    photo_url = Column(Text)
    headline = Column(Text)

    # Enrichment Status
    enriched = Column(Boolean, default=False, index=True)
    enriched_at = Column(DateTime(timezone=True))
    has_email = Column(Boolean, default=False)
    has_phone = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="contacts")
    email_drafts = relationship("EmailDraft", back_populates="contact", cascade="all, delete-orphan")
    email_history = relationship("EmailHistory", back_populates="contact", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="contact_tags", back_populates="contacts")

    # Constraints
    __table_args__ = (
        UniqueConstraint('apollo_id', 'first_name', 'last_name', 'company_id', name='unique_contact'),
        Index('idx_contacts_fullname', 'first_name', 'last_name'),
    )

    @property
    def full_name(self):
        """Generate full name from first and last name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def __repr__(self):
        return f"<Contact(name='{self.full_name}', email='{self.email}')>"


class Search(Base):
    """Search history model."""
    __tablename__ = 'searches'

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), index=True)

    # Search Parameters
    roles = Column(JSONB, nullable=False)  # ["recruiter", "engineering_manager"]
    search_limit = Column(Integer)

    # Results
    total_found = Column(Integer, default=0)
    total_enriched = Column(Integer, default=0)

    # Metadata
    user_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    company = relationship("Company", back_populates="searches")

    def __repr__(self):
        return f"<Search(company_id={self.company_id}, roles={self.roles}, found={self.total_found})>"


class EmailDraft(Base):
    """Email drafts model."""
    __tablename__ = 'email_drafts'

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'), index=True)

    # Email Content
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)

    # Context
    job_description = Column(Text)
    job_link = Column(Text)

    # AI Generation Info
    llm_provider = Column(Text)  # gemini, openai, mock
    llm_model = Column(Text)
    generated_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    contact = relationship("Contact", back_populates="email_drafts")
    email_sent = relationship("EmailHistory", back_populates="draft", uselist=False)

    def __repr__(self):
        return f"<EmailDraft(contact_id={self.contact_id}, subject='{self.subject[:30]}...')>"


class EmailHistory(Base):
    """Email sending history model."""
    __tablename__ = 'email_history'

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'), index=True)
    draft_id = Column(Integer, ForeignKey('email_drafts.id', ondelete='SET NULL'))

    # Email Details
    to_email = Column(Text, nullable=False, index=True)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)

    # Status
    status = Column(Text, default='draft', index=True)  # draft, sent, failed, bounced
    error_message = Column(Text)

    # Attachments
    resume_attached = Column(Boolean, default=False)
    resume_path = Column(Text)

    # Sending Info
    smtp_provider = Column(Text)
    sent_at = Column(DateTime(timezone=True), index=True)

    # Tracking (for future features)
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    replied_at = Column(DateTime(timezone=True))

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contact = relationship("Contact", back_populates="email_history")
    draft = relationship("EmailDraft", back_populates="email_sent")

    def __repr__(self):
        return f"<EmailHistory(to='{self.to_email}', status='{self.status}', sent_at='{self.sent_at}')>"


class Tag(Base):
    """Tags for organizing contacts."""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, unique=True, nullable=False)
    color = Column(Text)  # Hex color code for UI

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contacts = relationship("Contact", secondary="contact_tags", back_populates="tags")

    def __repr__(self):
        return f"<Tag(name='{self.name}')>"


class ContactTag(Base):
    """Many-to-many relationship between contacts and tags."""
    __tablename__ = 'contact_tags'

    contact_id = Column(Integer, ForeignKey('contacts.id', ondelete='CASCADE'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ContactTag(contact_id={self.contact_id}, tag_id={self.tag_id})>"
