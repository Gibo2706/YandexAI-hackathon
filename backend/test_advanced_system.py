"""
Test script za Advanced Scam Detection System.
Demonstrira sve nove feature-e.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_html_analysis():
    """Test HTML analiza endpoint-a"""
    print("\n" + "="*80)
    print("TEST 1: HTML ANALIZA")
    print("="*80)
    
    # Sample HTML - fake crypto investment site
    html_content = """
    <html>
    <head>
        <title>CryptoDoubler - Double Your Bitcoin in 24 Hours!</title>
        <meta name="description" content="Guaranteed profits! Send Bitcoin, get 2x back instantly!">
    </head>
    <body>
        <h1>AMAZING INVESTMENT OPPORTUNITY!</h1>
        <h2>Limited Time Offer - Act Now!</h2>
        <p>
            Join thousands of members making passive income with our proven system.
            No risk involved! 100% guaranteed returns! 
            
            Our exclusive cryptocurrency doubling platform uses a secret algorithm
            to guarantee profits. Send any amount of Bitcoin and receive double back
            within 24 hours. This is a once in a lifetime opportunity!
            
            Don't miss out! Only 50 spots remaining!
        </p>
        <h3>Testimonials</h3>
        <p>
            "I made $10,000 in one week!" - Anonymous User
            "This changed my life! Financial freedom!" - Happy Customer
        </p>
        <a href="http://suspicious-site.tk">Send Bitcoin Now!</a>
        <a href="http://scam-domain.ml">Join VIP Program!</a>
    </body>
    </html>
    """
    
    response = requests.post(
        f"{BASE_URL}/analyze-html",
        json={
            "html_content": html_content,
            "k": 20
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Response Status: {response.status_code}")
        print(f"\n📊 Generated Query: {data['query'][:100]}...")
        print(f"\n🏢 Company Info:")
        print(f"   Name: {data['company_info']['company_name']}")
        print(f"   Products: {', '.join(data['company_info']['products_services'])}")
        
        analysis = data['analysis']
        print(f"\n🎯 Analysis Results:")
        print(f"   Scam Score: {analysis['scam_score']}/100")
        print(f"   Confidence: {analysis['confidence']}/100")
        print(f"   Recommendation: {analysis['recommendation']}")
        print(f"   Algorithmic Score: {analysis['algorithmic_score']}/100")
        
        print(f"\n🚨 Red Flags ({len(analysis['red_flags'])}):")
        for flag in analysis['red_flags'][:5]:
            print(f"   • {flag}")
        
        if analysis.get('breakdown'):
            print(f"\n⚖️ Score Breakdown:")
            print(f"   HTML Score: {analysis['breakdown']['html_score']}")
            print(f"   Reddit Score: {analysis['breakdown'].get('reddit_score', 'N/A')}")
            print(f"   Strategy: {analysis['breakdown']['weight_strategy']}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_regular_search_with_preprocessing():
    """Test regular search sa preprocessingom"""
    print("\n" + "="*80)
    print("TEST 2: REGULAR SEARCH (sa preprocessingom)")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "query": "is coinbase a scam?",
            "k": 10
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {len(data)} discussions")
        
        # Check if enrichment data exists
        if data and 'enrichment' in data[0]:
            print(f"\n📊 First Discussion Enrichment:")
            enrichment = data[0]['enrichment']
            print(f"   Discussion Credibility: {enrichment['discussion_credibility']}/100")
            print(f"   Post Quality: {enrichment['post_quality']['quality_score']}/100")
            print(f"   Thread Consensus: {enrichment['thread_analysis']['consensus_level']}")
            print(f"   Scam Mentions: {enrichment['scam_analysis']['scam_mention_count']}")
            print(f"   Warning Count: {enrichment['scam_analysis']['warning_count']}")
    else:
        print(f"❌ Error: {response.status_code}")


def test_full_analysis():
    """Test full analysis sa svim preprocessing insights"""
    print("\n" + "="*80)
    print("TEST 3: FULL ANALYSIS (search + preprocessing + LLM)")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/full-analysis",
        json={
            "query": "bitcoin doubler scam",
            "k": 15
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Response Status: {response.status_code}")
        
        # Metadata
        metadata = data.get('metadata', {})
        print(f"\n📊 Metadata:")
        print(f"   Discussions: {metadata.get('num_discussions')}")
        print(f"   Avg Similarity: {metadata.get('avg_similarity', 0):.3f}")
        
        # Statistics
        stats = data.get('statistics', {})
        if stats:
            print(f"\n📈 Statistics:")
            print(f"   Total Discussions: {stats.get('total_discussions')}")
            
            sentiment = stats.get('sentiment_indicators', {})
            print(f"   Positive Comments: {sentiment.get('positive_comments')}")
            print(f"   Negative Comments: {sentiment.get('negative_comments')}")
        
        # LLM Analysis
        llm = data.get('llm_analysis', {})
        if llm:
            print(f"\n🤖 LLM Analysis:")
            print(f"   Scam Score: {llm.get('scam_score')}/100")
            print(f"   Confidence: {llm.get('confidence')}/100")
            print(f"   Recommendation: {llm.get('recommendation')}")
            print(f"   Summary: {llm.get('summary', '')[:200]}...")
            
            # Preprocessing insights (NOVO!)
            insights = llm.get('preprocessing_insights')
            if insights:
                print(f"\n💡 Preprocessing Insights:")
                print(f"   Avg Discussion Credibility: {insights.get('avg_discussion_credibility')}/100")
                print(f"   Total Scam Mentions: {insights.get('total_scam_mentions')}")
                print(f"   Community Consensus: {insights.get('community_consensus')}")
                print(f"   Keyword Risk Score: {insights.get('keyword_risk_score')}/100")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)


def test_health():
    """Test health endpoint"""
    print("\n" + "="*80)
    print("TEST 4: HEALTH CHECK")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Status: {data['status']}")
        print(f"   Index Ready: {data['index_ready']}")
        print(f"   Groq Ready: {data['groq_ready']}")
        print(f"\n📁 Files:")
        for file, exists in data['files'].items():
            status = "✅" if exists else "❌"
            print(f"   {status} {file}: {exists}")
    else:
        print(f"❌ Error: {response.status_code}")


if __name__ == "__main__":
    print("\n🚀 TESTING ADVANCED SCAM DETECTION SYSTEM")
    print("Make sure the API is running: python api/api.py")
    
    try:
        # Test health first
        test_health()
        
        # Test HTML analysis (new feature)
        test_html_analysis()
        
        # Test regular search with preprocessing
        test_regular_search_with_preprocessing()
        
        # Test full analysis with preprocessing insights
        test_full_analysis()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the server is running:")
        print("  cd backend")
        print("  python api/api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
