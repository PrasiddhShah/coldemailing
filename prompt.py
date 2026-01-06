# This is the prompt template used by the LLM to generate emails.
# You can edit this file to change the style, tone, or structure of the emails.
#
# AVAILABLE VARIABLES:
# {name}        - Full name of the contact
# {first_name}  - First name of the contact
# {title}       - Job title
# {company}     - Company name
# {location}    - Location (City, State)
# {headline}    - LinkedIn headline (if available)
# {user_context}- The custom context/offer you type in the UI

EMAIL_PROMPT_TEMPLATE = """
**Subject:** Interest in [Job Position] at [Company Name]

**Hi [Name],**

Hope you're doing well.

I'm a [Your Occupation & Specialization], and I’m interested in the **[Job Position]** at **[Company Name]**.

[One or two lines about your experience and impact.]

I believe my background in **[your skills/experience]** aligns well with **[company's goals/projects]**. I’d really appreciate the opportunity to connect, interview, or be considered for a referral.

**Role link:** [Insert link]

**Resume:** Attached

Looking forward to hearing from you.

Thanks,

[Your Name]





**Example**
Hi Nik,

Hope you're doing well.

I'm a Software Engineer with 2 years of experience, and I'm interested in the Software Engineer role at Pattern Data.

I've built full stack applications using TypeScript, React, and Node.js, and have hands on experience with PostgreSQL and AWS. At Sovereign InfoServices, I worked on document processing pipelines, ingesting 100K+ documents and building search systems with sub second retrieval, similar to Pattern's core platform.

I'd appreciate the opportunity to connect or be considered for a referral.

Role link: https://job-boards.greenhouse.io/patterndata/jobs/5012589007

Resume: Attached



write me this email for me, using the follow JOB description and resume

RESUME:

ABOUT ME:
Software Engineer with 2 years of experience developing scalable backend systems, data pipelines, and AI‐integrated applications. Skilled in Python, Java, and cloud platforms like Azure and AWS, with a focus on system reliability, performance optimization, and seamless data integration across distributed environments.
TECHNICAL SKILLS:
Programming Languages: Java, Python, C++, TypeScript, HTML, CSS.
Frameworks & Libraries: Flask, Node.js, Next.js, AngularJS, Spring Boot, PySpark, H2O Wave.
Databases: PostgreSQL, MySQL, MongoDB, SQLAlchemy.
Cloud: AWS, Azure, Docker, Rancher, Databricks, Snowflake.
Developer Tools: GitHub, Apache Kafka, Playwright, gRPC.
Certifications & Methodologies: AWS Certified Cloud Practitioner; Agile & Scrum practices.
PROFESSIONAL EXPERIENCE:
Software Engineer Intern, Sovereign InfoServices, USA May 2025 – Oct 2025
• Implemented a RAG platform, achieving a 50% reduction in document lookup time and sub‐second contextual retrieval, by ingesting 100K+ manuals from OpenText Documentum and automating Azure AI Search pipelines with Python notebooks.
• Collaborated with a cross‐functional team of 4 engineers to design, test, and deploy scalable backend services, ensuring compliance with functional and non‐functional requirements.
• Implemented real‐time hybrid vector keyword indexing by embedding 80K+ pages with Azure OpenAI (text‐embedding‐ada‐002), achieving 40% lower query latency and 30% higher top 5 relevance for search results.
Software Engineer Intern, Datanit, USA Jan 2025 – March 2025
• Enhanced MDM platform, improving data‐exchange reliability by 30% and reducing integration time by 50%, by integrating Postgres,MySQL, and MongoDB into Spring Boot microservices with secure REST APIs and server‐side logic.
• Optimized real‐time Apache Kafka streaming pipelines, achieving a 40% reduction in end‐to‐end data synchronization latency and 3x throughput by implementing topic partitioning, consumer‐group tuning.
Data Engineer Intern, CELEBAL TECHNOLOGY, USA May 2024 ‐ Aug 2024
• Architected an Azure Blob to Snowflake to Power BI pipeline, reducing reporting latency from days to real-time and accelerating customer insights delivery by 10x.
• Built Snowpark-powered financial dashboards using Python and Streamlit, improving data accessibility for non-technical analysts and eliminating 15+ hours of weekly manual reporting.
Software Engineer, H2O.Ai, USA Jan 2022 ‐ July 2023
• Developed a full‐stack Flask and H2O Wave analytics application integrated with Salesforce and Freshdesk, achieving a 15% increase in sales revenue by delivering iterative MVPs and enabling real‐time data synchronization.
• Optimized release cadence and scalability improving deployment speed 75% by containerizing Flask/Postgres, automating builds with Makefile, and orchestrating deployments via Rancher.
ACADEMIC PROJECTS:
LlamaDoc| Python, Ollama (Llama2), Prompt Engineering
• Developed a Python‐based Document‐to‐JSON converter, improving structured data extraction accuracy to 95% and reducing manual processing time by 80% for PDFs/DOCX by integrating Ollama’s Llama2 model to intelligently parse and normalize content.
MarketPulse |TypeScript, Node.js, Next.js, ConnectRPC
• Built a full‐stack crypto price streaming app using Next.js, Node.js, Playwright, and ConnectRPC, enabling real‐time TradingView data updates with efficient browser automation and push‐based communication.
Web‐Based Encryption and Decryption System |Angular, Flask, Docker, Jenkins
• Implemented a secure AES/DES/RSA web application, reducing security incidents 75% and accelerating deployments 60% by automating CI/CD with Docker and Jenkins.
Electric Vehicle Data Pipeline | Azure Blob, PySpark, DataBricks
• Implemented EV‐population Lakehouse on ADLS Gen2, improving analyst query performance 3x and reducing schema/parsingerrors 90% by developing PySpark/Delta dynamic JSON schema‐evolution parsing, modular ETL pipelines, automated data‐qualitychecks, and curated analytics tables.
EDUCATION:
Master of Science, Information Systems Aug 2023 - May 2025
George Mason University, Virgina, USA. GPA: 3.5
Bachelor of Engineering, Computer Science and Engineering July 2015 – June 2019
Charotar University of Science and Technology, Gujarat, India.

JOB DESCRIPTION:
{job_description}

Name: {name}
Role link: {job_link}
My Name:Prasiddh Shah

Requirements:
1. Return ONLY a valid JSON object with keys: "subject" and "body".
"""
