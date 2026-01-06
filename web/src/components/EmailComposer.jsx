import React, { useState, useEffect } from 'react';

const EmailComposer = ({ contact, onClose, onSend, savedContext = '', savedJobLink = '', onUpdateContext }) => {
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [userContext, setUserContext] = useState(savedContext);
    const [jobLink, setJobLink] = useState(savedJobLink);
    const [toEmail, setToEmail] = useState(contact.email || '');
    const [attachResume, setAttachResume] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isSending, setIsSending] = useState(false);

    // Update state when contact changes
    useEffect(() => {
        setToEmail(contact.email || '');
        setSubject('');
        setBody('');
    }, [contact]);

    // Sync context changes back to parent
    useEffect(() => {
        if (onUpdateContext) {
            onUpdateContext(userContext, jobLink);
        }
    }, [userContext, jobLink]);

    const handleGenerate = async () => {
        setIsGenerating(true);
        try {
            const response = await fetch('http://localhost:8000/api/generate-email', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contact,
                    user_context: userContext,
                    job_link: jobLink
                })
            });
            const data = await response.json();
            setSubject(data.subject);
            setBody(data.body);
        } catch (err) {
            console.error("Failed to generate draft:", err);
            setBody("Error generating draft. Please try again.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleSend = async () => {
        setIsSending(true);
        await onSend({
            to_email: toEmail,
            subject,
            body,
            attach_resume: attachResume
        });
        setIsSending(false);
    };

    return (
        <div className='composer-overlay' style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(5px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
        }}>
            <div className='card animate-fade-in' style={{
                width: '90%',
                maxWidth: '1000px',
                height: '80vh',
                display: 'flex',
                overflow: 'hidden',
                padding: 0,
                border: '1px solid var(--border-color)'
            }}>
                {/* Left Panel: Context */}
                <div style={{
                    width: '30%',
                    background: 'var(--bg-secondary)',
                    padding: '2rem',
                    borderRight: '1px solid var(--border-color)',
                    display: 'flex',
                    flexDirection: 'column'
                }}>
                    <h3 style={{ marginBottom: '1.5rem', color: 'var(--accent-primary)' }}>Contact Details</h3>

                    <div style={{ marginBottom: '2rem' }}>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{contact.first_name} {contact.last_name}</h2>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{contact.title}</p>
                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{contact.company}</p>
                    </div>

                    <div style={{ marginBottom: '2rem' }}>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email</label>
                        <input
                            type="text"
                            value={toEmail}
                            onChange={(e) => setToEmail(e.target.value)}
                            style={{
                                fontFamily: 'monospace',
                                marginTop: '0.25rem',
                                background: 'transparent',
                                border: 'none',
                                borderBottom: '1px solid var(--border-color)',
                                color: 'white',
                                width: '100%',
                                fontSize: '1rem',
                                padding: '0.25rem 0'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '2rem' }}>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Location</label>
                        <p style={{ marginTop: '0.25rem' }}>{contact.location || 'N/A'}</p>
                    </div>

                    <div style={{ marginBottom: '1rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Job Description / Context</label>
                        <textarea
                            value={userContext}
                            onChange={(e) => setUserContext(e.target.value)}
                            placeholder="Paste Job Description here..."
                            style={{
                                flex: 2,
                                width: '100%',
                                background: 'var(--bg-input)',
                                border: '1px solid var(--border-color)',
                                color: 'white',
                                borderRadius: '4px',
                                padding: '0.5rem',
                                resize: 'none',
                                fontSize: '0.9rem',
                                marginBottom: '1rem'
                            }}
                        />

                        <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>Job Link</label>
                        <input
                            type="text"
                            value={jobLink}
                            onChange={(e) => setJobLink(e.target.value)}
                            placeholder="https://..."
                            style={{
                                width: '100%',
                                background: 'var(--bg-input)',
                                border: '1px solid var(--border-color)',
                                color: 'white',
                                borderRadius: '4px',
                                padding: '0.5rem',
                                fontSize: '0.9rem'
                            }}
                        />
                    </div>

                    <div style={{ marginTop: 'auto' }}>
                        <button
                            onClick={handleGenerate}
                            className="btn"
                            disabled={isGenerating}
                            style={{
                                width: '100%',
                                background: 'rgba(99, 102, 241, 0.1)',
                                color: 'var(--accent-primary)',
                                border: '1px solid var(--accent-primary)'
                            }}
                        >
                            {isGenerating ? 'Regenerating...' : 'Regenerate Draft'}
                        </button>
                    </div>
                </div>

                {/* Right Panel: Editor */}
                <div style={{
                    flex: 1,
                    padding: '2rem',
                    display: 'flex',
                    flexDirection: 'column',
                    background: 'var(--bg-card)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3 style={{ color: 'white' }}>Compose Email</h3>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--text-secondary)',
                                fontSize: '1.5rem',
                                cursor: 'pointer'
                            }}
                        >
                            &times;
                        </button>
                    </div>

                    <div className="input-group">
                        <input
                            type="text"
                            className="input-field"
                            placeholder="Subject"
                            value={subject}
                            onChange={(e) => setSubject(e.target.value)}
                            style={{ fontSize: '1.1rem', fontWeight: 500 }}
                        />
                    </div>

                    <textarea
                        className="input-field"
                        placeholder="Write your email..."
                        value={body}
                        onChange={(e) => setBody(e.target.value)}
                        style={{
                            flex: 1,
                            resize: 'none',
                            marginBottom: '1.5rem',
                            lineHeight: '1.6',
                            fontFamily: 'inherit'
                        }}
                    />

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', alignItems: 'center' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={attachResume}
                                onChange={(e) => setAttachResume(e.target.checked)}
                            />
                            Attach Resume
                        </label>
                        <button
                            onClick={onClose}
                            className="btn"
                            style={{
                                background: 'transparent',
                                color: 'var(--text-secondary)'
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSend}
                            className="btn btn-primary"
                            disabled={isSending || !body}
                            style={{ minWidth: '120px' }}
                        >
                            {isSending ? 'Sending...' : 'Send Email'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EmailComposer;

