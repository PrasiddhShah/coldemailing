import React from 'react';

const ContactGrid = ({ contacts, onEnrich, onDraftEmail }) => {
    if (!contacts.length) return null;

    return (
        <div className="animate-fade-in" style={{ marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                Found {contacts.length} Contacts
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                {contacts.map((contact, index) => (
                    <div key={index} className="card" style={{ position: 'relative', overflow: 'hidden' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
                            <div>
                                <h4 style={{ fontWeight: 600, fontSize: '1.1rem' }}>
                                    {contact.first_name} {contact.last_name}
                                </h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{contact.title}</p>
                            </div>
                            {contact.email ? (
                                <span style={{
                                    background: 'transparent',
                                    color: 'var(--text-secondary)',
                                    padding: '2px 8px',
                                    borderRadius: 'var(--radius-sm)',
                                    fontSize: '0.7rem',
                                    border: '1px solid var(--border-color)'
                                }}>
                                    Enriched
                                </span>
                            ) : (
                                <span style={{
                                    background: 'transparent',
                                    color: 'var(--text-secondary)',
                                    padding: '2px 8px',
                                    borderRadius: 'var(--radius-sm)',
                                    fontSize: '0.7rem',
                                    border: '1px solid var(--border-color)'
                                }}>
                                    No Email
                                </span>
                            )}
                        </div>

                        <div style={{ marginBottom: '1.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            <p>{contact.company || "Company Unknown"}</p>
                            <p>{contact.location || "Location Unknown"}</p>
                        </div>

                        {contact.email ? (
                            <div style={{ marginBottom: '1rem' }}>
                                <p style={{ color: 'var(--text-primary)', fontSize: '0.875rem', fontFamily: 'monospace' }}>{contact.email}</p>
                            </div>
                        ) : null}

                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {!contact.email ? (
                                <button
                                    onClick={() => onEnrich(contact)}
                                    className="btn"
                                    style={{
                                        flex: 1,
                                        background: 'transparent',
                                        border: '1px solid var(--border-color)',
                                        color: 'var(--text-primary)'
                                    }}
                                >
                                    Reveal Email
                                </button>
                            ) : (
                                <button
                                    onClick={() => onDraftEmail(contact)}
                                    className="btn btn-primary"
                                    style={{ flex: 1 }}
                                >
                                    Draft Email
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ContactGrid;
