import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

grok_client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

GROK_MODEL = "llama-3.3-70b-versatile"


def extract_text_from_html(html_content: str) -> Dict[str, Any]:

    soup = BeautifulSoup(html_content, 'html.parser')
    
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    
    title = soup.find('title')
    title_text = title.get_text().strip() if title else ""
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else ""
    
    headings = []
    for tag in ['h1', 'h2', 'h3']:
        for heading in soup.find_all(tag):
            text = heading.get_text().strip()
            if text:
                headings.append(text)

    links = []
    for link in soup.find_all('a', href=True):
        links.append({
            'text': link.get_text().strip(),
            'href': link['href']
        })

    body_text = soup.get_text(separator=' ', strip=True)
    
    max_body_length = 10000
    if len(body_text) > max_body_length:
        body_text = body_text[:max_body_length] + "..."
    
    return {
        "title": title_text,
        "description": description,
        "headings": headings[:20],  
        "links": links[:50], 
        "body_text": body_text,
        "total_links": len(links),
        "total_headings": len(headings)
    }


def detect_scam_patterns(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    red_flags = []
    green_flags = []
    score = 0
    
    full_text = f"{extracted_data['title']} {extracted_data['description']} {' '.join(extracted_data['headings'])} {extracted_data['body_text']}"
    full_text_lower = full_text.lower()
    
    # ====== RED FLAGS - TIER 1: KRITIČNI (težina: +15) ======
    critical_scam_keywords = [
        'guaranteed profit', 'guaranteed returns', 'guaranteed income',
        'risk free investment', 'risk-free profit', 'no risk involved',
        'double your money', 'triple your investment', 'multiply your wealth',
        'get rich overnight', 'instant wealth', 'overnight millionaire',
        'secret loophole', 'secret method', 'hidden formula',
        'ponzi', 'pyramid scheme', 'multi-level marketing opportunity',
        'recruit members', 'downline', 'upline commission',
        'investment opportunity of a lifetime', 'once in a lifetime chance',
        'bank transfer required', 'wire transfer only', 'send bitcoin',
        'act within 24 hours', 'offer expires today', 'last chance',
        'government grant money', 'free government money', 'unclaimed funds',
        'nigerian prince', 'foreign investor', 'offshore account'
    ]
    
    for keyword in critical_scam_keywords:
        if keyword in full_text_lower:
            red_flags.append(f"🚨 CRITICAL: '{keyword}'")
            score += 15
    
    # ====== RED FLAGS - TIER 2: VISOKI RIZIK (težina: +10) ======
    high_risk_keywords = [
        'get rich quick', 'make money fast', 'easy money online',
        'passive income system', 'automated income', 'money while you sleep',
        'financial freedom', 'quit your job', 'fire your boss',
        'unlimited earning potential', 'unlimited income', 'sky is the limit',
        'exclusive opportunity', 'limited spots available', 'exclusive access',
        'crypto signals', 'trading bot guaranteed', 'forex guaranteed',
        'work from home opportunity', 'home based business', 'laptop lifestyle',
        'no experience required', 'no skills needed', 'anyone can do this',
        'click here to claim', 'claim your reward', 'you have been selected',
        'congratulations you won', 'winner notification', 'prize claim',
        'binary options', 'high yield investment', 'hyip',
        'network marketing', 'mlm opportunity', 'residual income opportunity'
    ]
    
    for keyword in high_risk_keywords:
        if keyword in full_text_lower:
            red_flags.append(f"⚠️ HIGH RISK: '{keyword}'")
            score += 10
    
    # ====== RED FLAGS - TIER 3: SUMNJIIVI (težina: +5) ======
    suspicious_keywords = [
        'limited time offer', 'act now', 'hurry up', 'dont miss out',
        'special discount', 'exclusive deal', 'members only',
        'crypto investment', 'cryptocurrency trading', 'nft investment',
        'high returns', 'impressive returns', 'exceptional roi',
        'earn thousands', 'make thousands', 'extra income',
        'side hustle', 'supplemental income', 'additional revenue',
        'proven system', 'tested method', 'foolproof strategy',
        'as seen on tv', 'celebrity endorsed', 'trusted by millions',
        'free trial', 'no credit card required', 'risk free trial',
        'money back guarantee', '100% satisfaction', 'full refund',
        'testimonials', 'success stories', 'real results',
        'join thousands', 'thousands of members', 'growing community'
    ]
    
    for keyword in suspicious_keywords:
        if keyword in full_text_lower:
            red_flags.append(f"⚡ SUSPICIOUS: '{keyword}'")
            score += 5
    
    # ====== GREEN FLAGS - TRUST SIGNALS ======
    trust_signals = {
        # Legal & Compliance (težina: -8)
        'legal': [
            'privacy policy', 'terms of service', 'terms and conditions',
            'cookie policy', 'gdpr compliant', 'data protection',
            'legal notice', 'disclaimer', 'compliance'
        ],
        # Company Info (težina: -7)
        'company': [
            'about us', 'our team', 'company history',
            'registered company', 'registration number', 'vat number',
            'business address', 'headquarters', 'office location'
        ],
        # Contact & Support (težina: -6)
        'contact': [
            'contact us', 'customer support', 'customer service',
            'help center', 'support team', 'contact form',
            'phone number', 'email address', 'live chat'
        ],
        # Certifications (težina: -10)
        'certifications': [
            'certified', 'accredited', 'licensed', 'regulated',
            'authorized dealer', 'official partner', 'verified',
            'ssl certificate', 'secure checkout', 'encrypted'
        ],
        # Transparency (težina: -7)
        'transparency': [
            'refund policy', 'return policy', 'money back',
            'pricing', 'transparent fees', 'no hidden costs',
            'faq', 'frequently asked questions', 'how it works'
        ]
    }
    
    for category, keywords in trust_signals.items():
        weight_map = {
            'legal': -8, 'company': -7, 'contact': -6,
            'certifications': -10, 'transparency': -7
        }
        weight = weight_map[category]
        
        for keyword in keywords:
            if keyword in full_text_lower:
                green_flags.append(f"✅ {category.upper()}: '{keyword}'")
                score += weight  
                break  
    
    # ====== STRUKTURNE ANALIZE ======
    
    # 1. External links spam (previše = sumnjivo)
    external_links = [l for l in extracted_data['links'] if l['href'].startswith('http')]
    if len(external_links) > 100:
        red_flags.append(f" Excessive external links: {len(external_links)}")
        score += 20
    elif len(external_links) > 50:
        red_flags.append(f" Many external links: {len(external_links)}")
        score += 10
    
    # 2. Contact info presence (email + phone = trust)
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    has_email = bool(re.search(email_pattern, full_text))
    has_phone = bool(re.search(phone_pattern, full_text))
    
    if has_email:
        green_flags.append(" Email contact found")
        score -= 5
    if has_phone:
        green_flags.append(" Phone contact found")
        score -= 5
    
    if not has_email and not has_phone:
        red_flags.append(" No contact information found")
        score += 12
    
    # 3. UPPERCASE spam detection (SCREAMING = spam)
    uppercase_chars = sum(1 for c in full_text if c.isupper())
    total_letters = sum(1 for c in full_text if c.isalpha())
    uppercase_ratio = uppercase_chars / max(total_letters, 1)
    
    if uppercase_ratio > 0.4:
        red_flags.append(f" EXCESSIVE UPPERCASE: {uppercase_ratio*100:.1f}% (aggressive marketing)")
        score += 15
    elif uppercase_ratio > 0.25:
        red_flags.append(f" High uppercase: {uppercase_ratio*100:.1f}%")
        score += 8
    
    # 4. Exclamation marks spam (!!!! = hype)
    exclamation_count = full_text.count('!')
    text_length_words = len(full_text.split())
    exclamation_density = exclamation_count / max(text_length_words, 1) * 100
    
    if exclamation_count > 20:
        red_flags.append(f"❗ Excessive exclamation marks: {exclamation_count} (hype indicator)")
        score += 12
    elif exclamation_count > 10:
        red_flags.append(f"❗ Many exclamation marks: {exclamation_count}")
        score += 6
    
    # 5. Dollar signs / money symbols spam
    money_symbols = full_text.count('$') + full_text.count('€') + full_text.count('£')
    if money_symbols > 15:
        red_flags.append(f" Excessive money symbols: {money_symbols}")
        score += 8
    
    # 6. Number spam (percentages, amounts - često u scam-ovima)
    number_pattern = r'\d{2,}'  # Brojevi sa 2+ cifre
    large_numbers = re.findall(number_pattern, full_text)
    if len(large_numbers) > 30:
        red_flags.append(f" Number spam detected: {len(large_numbers)} instances")
        score += 7
    
    # 7. Absence of legal pages
    has_privacy = 'privacy' in full_text_lower
    has_terms = 'terms' in full_text_lower or 'conditions' in full_text_lower
    
    if not has_privacy and not has_terms:
        red_flags.append("⚖️ Missing legal pages (privacy/terms)")
        score += 10
    
    # 8. Social proof manipulation check
    social_proof_words = ['thousands of customers', 'millions of users', 'trusted by thousands', 
                          'join millions', '10000+ members', 'thousands joined']
    for phrase in social_proof_words:
        if phrase in full_text_lower:
            red_flags.append(f"👥 Vague social proof: '{phrase}'")
            score += 6
            break
    
    return {
        "algorithmic_score": max(0, min(100, score)),
        "red_flags": red_flags,
        "green_flags": green_flags,
        "has_contact_info": has_email or has_phone,
        "metrics": {
            "external_links_count": len(external_links),
            "uppercase_ratio": round(uppercase_ratio * 100, 2),
            "exclamation_count": exclamation_count,
            "has_email": has_email,
            "has_phone": has_phone,
            "has_privacy_policy": has_privacy,
            "has_terms": has_terms
        }
    }


def extract_company_info(extracted_data: Dict[str, Any]) -> Dict[str, Any]:

    full_text = f"{extracted_data['title']} {extracted_data['description']} {' '.join(extracted_data['headings'])} {extracted_data['body_text']}"
    
    # Izvuci mogući naziv kompanije (jednostavna heuristika)
    company_patterns = [
        r'(?:company|corporation|corp|inc|ltd|llc)[:\s]+([A-Z][a-zA-Z\s&]+)',
        r'(?:about|welcome to)\s+([A-Z][a-zA-Z\s&]+)',
        r'©\s*\d{4}\s+([A-Z][a-zA-Z\s&]+)'
    ]
    
    company_name = extracted_data['title']  # Default
    for pattern in company_patterns:
        match = re.search(pattern, full_text)
        if match:
            company_name = match.group(1).strip()
            break
    
    product_keywords = [
        'investment', 'crypto', 'trading', 'course', 'training',
        'software', 'service', 'product', 'membership', 'subscription',
        'ebook', 'webinar', 'coaching', 'consulting', 'platform'
    ]
    
    products_found = []
    for keyword in product_keywords:
        if keyword in full_text.lower():
            products_found.append(keyword)
    
    return {
        "company_name": company_name[:100],  # Limit length
        "products_services": list(set(products_found))[:10],  # Unique, max 10
        "title": extracted_data['title']
    }


def build_search_query(extracted_data: Dict[str, Any], company_info: Dict[str, Any], scam_analysis: Dict[str, Any]) -> str:
    """
    Kreira query za Reddit search - JEDNOSTAVAN i FOKUSIRAN.
    """
    # Prioritet: Title (najčešće sadrži naziv kompanije/sajta)
    title = extracted_data.get('title', '').strip()
    
    # Očisti title od common suffixes
    clean_title = re.sub(r'\s*[-|–—].*$', '', title)  # Remove after dash
    clean_title = re.sub(r'\s+(home|homepage|official|website|online).*$', '', clean_title, flags=re.IGNORECASE)
    clean_title = clean_title.strip()
    
    # Ako je title dobar, koristi ga
    if clean_title and len(clean_title) > 3 and len(clean_title) < 100:
        query = f"{clean_title} scam reviews reddit"
    else:
        # Fallback na description ili body text
        description = extracted_data.get('description', '').strip()
        if description and len(description) > 20:
            query = f"{description[:150]} scam or legit"
        else:
            # Last resort - body text
            body = extracted_data.get('body_text', '').strip()
            query = f"{body[:150]} reviews"
    
    # Dodaj ključne reči ako su relevantne
    products = company_info.get('products_services', [])
    if 'crypto' in products or 'investment' in products or 'trading' in products:
        query += " investment platform"
    
    # Limit na 300 karaktera
    if len(query) > 300:
        query = query[:300]
    
    return query.strip()


def analyze_html_with_llm(extracted_data: Dict[str, Any], scam_analysis: Dict[str, Any], company_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM analiza HTML sadržaja
    """
    context = f"""WEBSITE CONTENT ANALYSIS REQUEST

Title: {extracted_data['title']}
Description: {extracted_data['description']}

Main Headings:
{chr(10).join(extracted_data['headings'][:10])}

Company/Brand: {company_info['company_name']}
Products/Services: {', '.join(company_info['products_services'])}

Body Text Preview:
{extracted_data['body_text'][:2000]}

Algorithmic Detection:
- Scam Score: {scam_analysis['algorithmic_score']}/100
- Red Flags: {', '.join(scam_analysis['red_flags'][:5])}
- Green Flags: {', '.join(scam_analysis['green_flags'][:5])}
- Contact Info Present: {scam_analysis['has_contact_info']}
"""

    system_prompt = """You are an expert web fraud analyst. Analyze this website content for scam indicators.

Return JSON with:
{
  "scam_score": 0-100 (0=legitimate, 100=definite scam),
  "confidence": 0-100,
  "summary": "2-3 sentence overview",
  "red_flags": ["warning 1", "warning 2", ...],
  "green_flags": ["positive 1", ...],
  "key_points": ["finding 1", "finding 2", ...],
  "recommendation": "AVOID/CAUTION/INVESTIGATE/SAFE",
  "reasoning": "detailed explanation"
}

Consider:
- Unrealistic promises (get rich quick, guaranteed returns)
- Lack of transparency (no company info, no contact)
- Pressure tactics (limited time, act now)
- Professional presentation vs content quality
- Presence of legitimate business information
"""

    try:
        response = grok_client.chat.completions.create(
            model=GROK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    
    except Exception as e:
        return {
            "scam_score": scam_analysis['algorithmic_score'],
            "confidence": 50,
            "summary": f"LLM analysis failed, using algorithmic score only. Error: {str(e)}",
            "red_flags": scam_analysis['red_flags'],
            "green_flags": scam_analysis['green_flags'],
            "key_points": [],
            "recommendation": "INVESTIGATE",
            "reasoning": f"Error: {str(e)}"
        }


def analyze_html_page(html_content: str) -> Dict[str, Any]:
    """
    Kompletna analiza HTML stranice - main funkcija
    """
    # 1. Ekstraktuj podatke iz HTML-a
    extracted_data = extract_text_from_html(html_content)
    
    # 2. Algoritmička detekcija scam pattern-a
    scam_analysis = detect_scam_patterns(extracted_data)
    
    # 3. Ekstraktuj company info
    company_info = extract_company_info(extracted_data)
    
    # 4. LLM analiza
    llm_analysis = analyze_html_with_llm(extracted_data, scam_analysis, company_info)
    
    # 5. Build search query
    search_query = build_search_query(extracted_data, company_info, scam_analysis)
    
    return {
        "extracted_data": {
            "title": extracted_data['title'],
            "description": extracted_data['description'],
            "headings_count": extracted_data['total_headings'],
            "links_count": extracted_data['total_links']
        },
        "company_info": company_info,
        "algorithmic_analysis": scam_analysis,
        "llm_preliminary_analysis": llm_analysis,
        "search_query": search_query
    }
