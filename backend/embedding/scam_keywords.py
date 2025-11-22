# ====== FINANCIAL SCAMS ======
FINANCIAL_SCAM_PATTERNS = {
    "ponzi_pyramid": [
        "ponzi scheme", "pyramid scheme", "matrix scheme", "chain letter",
        "multi-level marketing", "mlm scam", "network marketing scam",
        "recruit members", "downline", "upline", "residual income forever",
        "passive income guarantee", "recruitment fees", "buy starter kit"
    ],
    
    "investment_fraud": [
        "guaranteed returns", "risk-free investment", "no risk profit",
        "insider trading tip", "offshore investment", "tax haven",
        "prime bank", "high yield investment program", "hyip",
        "binary options guaranteed", "forex robot guarantee",
        "crypto pump and dump", "altcoin guarantee", "get in early",
        "pre-ipo investment", "exclusive investor opportunity"
    ],
    
    "advance_fee": [
        "nigerian prince", "inheritance claim", "unclaimed funds",
        "lottery winner notification", "you have won", "prize claim fee",
        "processing fee required", "transfer fee", "customs fee",
        "tax clearance certificate", "attorney fees upfront",
        "foreign business partner", "beneficiary notification"
    ],
    
    "crypto_scams": [
        "bitcoin doubler", "ethereum giveaway scam", "crypto airdrop fake",
        "send crypto get more", "elon musk giveaway", "celebrity crypto",
        "guaranteed mining returns", "cloud mining scam",
        "nft rug pull", "defi scam", "yield farming guaranteed",
        "liquidity pool guaranteed", "send to verify wallet"
    ]
}

# ====== E-COMMERCE & MARKETPLACE SCAMS ======
ECOMMERCE_SCAM_PATTERNS = {
    "fake_sellers": [
        "brand new in box cheap", "authentic replica", "factory direct",
        "warehouse clearance urgent", "bankruptcy sale everything must go",
        "gray market goods", "no receipt provided", "cash only deal",
        "meet in parking lot", "wire transfer only", "gift cards payment",
        "zelle only", "venmo friends family", "paypal friends family only"
    ],
    
    "phishing_indicators": [
        "verify account immediately", "suspended account action required",
        "unusual activity detected", "confirm identity now",
        "click here to reactivate", "update payment information urgent",
        "security alert verify", "account will be closed",
        "refund pending click here", "package delivery problem"
    ],
    
    "counterfeit": [
        "authentic aaa replica", "mirror quality", "1:1 copy",
        "factory original", "oem quality", "no box but genuine",
        "overstock original", "gray import authentic"
    ]
}

# ====== EMPLOYMENT & WORK FROM HOME SCAMS ======
EMPLOYMENT_SCAM_PATTERNS = {
    "fake_jobs": [
        "work from home earn thousands", "no experience high pay",
        "envelope stuffing job", "reshipping coordinator",
        "mystery shopper scam", "check cashing job",
        "pay for training materials", "buy starter kit required",
        "wire transfer job", "cryptocurrency job suspicious",
        "personal assistant forward packages", "money mule"
    ],
    
    "income_opportunity": [
        "financial freedom system", "quit your job guaranteed",
        "laptop lifestyle", "passive income automated",
        "get rich quick method", "overnight millionaire",
        "done for you system", "push button profits",
        "automated cash system", "secret loophole"
    ]
}

# ====== ROMANCE & PERSONAL SCAMS ======
ROMANCE_SCAM_PATTERNS = [
    "stranded abroad need money", "emergency funds please",
    "sick relative hospital", "customs release fee",
    "plane ticket to visit you", "visa application fee",
    "business partner betrayed", "investment went wrong help",
    "gold shipment stuck", "inheritance lawyer fees"
]

# ====== TECH SUPPORT & SOFTWARE SCAMS ======
TECH_SCAM_PATTERNS = [
    "microsoft called me", "apple security alert",
    "virus detected call now", "computer infected immediate",
    "remote access required", "antivirus expired renew",
    "ip address compromised", "hacker alert",
    "lifetime license cheap", "cracked software safe"
]

# ====== CHARITY & DISASTER SCAMS ======
CHARITY_SCAM_PATTERNS = [
    "disaster relief urgent", "hurricane victims donation",
    "fake charity registration", "government grant available",
    "veteran charity scam", "cancer patient donation",
    "orphanage donation africa", "wildlife rescue fake"
]

# ====== PRESSURE TACTICS (High Priority) ======
PRESSURE_TACTICS = {
    "urgency": [
        "act now or lose", "expires in 24 hours", "only today",
        "last chance ever", "spots filling fast", "limited time",
        "offer ends tonight", "hurry before gone", "immediate action required",
        "once in lifetime", "never again", "final call"
    ],
    
    "scarcity": [
        "only 3 left", "limited supply", "exclusive members only",
        "invitation only", "selected few", "private access",
        "beta testers needed", "early adopters only", "vip access"
    ],
    
    "social_proof_fake": [
        "thousands are joining", "everyone is doing it",
        "your neighbors making money", "celebrities use this",
        "doctors recommend scam", "government approved fake",
        "millions of satisfied", "trusted by thousands vague"
    ]
}

# ====== TRUST INDICATORS (Anti-scam signals) ======
TRUST_SIGNALS = {
    "legal_compliance": [
        "privacy policy", "terms of service", "terms and conditions",
        "cookie policy", "gdpr compliant", "ccpa compliant",
        "data protection act", "legal disclaimer", "regulatory compliance",
        "sec registered", "finra member", "fdic insured",
        "better business bureau accredited", "bbb rating"
    ],
    
    "business_legitimacy": [
        "registered business number", "vat number", "ein number",
        "business registration", "company house number",
        "d-u-n-s number", "business license", "trade license",
        "physical office address", "headquarters location",
        "operating since", "established year"
    ],
    
    "contact_transparency": [
        "customer service number", "support phone", "helpdesk",
        "live chat support", "email support", "contact form",
        "mailing address", "registered office", "contact us",
        "customer support hours", "toll free number"
    ],
    
    "certifications": [
        "ssl certificate", "https secure", "verified merchant",
        "certified professional", "licensed provider", "accredited",
        "iso certified", "pci compliant", "soc 2 compliant",
        "verified seller", "authenticated", "authorized dealer"
    ],
    
    "transparency": [
        "refund policy", "return policy", "money back guarantee legitimate",
        "shipping policy", "warranty information", "pricing breakdown",
        "fee structure", "no hidden fees", "transparent pricing",
        "frequently asked questions", "how it works", "about us detailed"
    ],
    
    "payment_security": [
        "secure checkout", "encrypted payment", "buyer protection",
        "escrow service", "payment processor", "credit card accepted",
        "paypal business", "stripe verified", "square merchant"
    ]
}

# ====== LINGUISTIC PATTERNS (Scam language) ======
LINGUISTIC_RED_FLAGS = {
    "exaggeration": [
        "100% guaranteed", "absolutely free", "completely risk free",
        "totally safe", "perfectly legal", "fully automated",
        "incredibly easy", "amazingly simple", "unbelievably profitable"
    ],
    
    "vague_claims": [
        "secret system", "hidden method", "insider knowledge",
        "proprietary algorithm", "exclusive formula", "patent pending fake",
        "proven method vague", "tested system no proof", "revolutionary breakthrough"
    ],
    
    "emotional_manipulation": [
        "don't be left behind", "fear of missing out", "your family deserves",
        "imagine your life", "what if you could", "financial stress relief",
        "debt free life guaranteed", "retire early guaranteed"
    ]
}

# ====== DOMAIN & URL PATTERNS ======
SUSPICIOUS_URL_PATTERNS = [
    r"\.tk$", r"\.ml$", r"\.ga$", r"\.cf$", r"\.gq$",  # Free TLDs
    r"bit\.ly", r"tinyurl\.com", r"goo\.gl",  # URL shorteners
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # IP addresses
    r"[0-9]{4,}",  # Many numbers in domain
    r"-{2,}", r"_{2,}",  # Multiple dashes/underscores
]

# ====== SCORING WEIGHTS ======
SEVERITY_WEIGHTS = {
    "critical": 20,      # Ponzi, advance fee, crypto doubler
    "high": 15,          # Investment fraud, fake jobs
    "medium": 10,        # Pressure tactics, vague claims
    "low": 5,            # Minor suspicious indicators
    "trust_major": -15,  # Strong trust signals
    "trust_minor": -8    # Moderate trust signals
}


def get_all_scam_keywords():
    all_keywords = []
    
    for category in FINANCIAL_SCAM_PATTERNS.values():
        all_keywords.extend(category)
    
    for category in ECOMMERCE_SCAM_PATTERNS.values():
        all_keywords.extend(category)
    
    for category in EMPLOYMENT_SCAM_PATTERNS.values():
        all_keywords.extend(category)
    
    all_keywords.extend(ROMANCE_SCAM_PATTERNS)
    all_keywords.extend(TECH_SCAM_PATTERNS)
    all_keywords.extend(CHARITY_SCAM_PATTERNS)
    
    for category in PRESSURE_TACTICS.values():
        all_keywords.extend(category)
    
    for category in LINGUISTIC_RED_FLAGS.values():
        all_keywords.extend(category)
    
    return list(set(all_keywords))


def get_all_trust_keywords():
    all_keywords = []
    
    for category in TRUST_SIGNALS.values():
        all_keywords.extend(category)
    
    return list(set(all_keywords))


def get_category_matches(text: str):

    text_lower = text.lower()
    matches = {
        "financial_scams": {},
        "ecommerce_scams": {},
        "employment_scams": {},
        "pressure_tactics": {},
        "linguistic_flags": {},
        "trust_signals": {}
    }
    
    for category, keywords in FINANCIAL_SCAM_PATTERNS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["financial_scams"][category] = found
    
    for category, keywords in ECOMMERCE_SCAM_PATTERNS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["ecommerce_scams"][category] = found
    
    # Employment scams
    for category, keywords in EMPLOYMENT_SCAM_PATTERNS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["employment_scams"][category] = found
    
    # Pressure tactics
    for category, keywords in PRESSURE_TACTICS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["pressure_tactics"][category] = found
    
    # Linguistic flags
    for category, keywords in LINGUISTIC_RED_FLAGS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["linguistic_flags"][category] = found
    
    # Trust signals
    for category, keywords in TRUST_SIGNALS.items():
        found = [kw for kw in keywords if kw in text_lower]
        if found:
            matches["trust_signals"][category] = found
    
    return matches
