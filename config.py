import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration management for Apollo API tool."""

    APOLLO_API_KEY = os.getenv('APOLLO_API_KEY', '')
    API_BASE_URL = "https://api.apollo.io"
    DEFAULT_PER_PAGE = int(os.getenv('DEFAULT_PER_PAGE', '100'))
    DEFAULT_PER_PAGE = int(os.getenv('DEFAULT_PER_PAGE', '100'))
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', 'outputs')

    # AI Config
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini') # mock, openai, gemini
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.5-flash')

    # Email Config
    EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'mock') # mock, smtp
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_EMAIL = os.getenv('SMTP_EMAIL', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    RESUME_DIR = os.getenv('RESUME_DIR', 'docs')




    TITLE_MAPPINGS = {
        'recruiter': {
            'titles': [
                # Standard Recruiter Titles
                'Recruiter',
                'Technical Recruiter',
                'Senior Recruiter',
                'Lead Recruiter',
                'Staff Recruiter',
                'Corporate Recruiter',
                'IT Recruiter',
                'Software Recruiter',
                'Engineering Recruiter',

                # Talent Acquisition Variations
                'Talent Acquisition',
                'Talent Acquisition Specialist',
                'Talent Acquisition Partner',
                'Talent Acquisition Manager',
                'Senior Talent Acquisition',
                'Lead Talent Acquisition',
                'Talent Acquisition Lead',
                'Director of Talent Acquisition',
                'VP Talent Acquisition',
                'Head of Talent Acquisition',
                'Talent Acquisition Coordinator',
                'TA Specialist',
                'TA Partner',
                'TA Manager',

                # Management & Leadership
                'Recruiting Manager',
                'Recruitment Manager',
                'Head of Recruiting',
                'Head of Recruitment',
                'Director of Recruiting',
                'Director of Recruitment',
                'VP of Recruiting',
                'VP Recruiting',
                'Hiring Manager',

                # People & HR Variations
                'People Partner',
                'People Operations',
                'People Operations Manager',
                'People Ops',
                'HR Manager',
                'HR Business Partner',
                'HRBP',
                'Human Resources Business Partner',
                'Human Resources Manager',
                'HR Specialist',
                'HR Generalist',
                'Senior HR Business Partner',

                # Talent & Sourcing
                'Talent Partner',
                'Talent Manager',
                'Talent Scout',
                'Talent Sourcer',
                'Technical Sourcer',
                'Sourcing Specialist',
                'Sourcing Manager',
                'Lead Sourcer',

                # Other Variations
                'Recruitment Consultant',
                'Talent Consultant',
                'Staffing Manager',
                'Staffing Specialist',
                'Workforce Planning',
                'Talent Advisor'
            ],
            'seniorities': ['manager', 'head', 'senior', 'director', 'vp']
        },
        'engineering_manager': {
            'titles': [
                # Engineering Manager Titles
                'Engineering Manager',
                'Software Engineering Manager',
                'Senior Engineering Manager',
                'Staff Engineering Manager',
                'Development Manager',
                'Software Development Manager',

                # Team Lead Variations
                'Team Lead',
                'Engineering Lead',
                'Tech Lead',
                'Technical Lead',
                'Lead Engineer',
                'Lead Software Engineer',
                'Staff Engineer',
                'Principal Engineer',

                # Director Level
                'Director of Engineering',
                'Engineering Director',
                'Director Software Engineering',
                'Senior Engineering Manager',
                'Group Engineering Manager',

                # Specialized
                'Frontend Engineering Manager',
                'Backend Engineering Manager',
                'Full Stack Engineering Manager',
                'Mobile Engineering Manager',
                'Platform Engineering Manager',
                'Infrastructure Engineering Manager',
                'DevOps Manager',
                'SRE Manager',
                'QA Manager',
                'Test Manager',
                'Quality Engineering Manager'
            ],
            'seniorities': ['manager', 'head', 'director', 'senior', 'vp']
        },
        'cto': {
            'titles': [
                # C-Level
                'CTO',
                'Chief Technology Officer',
                'Chief Technical Officer',
                'CIO',
                'Chief Information Officer',
                'CPTO',
                'Chief Product Technology Officer',

                # VP Engineering
                'VP Engineering',
                'VP of Engineering',
                'Vice President of Engineering',
                'Vice President Engineering',
                'SVP Engineering',
                'Senior VP Engineering',

                # Head of Engineering
                'Head of Engineering',
                'Head of Technology',
                'Head of Software Engineering',
                'Head of Software Development',
                'Head of Product Engineering',

                # Other Executive Tech Roles
                'VP Technology',
                'VP of Technology',
                'Director of Engineering',
                'Senior Director of Engineering'
            ],
            'seniorities': ['c_suite', 'vp', 'head', 'director']
        },
        'ceo': {
            'titles': [
                'CEO',
                'Chief Executive Officer',
                'Founder',
                'Co-Founder',
                'President',
                'Managing Director',
                'Owner',
                'Founder & CEO',
                'Co-Founder & CEO'
            ],
            'seniorities': ['c_suite', 'founder', 'owner']
        },
        'founder': {
             'titles': [
                 'Founder',
                 'Co-Founder',
                 'Cofounder',
                 'Owner',
                 'Founding Partner',
                 'Founder & CEO',
                 'Co-Founder & CTO',
                 'Founding Engineer'
             ],
             'seniorities': ['founder', 'c_suite', 'owner']
        },
        'sales': {
            'titles': [
                'Sales Manager',
                'Account Executive',
                'Senior Account Executive',
                'VP of Sales',
                'VP Sales',
                'Head of Sales',
                'Director of Sales',
                'Sales Director',
                'Business Development',
                'Business Development Manager',
                'BDR',
                'SDR',
                'Sales Development Representative',
                'Business Development Representative',
                'Chief Revenue Officer',
                'CRO',
                'Revenue Operations'
            ],
            'seniorities': ['manager', 'head', 'vp', 'director', 'c_suite']
        },
        'marketing': {
            'titles': [
                'Marketing Manager',
                'CMO',
                'Chief Marketing Officer',
                'VP of Marketing',
                'VP Marketing',
                'Head of Marketing',
                'Director of Marketing',
                'Marketing Director',
                'Product Marketing Manager',
                'Growth Manager',
                'Head of Growth',
                'VP Growth',
                'Demand Generation Manager',
                'Content Marketing Manager',
                'Digital Marketing Manager'
            ],
            'seniorities': ['manager', 'head', 'vp', 'c_suite', 'director']
        }
    }


def load_config():
    """Load and return configuration."""
    return Config()


def validate_api_key(api_key):
    """Validate that API key is present and not empty."""
    if not api_key or api_key == 'your_apollo_api_key_here':
        raise ValueError(
            "Apollo API key not found or invalid. "
            "Please set APOLLO_API_KEY in your .env file. "
            "You can create one by copying .env.example to .env and adding your API key."
        )
    return True


def mask_api_key(api_key):
    """Mask API key for logging (show only last 4 characters)."""
    if len(api_key) <= 4:
        return "****"
    return "*" * (len(api_key) - 4) + api_key[-4:]


def find_resume_path(resume_dir='docs'):
    """
    Find the first PDF file in the resume directory.

    Args:
        resume_dir: Directory to search for PDF files

    Returns:
        Path to the first PDF found, or None if no PDF exists
    """
    if not os.path.exists(resume_dir):
        return None

    # Look for PDF files in the directory
    for filename in os.listdir(resume_dir):
        if filename.lower().endswith('.pdf'):
            return os.path.join(resume_dir, filename)

    return None
