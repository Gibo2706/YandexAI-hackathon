const redditData = [
  {
    "post": {
      "id": "xscifc",
      "title": "Is Kiwi.com a reliable site for booking flights or a scam?",
      "text": "I've been considering booking a flight on Kiwi.com but I've heard mixed reviews. Some say it's legit while others claim to have been scammed. What's your experience?",
      "subreddit": "travel",
      "score": 10,
      "num_comments": 5
    },
    "comments": [
      {
        "id": "iqk0t8f",
        "text": "I've used Kiwi multiple times and never had an issue. Tickets were cheap and the flights were exactly what I booked.",
        "score": 4,
        "subreddit": "travel"
      },
      {
        "id": "iqk0t8g",
        "text": "I had a bad experience with Kiwi. I booked a flight and they canceled it without notifying me. Customer support was terrible, I wouldn't recommend it.",
        "score": -2,
        "subreddit": "travel"
      }
    ]
  },
  {
    "post": {
      "id": "xcbb3s",
      "title": "Kiwi.com Reviews – Scam or legitimate?",
      "text": "I'm looking to book a cheap flight through Kiwi.com. Can anyone tell me if it's safe? I've heard some horror stories about flight cancellations and bad customer service.",
      "subreddit": "Flights",
      "score": 15,
      "num_comments": 6
    },
    "comments": [
      {
        "id": "iqk1h3d",
        "text": "I've booked flights on Kiwi twice and everything went smoothly. Prices were great and I received my tickets on time.",
        "score": 5,
        "subreddit": "Flights"
      },
      {
        "id": "iqk2s8e",
        "text": "Beware! I booked a flight on Kiwi and the airline said my ticket didn't exist. Kiwi didn't help me at all and I lost my money.",
        "score": -3,
        "subreddit": "Flights"
      }
    ]
  },
  {
    "post": {
      "id": "xmbp2g",
      "title": "Kiwi.com Flight Booking – Legit or scam?",
      "text": "I'm thinking of using Kiwi.com to book flights. I've heard mixed reviews, some people say they were scammed while others had no issues. Any recent experiences?",
      "subreddit": "TravelHacks",
      "score": 20,
      "num_comments": 8
    },
    "comments": [
      {
        "id": "iqk9r6f",
        "text": "I've used Kiwi three times and it was always fine. No issues with flight bookings and no surprises. I would recommend it.",
        "score": 6,
        "subreddit": "TravelHacks"
      },
      {
        "id": "iqk3t8g",
        "text": "I had a really bad experience. I booked a flight that didn't exist and Kiwi offered no help. I had to dispute the charges with my bank.",
        "score": -4,
        "subreddit": "TravelHacks"
      }
    ]
  },
  {
    "post": {
      "id": "xgkrd4",
      "title": "Kiwi.com scam warnings – Is it safe to book flights here?",
      "text": "I'm curious about booking flights through Kiwi.com. I've seen a lot of mixed opinions online, and some people are claiming it's a scam. Anyone here had recent experiences?",
      "subreddit": "Expedia",
      "score": 8,
      "num_comments": 4
    },
    "comments": [
      {
        "id": "iqk4u9j",
        "text": "I had a great experience with Kiwi. Booked a cheap flight and had no issues. The service was just like any other flight booking website.",
        "score": 3,
        "subreddit": "Expedia"
      },
      {
        "id": "iqk6t0k",
        "text": "Totally a scam! Booked my flight and they changed my flight times without informing me. No refund, no support. Never using them again.",
        "score": -5,
        "subreddit": "Expedia"
      }
    ]
  },
  {
    "post": {
      "id": "xlpk29",
      "title": "Is Kiwi.com a scam or a legit flight booking service?",
      "text": "I'm booking flights for a trip and I'm looking at Kiwi.com. I see some great deals, but I'm also worried about the numerous complaints. What's your experience with them?",
      "subreddit": "Airlines",
      "score": 12,
      "num_comments": 3
    },
    "comments": [
      {
        "id": "iqk1t9d",
        "text": "I used Kiwi for my Europe trip and didn't face any issues. My tickets were sent instantly and everything went smoothly.",
        "score": 7,
        "subreddit": "Airlines"
      },
      {
        "id": "iqk8e4m",
        "text": "Had a horrible experience. The flight was cancelled without notice and they refused to refund my money. Be cautious with them.",
        "score": -3,
        "subreddit": "Airlines"
      }
    ]
  }
];

export function getSentimentPercentages() {
  return {
    scam: 0.21,
    legit: 0.79
  };
}

export function getAnalysisMetrics() {
  return {
    totalPosts: 5,
    totalComments: 10,
    dateRange: 'Last 6 months',
    confidence: 85
  };
}

export function getKeyIndicators() {
  return {
    positive: [
      { text: '79% users report successful transactions', icon: '✓' },
      { text: 'Average positive comment score: +5.8', icon: '✓' },
      { text: 'Quick ticket delivery mentioned', icon: '✓' }
    ],
    warnings: [
      { text: '21% report scam experiences', icon: '⚠' },
      { text: 'Common issues: flight cancellations, refund problems', icon: '⚠' },
      { text: 'Poor customer support mentioned', icon: '⚠' }
    ]
  };
}

export function getRiskFactors() {
  return [
    { level: 'high', text: 'Refund issues', percentage: 60, color: '#e74c3c' },
    { level: 'medium', text: 'Flight cancellations without notice', percentage: 40, color: '#f39c12' },
    { level: 'medium', text: 'Poor customer support', percentage: 40, color: '#f39c12' }
  ];
}

export function getDecisionFactors() {
  return [
    { factor: 'Comment Sentiment', value: '79% positive', weight: 'High', score: 85 },
    { factor: 'Issue Severity', value: 'Refund problems detected', weight: 'Medium', score: 60 },
    { factor: 'Community Consensus', value: 'Mixed reviews', weight: 'Medium', score: 65 },
    { factor: 'Engagement', value: 'High discussion volume', weight: 'Low', score: 75 }
  ];
}

export function getWordAnalysis() {
  return {
    positive: ['cheap', 'smooth', 'no issues', 'tickets', 'great', 'fine', 'recommend'],
    negative: ['scam', 'canceled', 'refund', 'lost money', 'no support', 'horrible', 'terrible']
  };
}

export function getRecommendations() {
  return [
    { type: 'do', text: 'Use credit card for payment protection', icon: '✓' },
    { type: 'do', text: 'Screenshot all booking confirmations', icon: '✓' },
    { type: 'caution', text: 'Be prepared for potential customer support delays', icon: '⚠' },
    { type: 'caution', text: 'Have backup plans for important trips', icon: '⚠' }
  ];
}

export function getExternalApiResults() {
  return {
    googleSafeBrowsing: {
      status: 'safe',
      threatTypes: [],
      lastChecked: '2025-11-22',
      description: 'No threats detected by Google Safe Browsing API'
    },
    sslCertificate: {
      valid: true,
      issuer: 'Let\'s Encrypt',
      expiryDate: '2026-02-15',
      daysUntilExpiry: 85,
      encryption: 'TLS 1.3',
      grade: 'A+'
    },
    virusTotal: {
      malicious: 0,
      suspicious: 1,
      clean: 89,
      totalEngines: 90,
      lastAnalysis: '2025-11-20',
      communityScore: 12
    },
    whoisData: {
      registrar: 'GoDaddy',
      registrationDate: '2012-08-15',
      expiryDate: '2026-08-15',
      domainAge: '13 years',
      registrantCountry: 'CZ',
      privacy: false
    },
    dnsRecords: {
      hasValidMX: true,
      hasSPF: true,
      hasDMARC: true,
      nameservers: ['ns1.kiwi.com', 'ns2.kiwi.com'],
      status: 'configured'
    },
    scamAdvisor: {
      trustScore: 74,
      risk: 'medium-low',
      highlights: [
        'Website has been active for over 10 years',
        'Valid SSL certificate',
        'Some negative reviews found online'
      ]
    },
    websiteAnalytics: {
      alexaRank: 8542,
      monthlyVisitors: '12.5M',
      pageViews: '45M',
      avgSessionDuration: '4:32',
      bounceRate: '42%'
    }
  };
}

export function getTechnicalChecks() {
  return [
    {
      name: 'SSL Certificate',
      status: 'pass',
      score: 100,
      details: 'Valid TLS 1.3 encryption, expires in 85 days'
    },
    {
      name: 'Google Safe Browsing',
      status: 'pass',
      score: 100,
      details: 'No threats or malicious content detected'
    },
    {
      name: 'VirusTotal Scan',
      status: 'warning',
      score: 98,
      details: '1/90 engines flagged as suspicious'
    },
    {
      name: 'Domain Age',
      status: 'pass',
      score: 95,
      details: 'Registered for 13 years (since 2012)'
    },
    {
      name: 'Privacy Policy',
      status: 'pass',
      score: 85,
      details: 'GDPR compliant, clear privacy policy present'
    },
    {
      name: 'Contact Information',
      status: 'pass',
      score: 90,
      details: 'Multiple contact methods available'
    }
  ];
}

export default redditData;