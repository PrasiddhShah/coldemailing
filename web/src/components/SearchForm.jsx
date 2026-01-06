import React, { useState } from 'react';

const SearchForm = ({ onSearch, isLoading }) => {
    const [company, setCompany] = useState('');
    const [roles, setRoles] = useState(['recruiter']);
    const [limit, setLimit] = useState(10);

    const availableRoles = [
        { id: 'recruiter', label: 'Recruiter' },
        { id: 'engineering_manager', label: 'Eng Manager' },
        { id: 'cto', label: 'CTO' },
        { id: 'ceo', label: 'CEO & Founders' },
        { id: 'sales', label: 'Sales' },
        { id: 'marketing', label: 'Marketing' },
    ];

    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch({ company, roles, limit });
    };

    const toggleRole = (roleId) => {
        setRoles(prev =>
            prev.includes(roleId)
                ? prev.filter(r => r !== roleId)
                : [...prev, roleId]
        );
    };

    return (
        <div className="card animate-fade-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', background: 'linear-gradient(to right, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Find Contacts
            </h2>

            <form onSubmit={handleSubmit}>
                <div className="input-group">
                    <label className="input-label">Company Name or Domain</label>
                    <input
                        type="text"
                        className="input-field"
                        placeholder="e.g. Google, stripe.com"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        required
                    />
                </div>

                <div className="input-group">
                    <label className="input-label">Target Roles</label>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {availableRoles.map(role => (
                            <button
                                key={role.id}
                                type="button"
                                onClick={() => toggleRole(role.id)}
                                style={{
                                    padding: '0.5rem 1rem',
                                    borderRadius: '2rem',
                                    border: `1px solid ${roles.includes(role.id) ? 'var(--accent-primary)' : 'var(--border-color)'}`,
                                    background: roles.includes(role.id) ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                                    color: roles.includes(role.id) ? 'white' : 'var(--text-secondary)',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {role.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="input-group">
                    <label className="input-label">Max Results</label>
                    <input
                        type="number"
                        className="input-field"
                        value={limit}
                        onChange={(e) => setLimit(parseInt(e.target.value))}
                        min="1"
                        max="100"
                        style={{ width: '100px' }}
                    />
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ width: '100%', marginTop: '1rem' }}
                    disabled={isLoading || !company}
                >
                    {isLoading ? 'Searching...' : 'Search Contacts'}
                </button>
            </form>
        </div>
    );
};

export default SearchForm;
