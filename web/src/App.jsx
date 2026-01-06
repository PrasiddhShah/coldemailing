import React, { useState } from 'react';
import SearchForm from './components/SearchForm';
import ContactGrid from './components/ContactGrid';
import EmailComposer from './components/EmailComposer';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [contacts, setContacts] = useState([]);
  const [draftingContact, setDraftingContact] = useState(null);
  // Store context per company: { "CompanyName": { desc: "...", link: "..." } }
  const [companyContexts, setCompanyContexts] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null); // { message, type: 'success' | 'error' }

  // Auto-dismiss notification
  React.useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const handleSearch = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!response.ok) throw new Error('Search failed');

      const data = await response.json();
      setContacts(data.contacts || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnrich = async (contact) => {
    try {
      const response = await fetch(`${API_BASE}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contacts: [contact] }),
      });

      if (!response.ok) throw new Error('Enrichment failed');

      const data = await response.json();
      const enrichedContact = data.contacts[0];

      // Update local state
      setContacts(prev => prev.map(c =>
        (c.id === enrichedContact.id || (c.first_name === enrichedContact.first_name && c.last_name === enrichedContact.last_name))
          ? enrichedContact
          : c
      ));

      return enrichedContact;
    } catch (err) {
      setNotification({ message: 'Failed to reveal email: ' + err.message, type: 'error' });
      return null;
    }
  };

  const handleDraftEmail = async (contact) => {
    let targetContact = contact;

    // JUST-IN-TIME ENRICHMENT
    // If we don't have the email yet, fetch it now (Cost: 1 Credit)
    if (!targetContact.email) {
      setNotification({ message: 'Revealing email... (1 Credit)', type: 'success' });
      const enriched = await handleEnrich(contact);
      if (enriched) {
        targetContact = enriched;
      } else {
        return; // Stop if enrichment failed
      }
    }

    setDraftingContact(targetContact);
  };

  const handleSendEmail = async (emailData) => {
    try {
      const response = await fetch(`${API_BASE}/send-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(emailData),
      });

      if (!response.ok) throw new Error('Failed to send email');

      setNotification({ message: 'Email sent successfully!', type: 'success' });
      setDraftingContact(null);
    } catch (err) {
      setNotification({ message: 'Error sending email: ' + err.message, type: 'error' });
    }
  };

  const handleUpdateCompanyContext = (company, description, link) => {
    setCompanyContexts(prev => ({
      ...prev,
      [company]: { description, link }
    }));
  };

  return (
    <div style={{ paddingBottom: '4rem' }}>
      <header style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <div style={{
          display: 'inline-block',
          padding: '0.5rem 1rem',
          borderRadius: '2rem',
          background: 'rgba(99, 102, 241, 0.1)',
          color: 'var(--accent-primary)',
          fontSize: '0.875rem',
          fontWeight: 600,
          marginBottom: '1rem'
        }}>
          Apollo Cold Emailer
        </div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
          Find & Connect with <span style={{ color: 'var(--accent-primary)' }}>Top Talent</span>
        </h1>
      </header>

      <SearchForm onSearch={handleSearch} isLoading={isLoading} />

      {error && (
        <div style={{
          maxWidth: '600px',
          margin: '2rem auto',
          padding: '1rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(239, 68, 68, 0.1)',
          color: '#ef4444',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          textAlign: 'center'
        }}>
          {error}
        </div>
      )}

      <ContactGrid
        contacts={contacts}
        onEnrich={handleEnrich}
        onDraftEmail={handleDraftEmail}
      />

      {draftingContact && (
        <EmailComposer
          contact={draftingContact}
          onClose={() => setDraftingContact(null)}
          onSend={handleSendEmail}
          savedContext={companyContexts[draftingContact.company]?.description || ''}
          savedJobLink={companyContexts[draftingContact.company]?.link || ''}
          onUpdateContext={(desc, link) => handleUpdateCompanyContext(draftingContact.company, desc, link)}
        />
      )}

      {/* Toast Notification */}
      {notification && (
        <div className="animate-fade-in" style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          background: notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(16, 185, 129, 0.9)',
          color: 'white',
          padding: '1rem 2rem',
          borderRadius: '8px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
          zIndex: 2000,
          backdropFilter: 'blur(4px)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default App;
