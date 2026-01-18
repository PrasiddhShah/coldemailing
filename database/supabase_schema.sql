-- ============================================================================
-- Apollo Cold Emailer - Supabase Database Schema
-- ============================================================================
-- Run this in: Supabase Dashboard > SQL Editor > New Query
-- ============================================================================

-- ============================================================================
-- COMPANIES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE NOT NULL,
    organization_id TEXT,
    industry TEXT,
    website TEXT,
    employee_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
CREATE INDEX IF NOT EXISTS idx_companies_org_id ON companies(organization_id);

-- ============================================================================
-- CONTACTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    apollo_id TEXT UNIQUE,

    -- Personal Info
    first_name TEXT NOT NULL,
    last_name TEXT,
    title TEXT,
    email TEXT,
    phone TEXT,

    -- Professional Info
    linkedin_url TEXT,
    location TEXT,
    seniority TEXT,
    departments JSONB,

    -- Additional Info
    photo_url TEXT,
    headline TEXT,

    -- Enrichment Status
    enriched BOOLEAN DEFAULT FALSE,
    enriched_at TIMESTAMPTZ,
    has_email BOOLEAN DEFAULT FALSE,
    has_phone BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint for upsert operations
    CONSTRAINT unique_contact UNIQUE (apollo_id, first_name, last_name, company_id)
);

CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_apollo_id ON contacts(apollo_id);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_enriched ON contacts(enriched);
CREATE INDEX IF NOT EXISTS idx_contacts_title ON contacts(title);
CREATE INDEX IF NOT EXISTS idx_contacts_seniority ON contacts(seniority);
CREATE INDEX IF NOT EXISTS idx_contacts_fullname ON contacts(first_name, last_name);
CREATE INDEX IF NOT EXISTS idx_contacts_departments ON contacts USING GIN(departments);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_contacts_fulltext ON contacts
    USING GIN(to_tsvector('english',
        COALESCE(first_name, '') || ' ' || COALESCE(last_name, '') || ' ' || COALESCE(title, '')
    ));

-- ============================================================================
-- SEARCHES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS searches (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,

    -- Search Parameters
    roles JSONB NOT NULL,
    search_limit INTEGER,

    -- Results
    total_found INTEGER DEFAULT 0,
    total_enriched INTEGER DEFAULT 0,

    -- Metadata
    user_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_searches_company_id ON searches(company_id);
CREATE INDEX IF NOT EXISTS idx_searches_created_at ON searches(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_searches_roles ON searches USING GIN(roles);

-- ============================================================================
-- EMAIL_DRAFTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_drafts (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,

    -- Email Content
    subject TEXT NOT NULL,
    body TEXT NOT NULL,

    -- Context
    job_description TEXT,
    job_link TEXT,

    -- AI Generation Info
    llm_provider TEXT,
    llm_model TEXT,
    generated_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_drafts_contact_id ON email_drafts(contact_id);
CREATE INDEX IF NOT EXISTS idx_drafts_created_at ON email_drafts(created_at DESC);

-- ============================================================================
-- EMAIL_HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS email_history (
    id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    draft_id INTEGER REFERENCES email_drafts(id) ON DELETE SET NULL,

    -- Email Details
    to_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,

    -- Status
    status TEXT DEFAULT 'draft',
    error_message TEXT,

    -- Attachments
    resume_attached BOOLEAN DEFAULT FALSE,
    resume_path TEXT,

    -- Sending Info
    smtp_provider TEXT,
    sent_at TIMESTAMPTZ,

    -- Tracking
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    replied_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_history_contact_id ON email_history(contact_id);
CREATE INDEX IF NOT EXISTS idx_email_history_status ON email_history(status);
CREATE INDEX IF NOT EXISTS idx_email_history_sent_at ON email_history(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_history_to_email ON email_history(to_email);

-- ============================================================================
-- TAGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    color TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- CONTACT_TAGS TABLE (Many-to-Many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS contact_tags (
    contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (contact_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_contact_tags_contact_id ON contact_tags(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_tags_tag_id ON contact_tags(tag_id);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT (Supabase compatible)
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_contacts_updated_at ON contacts;
CREATE TRIGGER update_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_drafts_updated_at ON email_drafts;
CREATE TRIGGER update_drafts_updated_at
    BEFORE UPDATE ON email_drafts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: All enriched contacts with company info
CREATE OR REPLACE VIEW enriched_contacts AS
SELECT
    c.*,
    co.name as company_name,
    co.domain as company_domain,
    co.industry as company_industry
FROM contacts c
LEFT JOIN companies co ON c.company_id = co.id
WHERE c.enriched = TRUE;

-- View: Email statistics per contact
CREATE OR REPLACE VIEW contact_email_stats AS
SELECT
    c.id as contact_id,
    c.first_name || ' ' || COALESCE(c.last_name, '') as full_name,
    c.email,
    COUNT(eh.id) FILTER (WHERE eh.status = 'sent') as total_emails_sent,
    MAX(eh.sent_at) as last_email_sent,
    BOOL_OR(eh.opened_at IS NOT NULL) as ever_opened,
    BOOL_OR(eh.replied_at IS NOT NULL) as ever_replied
FROM contacts c
LEFT JOIN email_history eh ON c.id = eh.contact_id
GROUP BY c.id, c.first_name, c.last_name, c.email;

-- View: Company statistics
CREATE OR REPLACE VIEW company_stats AS
SELECT
    co.id,
    co.name,
    co.domain,
    COUNT(DISTINCT c.id) as total_contacts,
    COUNT(DISTINCT CASE WHEN c.enriched THEN c.id END) as enriched_contacts,
    COUNT(DISTINCT s.id) as total_searches,
    COUNT(DISTINCT eh.id) FILTER (WHERE eh.status = 'sent') as emails_sent
FROM companies co
LEFT JOIN contacts c ON co.id = c.company_id
LEFT JOIN searches s ON co.id = s.company_id
LEFT JOIN email_history eh ON c.id = eh.contact_id
GROUP BY co.id, co.name, co.domain;

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY (Optional - uncomment if needed)
-- ============================================================================
-- ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE searches ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE email_drafts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE email_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE contact_tags ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- VERIFICATION QUERY
-- ============================================================================
-- Run this after setup to verify tables were created:
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;
