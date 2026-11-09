import json
import os
import re
import math
from pathlib import Path
from collections import Counter
import requests
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KB_PATH = BASE_DIR / 'knowledge_base.json'

def load_knowledge_base():
    try:
        with open(KB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[RAG] Error loading knowledge base: {e}")
        return {}

KNOWLEDGE_BASE = load_knowledge_base()

# English stop words for BM25 tokenization
STOP_WORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'his', 'him',
    'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'would',
    'with', 'about', 'can', 'could', 'do', 'does', 'did', 'tell', 'me', 'what', 'which', 'how',
    'who', 'where', 'when', 'why', 'give', 'show', 'please', 'know', 'some', 'any', 'i', 'you',
    'your', 'my', 'there', 'their', 'them', 'this', 'these', 'those'
}

def tokenize(text):
    """Clean text into meaningful lower-case alphabetic tokens"""
    tokens = re.findall(r'[a-zA-Z0-9_\-\.\+]+', text.lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

# ========================================================
# KNOWLEDGE CHUNK BUILDER
# ========================================================

def build_knowledge_chunks():
    chunks = []
    p = KNOWLEDGE_BASE.get('profile', {})
    curr = KNOWLEDGE_BASE.get('current_status', {})
    edu = p.get('education', {})
    c = p.get('contact', {})
    skills = KNOWLEDGE_BASE.get('skills', {})
    ce = KNOWLEDGE_BASE.get('flagship_project', {})
    ce_db = ce.get('database_architecture', {})
    ce_decisions = ce.get('architectural_decisions', {})

    # 1. Profile Overview
    chunks.append({
        'id': 'profile_overview',
        'category': 'bio',
        'title': 'Jothilingam S — Profile & Background',
        'section': 'Professional Identity & Core Summary',
        'status': 'Verified Identity',
        'keywords': ['jothilingam', 'profile', 'bio', 'engineer', 'architect', 'developer', 'location', 'coimbatore', 'tamil nadu', 'about', 'summary', 'overview', 'who'],
        'content': (
            f"Jothilingam S is a {p.get('title')} based in {p.get('location')}. "
            f"Professional summary: {p.get('summary', '')} "
            f"He is currently active as a {curr.get('role')} (started {curr.get('timeline')}). "
            f"Availability: {p.get('availability')}. "
            f"Languages: {', '.join(p.get('languages', []))}."
        ),
        'structured_answer': (
            f"**Jothilingam S** is a **{p.get('title')}** based in {p.get('location')}.\n\n"
            f"He specializes in full-stack web applications, resilient offline-first architectures (like CollectEasy), "
            f"and multi-tier cloud infrastructure on AWS and GCP. He is currently working as a **Freelance Full-Stack Developer** "
            f"({curr.get('timeline')}) and is available for software engineering roles, cloud consulting, and contracts."
        )
    })

    # 2. Current Status (Freelance)
    chunks.append({
        'id': 'current_status',
        'category': 'status',
        'title': 'Current Professional State — Freelance Full-Stack Developer',
        'section': 'Active Engagements & Production Deliveries',
        'status': 'Active Professional Engagement (May 2026 – Present)',
        'keywords': ['current', 'currently', 'now', 'freelance', 'freelancing', 'status', 'role', 'active', 'recent', 'may 2026', 'present', 'started', 'doing now'],
        'content': (
            f"Role: {curr.get('role')}. Timeline: {curr.get('timeline')}. Status: {curr.get('status')}. "
            f"{curr.get('description')} He began his freelance full-stack engineering career in May 2026 "
            f"immediately following his web development internship at El Codamics. "
            f"Deliveries include: {' '.join(curr.get('deliveries', []))}"
        ),
        'structured_answer': (
            f"Jothilingam is currently working as a **Freelance Full-Stack Developer** (**May 2026 – Present**).\n\n"
            f"Following the completion of his web development internship at El Codamics in May 2026, he transitioned into independent commercial deliveries. "
            f"His active work focuses on end-to-end web architectures, offline-first PWAs (like CollectEasy), and cloud deployments across AWS and GCP."
        )
    })

    # 3. Flagship Project: CollectEasy (Overview & Storage Architecture)
    chunks.append({
        'id': 'flagship_collecteasy',
        'category': 'project',
        'title': 'Flagship Project: CollectEasy — Offline-First Chit Fund & Field Collection Platform',
        'section': 'Offline PWA & Storage Architecture',
        'status': 'Implemented & Deployed Production PWA',
        'keywords': ['collecteasy', 'flagship', 'chit', 'fund', 'offline', 'pwa', 'indexeddb', 'idempotency', 'uuid', 'paise', 'ledger', 'collection', 'agent', 'fintech', 'database', 'storage', 'why', 'localstorage', 'rationale'],
        'content': (
            f"Project: {ce.get('name')} ({ce.get('tagline')}). Category: {ce.get('category')}. Status: {ce.get('status')}. "
            f"Highlights: {' '.join(ce.get('highlights', []))} "
            f"Database & Storage Architecture: Client-Side Storage: {ce_db.get('client_storage')}. "
            f"Backend Database: {ce_db.get('backend_database')}. "
            f"Architectural Decisions: Why IndexedDB over localStorage: {ce_decisions.get('why_indexeddb')} "
            f"Why Idempotent UUID Keys: {ce_decisions.get('why_idempotent_uuid')} "
            f"Why Paise Integer Math: {ce_decisions.get('why_paise_math')} "
            f"Why 3-Tier Topology: {ce_decisions.get('why_3_tier_topology')} "
            f"Technologies: {', '.join(ce.get('technologies', []))}."
        ),
        'structured_answer': (
            f"**CollectEasy** is Jothilingam's flagship production platform—an offline-first chit fund management and field collection PWA.\n\n"
            f"**Core Architecture & Decisions:**\n"
            f"- **Offline-First PWA (IndexedDB)**: Engineered with asynchronous client-side IndexedDB caching so field collection agents record transactions uninterrupted in low-connectivity rural zones without UI blocking or 5MB storage limits.\n"
            f"- **Idempotent UUID Keys**: Dynamically generated on the client to guarantee zero duplicate financial entries upon network reconnection and synchronization.\n"
            f"- **Paise Integer Arithmetic**: Calculates all currency strictly as integer paise, eliminating IEEE-754 floating-point rounding errors.\n"
            f"- **3-Tier Topology**: Mobile Agent PWA client communicating with scalable Node.js/Express REST microservices and a persistent transactional database."
        )
    })

    # 4. Commercial Projects: SPM Crackers & The Grove Restaurant
    for cp in KNOWLEDGE_BASE.get('commercial_projects', []):
        name_clean = cp.get('name', '')
        c_id = f"project_{name_clean.lower().replace(' ', '_')}"
        is_grove = 'grove' in name_clean.lower()
        decisions_str = ""
        if is_grove and cp.get('architectural_decisions'):
            decisions_str = f" Architectural Decisions: Why GCP Cloud Run: {cp.get('architectural_decisions', {}).get('why_gcp_cloud_run')}"

        chunks.append({
            'id': c_id,
            'category': 'project',
            'title': f"Commercial Project: {name_clean} — {cp.get('type')}",
            'section': 'Deployment & Product Architecture',
            'status': cp.get('status', 'Implemented & Deployed Production Application'),
            'keywords': [name_clean.lower(), 'ecommerce', 'restaurant', 'store', 'shop', 'spm', 'crackers', 'grove', 'gcp', 'cloud run', 'retail', 'hospitality', 'deployment'],
            'content': (
                f"Project: {name_clean} ({cp.get('url')}). Type: {cp.get('type')}. Status: {cp.get('status')}. "
                f"Platform: {cp.get('deployment_platform', 'Web Production')}. "
                f"Highlights: {' '.join(cp.get('highlights', []))}{decisions_str} "
                f"Technologies: {', '.join(cp.get('technologies', []))}."
            ),
            'structured_answer': (
                f"**{name_clean}** ([{cp.get('url')}]({cp.get('url')})) is an implemented and deployed commercial web application:\n\n"
                f"- **Domain & Category**: {cp.get('type')}\n"
                f"- **Status**: {cp.get('status')}\n"
                f"- **Platform / Deployment**: {cp.get('deployment_platform', 'Production Web')}\n"
                f"- **Engineering Highlights**: {' '.join(cp.get('highlights', []))}\n"
                f"- **Core Stack**: {', '.join(cp.get('technologies', []))}"
            )
        })

    # 5. Cloud Architectures (AWS Multi-Tier & High Availability)
    for ca in KNOWLEDGE_BASE.get('cloud_architectures', []):
        name_ca = ca.get('name', '')
        c_id = f"cloud_{name_ca.lower().replace(' ', '_')}"
        chunks.append({
            'id': c_id,
            'category': 'cloud',
            'title': f"Cloud Architecture: {name_ca}",
            'section': 'AWS Systems & Infrastructure Topologies',
            'status': ca.get('status', 'Designed Cloud Architecture Topology'),
            'keywords': ['aws', 'cloud', 'architecture', 'infrastructure', 'ec2', 's3', 'vpc', 'rds', 'alb', 'load balancer', 'auto scaling', 'high availability', 'failover', 'route 53', 'cloudwatch', 'topology'],
            'content': (
                f"Architecture: {name_ca} ({ca.get('type')}). Status: {ca.get('status')}. "
                f"Highlights: {' '.join(ca.get('highlights', []))} "
                f"Technologies: {', '.join(ca.get('technologies', []))}."
            ),
            'structured_answer': (
                f"**{name_ca}** ({ca.get('status')}):\n\n"
                f"{chr(10).join('- ' + h for h in ca.get('highlights', []))}\n\n"
                f"**Toolchains & Services**: {', '.join(ca.get('technologies', []))}"
            )
        })

    # 6. Technical Capabilities & Skills
    chunks.append({
        'id': 'skills_capabilities',
        'category': 'skills',
        'title': 'Technical Capabilities: Core Skills & Toolchains',
        'section': 'Engineering Taxonomy & Stack Matrix',
        'status': 'Verified Technical Proficiencies',
        'keywords': ['skills', 'stack', 'technologies', 'tools', 'languages', 'frontend', 'backend', 'database', 'cloud', 'react', 'nextjs', 'python', 'fastapi', 'node', 'django', 'docker', 'git'],
        'content': (
            f"Verified engineering skills: Frontend: {', '.join(skills.get('frontend', []))}. "
            f"Backend: {', '.join(skills.get('backend', []))}. "
            f"Cloud: {', '.join(skills.get('cloud', []))}. "
            f"Data & Systems: {', '.join(skills.get('data_and_systems', []))}. "
            f"Note: Jothilingam does not have verified commercial experience in unlisted technologies such as Rust, Kubernetes operators, Solidity smart contracts, Blockchain, or Swift."
        ),
        'structured_answer': (
            f"Jothilingam's verified engineering stack across four core domains:\n\n"
            f"1. **Frontend Engineering**: {', '.join(skills.get('frontend', []))}\n"
            f"2. **Backend Architecture**: {', '.join(skills.get('backend', []))}\n"
            f"3. **Cloud Infrastructure**: {', '.join(skills.get('cloud', []))}\n"
            f"4. **Data & Systems**: {', '.join(skills.get('data_and_systems', []))}"
        )
    })

    # 7. Experience / Internship at El Codamics
    for exp in KNOWLEDGE_BASE.get('experience', []):
        chunks.append({
            'id': 'internship_elcodamics',
            'category': 'experience',
            'title': f"Professional Experience: {exp.get('role')} at {exp.get('company')}",
            'section': 'Industry Internship & Engineering Deliveries',
            'status': exp.get('status', 'Completed Internship'),
            'keywords': ['intern', 'internship', 'el codamics', 'codamics', 'experience', 'company', 'work', 'crm', 'rest api', 'agile', 'responsibilities'],
            'content': (
                f"Role: {exp.get('role')} at {exp.get('company')}, {exp.get('location')} ({exp.get('timeline')}). "
                f"Status: {exp.get('status')}. "
                f"Responsibilities: {' '.join(exp.get('responsibilities', []))} "
                f"Technologies: {', '.join(exp.get('technologies', []))}."
            ),
            'structured_answer': (
                f"Jothilingam completed a **{exp.get('role')}** at **{exp.get('company')}** in {exp.get('location')} ({exp.get('timeline')}):\n\n"
                f"- Contributed to enterprise CRM architecture, client modules, and enterprise workflows.\n"
                f"- Integrated RESTful APIs and optimized client-side state handling for responsive UI components.\n"
                f"- Collaborated with senior engineers on code reviews, Git version control, and agile sprint delivery.\n"
                f"- **Technologies**: {', '.join(exp.get('technologies', []))}."
            )
        })

    # 8. Education & Credentials at NIET (Anna University)
    chunks.append({
        'id': 'education_niet',
        'category': 'education',
        'title': 'Academic Credentials: B.Tech in Information Technology',
        'section': 'Higher Education & Accreditation',
        'status': edu.get('status', 'Completed Degree'),
        'keywords': ['education', 'college', 'degree', 'btech', 'university', 'cgpa', 'nehru', 'niet', 'anna university', 'marks', 'academic', 'study', 'grade'],
        'content': (
            f"Degree: {edu.get('degree')} from {edu.get('institution')} ({edu.get('affiliation')}). "
            f"Timeline: {edu.get('timeline')}. CGPA: {edu.get('cgpa')}. Status: {edu.get('status')}."
        ),
        'structured_answer': (
            f"Jothilingam earned his **{edu.get('degree')}** from **{edu.get('institution')}** "
            f"({edu.get('affiliation')}), studying from **{edu.get('timeline')}** and graduating with a verified **{edu.get('cgpa')} CGPA**."
        )
    })

    # 9. Contact & Social Channels
    chunks.append({
        'id': 'contact_details',
        'category': 'contact',
        'title': 'Contact Channels & Direct Inquiries',
        'section': 'Direct Inquiries & Profiles',
        'status': 'Verified Contact Channels',
        'keywords': ['contact', 'email', 'phone', 'reach', 'hire', 'call', 'message', 'linkedin', 'github', 'connect', 'talk', 'touch', 'get in touch'],
        'content': (
            f"Email: {c.get('email')}, Phone: {c.get('phone')}. "
            f"LinkedIn: {c.get('linkedin')}, GitHub: {c.get('github')}. "
            f"Location: {p.get('location')}."
        ),
        'structured_answer': (
            f"You can contact Jothilingam S directly:\n\n"
            f"- **Email**: [{c.get('email')}](mailto:{c.get('email')})\n"
            f"- **Phone**: [{c.get('phone')}](tel:{c.get('phone').replace(' ', '')})\n"
            f"- **LinkedIn**: [linkedin.com/in/jothilingamsivalingam]({c.get('linkedin')})\n"
            f"- **GitHub**: [github.com/JOTHILINGAM-S-CYBROX]({c.get('github')})\n"
            f"- **Location**: {p.get('location')}"
        )
    })

    return chunks

CHUNKS = build_knowledge_chunks()

# Precompute IDF for BM25 retrieval
def compute_corpus_stats(chunks):
    total_docs = len(chunks)
    doc_freq = Counter()
    doc_tokens = {}
    
    for c in chunks:
        full_text = f"{c['title']} {c['section']} {' '.join(c['keywords'])} {c['content']}"
        tokens = tokenize(full_text)
        doc_tokens[c['id']] = tokens
        unique_tokens = set(tokens)
        for t in unique_tokens:
            doc_freq[t] += 1
            
    idf = {}
    for t, count in doc_freq.items():
        idf[t] = math.log(1 + (total_docs - count + 0.5) / (count + 0.5))
        
    avg_doc_len = sum(len(toks) for toks in doc_tokens.values()) / max(total_docs, 1)
    
    return idf, doc_tokens, avg_doc_len

CORPUS_IDF, DOC_TOKENS, AVG_DOC_LEN = compute_corpus_stats(CHUNKS)

# Domain Specific Keyword Boosts to prevent topic bleed
DOMAIN_BOOSTS = {
    'contact_details': ['contact', 'email', 'phone', 'reach', 'hire', 'call', 'message', 'touch', 'get in touch', 'linkedin', 'github'],
    'flagship_collecteasy': ['collecteasy', 'chit', 'fund', 'offline', 'pwa', 'indexeddb', 'uuid', 'idempotency', 'paise', 'database', 'localstorage'],
    'current_status': ['current', 'currently', 'now', 'freelance', 'freelancing', 'status', 'may 2026', 'doing now'],
    'cloud_scalable_aws_infrastructure': ['aws', 'cloud', 'ec2', 's3', 'vpc', 'rds', 'route 53', 'cloudwatch', 'infrastructure'],
    'cloud_high_availability_aws_architecture': ['high availability', 'alb', 'load balancer', 'auto scaling', 'multi-az', 'standby', 'failover'],
    'internship_elcodamics': ['intern', 'internship', 'el codamics', 'codamics'],
    'education_niet': ['education', 'college', 'degree', 'btech', 'university', 'cgpa', 'nehru', 'niet', 'anna university', 'academic'],
    'skills_capabilities': ['skills', 'stack', 'technologies', 'tools', 'languages', 'frontend', 'backend', 'database', 'libraries', 'frameworks'],
    'project_spm_crackers': ['spm', 'crackers', 'ecommerce', 'e-commerce', 'seasonal', 'spmcrackers'],
    'project_the_grove_restaurant': ['grove', 'restaurant', 'thegrove', 'hospitality', 'cloud run', 'gcp']
}

# ========================================================
# CONVERSATIONAL INTENT CLASSIFIER
# ========================================================

GREETING_WORDS = {'hi', 'hii', 'hiii', 'hello', 'hey', 'heyy', 'howdy', 'yo', 'sup', 'namaste', 'vanakkam'}

def is_greeting(query):
    q = query.strip().lower()
    tokens = re.findall(r'\b\w+\b', q)
    if not tokens:
        return False
    # Single greeting word or short greeting phrase like "hi there"
    if tokens[0] in GREETING_WORDS and len(tokens) <= 3:
        return True
    if any(q == g or q.startswith(g + ' ') for g in ['good morning', 'good afternoon', 'good evening', 'good day', 'hey there', 'hello there']):
        return True
    return False

def is_gratitude(query):
    q = query.strip().lower()
    return bool(re.search(r'\b(thank|thanks|thx|ty|great|awesome|perfect|appreciate)\b', q))

def is_farewell(query):
    q = query.strip().lower()
    return bool(re.search(r'\b(bye|goodbye|see you|cya|take care)\b', q))

def is_bot_identity(query):
    q = query.strip().lower()
    return bool(re.search(r'\b(who are you|what are you|what can you do|how do you work|help|capabilities)\b', q))

def classify_intent(message):
    if is_greeting(message):
        return 'greeting'
    if is_gratitude(message):
        return 'gratitude'
    if is_farewell(message):
        return 'farewell'
    if is_bot_identity(message):
        return 'bot_identity'
    return 'informational'

# ========================================================
# MULTI-TURN CONTEXT RESOLVER
# ========================================================

def resolve_conversation_context(query, history=None):
    """
    Inspect previous conversation turns to resolve pronouns and follow-up references
    (e.g., "Which database does it use?", "Why did you choose that?", "How was it deployed?").
    Returns rewritten retrieval query.
    """
    if not history or not isinstance(history, list) or len(history) == 0:
        return query

    q_lower = query.lower()
    has_pronoun_or_short = (
        len(q_lower.split()) <= 6 or
        any(re.search(r'\b' + re.escape(w) + r'\b', q_lower) for w in [
            'it', 'its', 'that', 'this', 'there', 'the project', 'the app', 'the database',
            'the system', 'why', 'how', 'stack', 'database', 'deploy', 'deployed', 'choice', 'choose'
        ])
    )

    if not has_pronoun_or_short:
        return query

    # Find the most recent active entity discussed in history
    active_entity = None
    for turn in reversed(history[-6:]):
        text = turn.get('content', '').lower()
        if any(k in text for k in ['collecteasy', 'chit fund', 'indexeddb', 'paise', 'idempotent']):
            active_entity = 'collecteasy'
            break
        elif any(k in text for k in ['the grove', 'grove restaurant', 'cloud run', 'gcp']):
            active_entity = 'the grove restaurant gcp'
            break
        elif any(k in text for k in ['spm crackers', 'crackers', 'spmcrackers']):
            active_entity = 'spm crackers e-commerce'
            break
        elif any(k in text for k in ['aws', 'ec2', 'alb', 'auto scaling', 'rds multi-az', 'vpc']):
            active_entity = 'aws cloud architecture'
            break
        elif any(k in text for k in ['el codamics', 'intern', 'internship', 'crm']):
            active_entity = 'el codamics internship'
            break
        elif any(k in text for k in ['education', 'college', 'niet', 'anna university', 'btech', 'degree', 'cgpa']):
            active_entity = 'education niet'
            break
        elif any(k in text for k in ['freelance', 'current role', 'may 2026']):
            active_entity = 'freelance full-stack developer'
            break

    if active_entity:
        return f"{active_entity} {query}"

    return query

# ========================================================
# BM25 + DOMAIN VECTOR RETRIEVAL ENGINE
# ========================================================

def retrieve_knowledge(query, top_k=2):
    """BM25 + Domain Boost semantic ranking across portfolio knowledge chunks"""
    query_tokens = tokenize(query)
    q_lower = query.lower()
    
    k1 = 1.5
    b = 0.75
    
    scored_chunks = []
    for chunk in CHUNKS:
        c_id = chunk['id']
        tokens = DOC_TOKENS.get(c_id, [])
        doc_len = len(tokens)
        token_counts = Counter(tokens)
        
        bm25_score = 0.0
        for qt in query_tokens:
            if qt in token_counts:
                tf = token_counts[qt]
                idf = CORPUS_IDF.get(qt, 0.5)
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / AVG_DOC_LEN))
                bm25_score += idf * (numerator / denominator)
                
        # Keyword and phrase bonus
        for kw in chunk['keywords']:
            if kw in q_lower:
                bm25_score += 2.5
                
        # Title & section match bonus
        for qt in query_tokens:
            if qt in chunk['title'].lower():
                bm25_score += 2.0
            if qt in chunk['section'].lower():
                bm25_score += 1.5

        # Domain-specific priority boosts
        boost_keywords = DOMAIN_BOOSTS.get(c_id, [])
        for bk in boost_keywords:
            if bk in q_lower:
                bm25_score += 8.0

        scored_chunks.append((bm25_score, chunk))
        
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_results = [item[1] for item in scored_chunks if item[0] > 1.2]
    if not top_results and scored_chunks:
        top_results = [scored_chunks[0][1]]
        
    return top_results[:top_k]

# ========================================================
# GEMINI GENERATIVE REASONING ENGINE
# ========================================================

def strip_leading_salutation(text):
    """Remove redundant leading greetings from factual answers"""
    if not text:
        return ""
    pattern = r'^(?:hello!|hello|hi!|hi|hey!|hey|greetings|howdy)[,\s]+'
    cleaned = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned if cleaned else text

def query_gemini_api(user_message, context_chunks, history=None):
    """
    Call Google Gemini API using v1beta systemInstruction and structured contents.
    Enforces strict grounding, context continuity, system distinctions, and unknown handling.
    """
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        return None

    context_text = "\n\n".join([
        f"[{c['title']} | Section: {c['section']} | Status: {c.get('status', 'Verified')}]:\n{c['content']}"
        for c in context_chunks
    ])

    system_instruction_text = (
        "You are Architect AI, the conversational engineering copilot for Jothilingam S, a Full-Stack Software Engineer & Cloud Architect based in Coimbatore, India.\n\n"
        "STRICT GROUNDING & CONVERSATIONAL RULES:\n"
        "1. GROUNDING: Base all factual answers strictly on the provided VERIFIED PORTFOLIO GROUND TRUTH. Never fabricate project features, technologies, achievements, or employment.\n"
        "2. SYSTEM CLASSIFICATION & STATUS DISTINCTIONS:\n"
        "   - Implemented & Deployed: CollectEasy (flagship offline-first PWA with IndexedDB, idempotent UUIDs, paise integer math, 3-tier architecture), "
        "SPM Crackers (commercial seasonal e-commerce at spmcrackers.in), The Grove Restaurant (commercial hospitality web app at thegrove.restaurant deployed on GCP Cloud Run).\n"
        "   - Designed Cloud Architectures: Scalable AWS Infrastructure (EC2, S3, RDS, isolated VPC, IAM, Route 53, CloudWatch), "
        "High Availability AWS Architecture (ALB multi-AZ health routing, Auto Scaling Groups, Amazon RDS Multi-AZ standby failover).\n"
        "   - Completed Internship: El Codamics (Jan 19, 2026 – May 2, 2026) as Web Developer Intern working on CRM architecture, REST APIs, and MERN stack.\n"
        "   - Academic Credentials: B.Tech in Information Technology from Nehru Institute of Engineering and Technology (Anna University affiliated), Nov 2022 – Apr 2026, CGPA 7.5/10.\n"
        "   - Current Role: Freelance Full-Stack Developer (May 2026 – Present).\n"
        "3. CONTEXT CONTINUITY & MULTI-TURN RESOLUTION:\n"
        "   - When the user asks a follow-up question using pronouns like 'it', 'that', 'the database', 'the project', or asks 'Why did you choose that?' or 'How was it deployed?', "
        "refer to the specific project or system discussed in previous conversation turns.\n"
        "4. ARCHITECTURAL DECISIONS & REASONING:\n"
        "   - When asked why a specific technology was chosen (e.g. why IndexedDB over localStorage in CollectEasy, why idempotent UUIDs, why paise integer math, why GCP Cloud Run in The Grove): "
        "explain the documented architectural rationale accurately.\n"
        "   - If the user asks for technical reasoning not explicitly documented, clearly state the standard engineering principle while distinguishing it from verified project records.\n"
        "5. UNKNOWN INFORMATION & UNVERIFIED TECHNOLOGIES:\n"
        "   - If the user asks whether Jothilingam knows, has built, or has experience with a technology, skill, or project NOT explicitly verified in the ground truth "
        "(for example: Rust, Kubernetes operators, Solidity, smart contracts, blockchain, Swift, iOS native, Ruby on Rails): "
        "Do NOT speculate, assume, or invent experience. Respond naturally and clearly: "
        "'I don't have verified information about that specific detail in Jothilingam's portfolio documentation.'\n"
        "6. RESPONSE QUALITY & CONCISENESS:\n"
        "   - Be direct, conversational, articulate, and complete. Use bullet points or short paragraphs only when helpful. Never cut off mid-sentence."
    )

    # Multi-turn conversation assembly
    contents = []
    if history and isinstance(history, list):
        for item in history[-6:]:
            role = 'user' if item.get('role') == 'user' else 'model'
            text = item.get('content', '').strip()
            if text:
                contents.append({'role': role, 'parts': [{'text': text}]})

    # Append current turn with fresh retrieved context attached
    current_prompt = (
        f"--- VERIFIED PORTFOLIO GROUND TRUTH ---\n"
        f"{context_text}\n"
        f"---------------------------------------\n\n"
        f"User Question: {user_message}\n\n"
        f"Direct Grounded Answer:"
    )
    contents.append({'role': 'user', 'parts': [{'text': current_prompt}]})

    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction_text}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024
        }
    }

    models_to_try = [
        os.getenv('GEMINI_MODEL', 'gemini-flash-lite-latest'),
        'gemini-flash-lite-latest',
        'gemini-2.5-flash',
        'gemini-flash-latest',
        'gemini-3.5-flash'
    ]
    models_to_try = list(dict.fromkeys(models_to_try))

    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, timeout=12)
            if res.status_code == 200:
                data = res.json()
                candidate = data.get('candidates', [{}])[0]
                finish_reason = candidate.get('finishReason', '')
                if finish_reason == 'MAX_TOKENS':
                    continue
                parts = candidate.get('content', {}).get('parts', [])
                if parts:
                    text = parts[0].get('text', '').strip()
                    # Check text completeness (non-empty and not ending in trailing dash or unfinished token)
                    if text and len(text) > 30 and not text.endswith(('-', '**')):
                        return {
                            'answer': text,
                            'model': model_name
                        }
        except Exception as e:
            print(f"[RAG] Error querying Gemini model {model_name}: {e}")
            continue

    return None

# ========================================================
# UNKNOWN TECHNOLOGY DETECTOR
# ========================================================

UNVERIFIED_TECHNOLOGIES = [
    'rust', 'kubernetes operator', 'kubernetes operators', 'solidity', 'smart contract',
    'smart contracts', 'blockchain', 'web3', 'crypto', 'swift', 'ios native', 'kotlin',
    'android native', 'cobol', 'c++', 'embedded', 'ruby on rails', 'ruby', 'assembly'
]

def asks_unverified_technology(query):
    q = query.lower()
    return any(re.search(r'\b' + re.escape(tech) + r'\b', q) for tech in UNVERIFIED_TECHNOLOGIES)

# ========================================================
# MAIN RAG ANSWER PIPELINE
# ========================================================

def answer_query(user_message, history=None):
    """
    Main RAG orchestrator:
    1. Conversational intent detection (natural greetings, gratitude, farewells).
    2. Context continuity resolution from conversation history.
    3. Retrieval of relevant grounded knowledge chunks.
    4. Gemini LLM generation with strict grounding & system distinctions.
    5. Fallback to BM25 structured response if LLM is unavailable.
    """
    cleaned_query = user_message.strip()
    if not cleaned_query:
        return {
            "answer": "Hello! How can I assist you with Jothilingam's portfolio or projects?",
            "engine": "conversational-core",
            "sources": []
        }

    intent = classify_intent(cleaned_query)

    # 1. Natural Greeting (Concise, friendly, NO capability lists)
    if intent == 'greeting':
        return {
            "answer": "Hey! 👋 Nice to meet you. What would you like to explore about Jothilingam's projects or technical experience?",
            "engine": "conversational-intent",
            "sources": ["Portfolio Assistant Introduction"]
        }

    # 2. Gratitude
    if intent == 'gratitude':
        return {
            "answer": "You're very welcome! Let me know if you would like to explore any technical architectures, project decisions, or how to get in touch with Jothilingam.",
            "engine": "conversational-intent",
            "sources": []
        }

    # 3. Farewells
    if intent == 'farewell':
        return {
            "answer": "Thanks for stopping by! Feel free to reach back out anytime or connect directly with Jothilingam at jothilingamsivalingamg@gmail.com. Have a great day ahead!",
            "engine": "conversational-intent",
            "sources": []
        }

    # 4. Bot Identity
    if intent == 'bot_identity':
        return {
            "answer": (
                "I am **Architect AI**, Jothilingam's conversational engineering copilot. "
                "I can answer questions about his software projects (such as CollectEasy, The Grove, and SPM Crackers), "
                "cloud topologies on AWS and GCP, his technical stack, and his professional journey."
            ),
            "engine": "conversational-intent",
            "sources": ["Architect AI Introduction"]
        }

    # 5. Unknown Technology Guard (Before retrieval)
    if asks_unverified_technology(cleaned_query):
        return {
            "answer": (
                "I don't have verified information about that specific detail in Jothilingam's portfolio documentation. "
                "His verified engineering stack is focused on full-stack web applications (React, Next.js, Node.js, Python), "
                "offline-first PWAs (CollectEasy), and cloud infrastructure across AWS and GCP."
            ),
            "engine": "grounding-guard",
            "sources": ["Technical Capabilities: Core Skills & Toolchains"]
        }

    # 6. Multi-Turn Context Resolution for Follow-Ups
    retrieval_query = resolve_conversation_context(cleaned_query, history=history)

    retrieved = retrieve_knowledge(retrieval_query, top_k=2)
    sources = [f"{c['title']} ({c['section']})" for c in retrieved]

    # 7. Generative LLM Pipeline (Gemini)
    gemini_result = query_gemini_api(cleaned_query, retrieved, history=history)
    if gemini_result:
        raw_answer = gemini_result['answer']
        clean_ans = strip_leading_salutation(raw_answer)
        return {
            "answer": clean_ans,
            "engine": f"gemini ({gemini_result['model']})",
            "sources": sources
        }

    # 8. Grounded BM25 Fallback Synthesizer
    if retrieved:
        primary_chunk = retrieved[0]
        answer_text = primary_chunk['structured_answer']

        q_lower = cleaned_query.lower()
        if any(w in q_lower for w in ['capable', 'can he', 'can you', 'is he able', 'does he know']):
            answer_text = f"**Yes, absolutely!** Jothilingam is an experienced Full-Stack Developer actively delivering end-to-end production systems.\n\n" + answer_text

        clean_ans = strip_leading_salutation(answer_text)
        return {
            "answer": clean_ans,
            "engine": "django-bm25-rag",
            "sources": sources
        }

    # 9. Graceful catch-all
    return {
        "answer": (
            "I don't have verified information about that specific detail in Jothilingam's portfolio documentation. "
            "You can ask me about his flagship project **CollectEasy**, his commercial works (**SPM Crackers**, **The Grove**), "
            "his **AWS cloud architectures**, his **current freelance work (May 2026 – Present)**, or how to get in touch."
        ),
        "engine": "django-bm25-rag",
        "sources": []
    }
