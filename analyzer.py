"""
Main analysis orchestrator for Financial News Simplifier.
Coordinates news parsing, AI processing, demo mode execution, and database persistence.
"""

from typing import Dict, Any, Optional, Tuple
from config import is_api_key_configured
from news_parser import extract_article_from_url, clean_article_text
from utils.validators import validate_article_text, validate_analysis_payload
from ai_service import analyze_with_ai
from database import save_analysis
from modules.financial_terms import extract_glossary_terms_from_text


# Predefined realistic demo articles for instant testing and evaluation
DEMO_ARTICLES = {
    "rbi_monetary_policy": {
        "title": "RBI Keeps Repo Rate Unchanged at 6.50% Amid Persistent Food Inflation Pressures",
        "category": "Monetary Policy & Banking",
        "text": """MUMBAI — The Reserve Bank of India's Monetary Policy Committee (MPC), headed by Governor Shaktikanta Das, on Thursday decided to keep the benchmark repo rate unchanged at 6.50% for the eighth consecutive meeting. The decision was backed by a 4-to-2 majority among committee members, who reiterated the central bank's focus on remaining 'withdrawal of accommodation' to ensure that retail inflation aligns durably with the 4.0% target while supporting economic growth.

Governor Das emphasized that while headline Consumer Price Index (CPI) inflation had moderated to 4.75% in May, volatile food prices continue to pose recurring risks to the overall inflation trajectory. High prices for pulses, vegetables, and cereals remain significant concerns for household budgets.

The RBI projected real GDP growth for the current fiscal year (FY25) at a robust 7.2%, driven by sustained rural demand recovery, a promising monsoon forecast, and high capacity utilization in the manufacturing sector. Commercial banks have largely passed on previous rate hikes, leading to higher deposit and lending rates across the banking system.

Market analysts noted that while major global central banks like the European Central Bank and Bank of Canada have commenced rate cuts, the RBI remains cautious due to domestic food price pressures and resilient economic expansion.""",
        "analysis": {
            "headline": "RBI Holds Interest Rate at 6.50% to Balance Growth and Inflation",
            "short_summary": "The Reserve Bank of India decided to keep its benchmark repo rate steady at 6.50% for the eighth straight meeting. The central bank raised its economic growth forecast to 7.2% while staying watchful over stubborn food price inflation.",
            "simple_explanation": "The Reserve Bank of India (India's central bank) decided not to change the interest rate at which it lends money to other banks. For regular people and businesses, this means loan interest rates and monthly EMIs on home or car loans are likely to stay steady for now. While India's overall economy is performing well and growing rapidly, the RBI is being cautious because everyday food prices like vegetables and pulses are still rising, which affects household budgets.",
            "key_points": [
                "What happened: The RBI Monetary Policy Committee voted 4-2 to keep the benchmark repo rate steady at 6.50%.",
                "Who is involved: RBI Governor Shaktikanta Das, the 6-member MPC, commercial banks, and Indian consumers.",
                "Why it matters: Interest rates determine the cost of loans, home loan EMIs, and returns on savings bank fixed deposits.",
                "Important numbers: Benchmark repo rate kept at 6.50%; GDP growth forecast raised to 7.2%; retail inflation at 4.75% against a 4.0% target.",
                "Possible business effect: Corporate borrowing costs remain stable; companies can plan capital expansion with predictable financing expenses.",
                "Possible consumer effect: Home, vehicle, and personal loan EMIs will not rise further immediately, but fixed deposit interest rates also stay flat.",
                "What remains uncertain: Future interest rate cuts depend heavily on monsoon rainfall and subsequent food grain harvests."
            ],
            "financial_terms": [
                {
                    "term": "Repo Rate",
                    "simple_definition": "The interest rate at which the central bank lends money to commercial banks for short periods.",
                    "context_in_article": "Held steady at 6.50%, determining benchmark borrowing costs across India."
                },
                {
                    "term": "Monetary Policy Committee (MPC)",
                    "simple_definition": "A specialized 6-member panel responsible for fixing the benchmark interest rate in India.",
                    "context_in_article": "Voted 4 to 2 to maintain current policy rates."
                },
                {
                    "term": "CPI (Consumer Price Index)",
                    "simple_definition": "An index measuring changes in prices paid by everyday consumers for common household goods.",
                    "context_in_article": "Stood at 4.75%, slightly above the RBI's target of 4.0%."
                },
                {
                    "term": "GDP (Gross Domestic Product)",
                    "simple_definition": "The total market value of all goods and services produced within the country.",
                    "context_in_article": "Forecast to grow at a healthy 7.2% rate for the fiscal year."
                }
            ],
            "entities": {
                "companies": [],
                "banks": ["Commercial Banks", "European Central Bank", "Bank of Canada"],
                "government_orgs": ["Monetary Policy Committee (MPC)"],
                "countries": ["India", "Canada"],
                "financial_institutions": ["Reserve Bank of India (RBI)"],
                "people": ["Shaktikanta Das"],
                "economic_indicators": ["Repo Rate (6.50%)", "CPI Inflation (4.75%)", "GDP Growth (7.2%)"]
            },
            "sector": "Banking & Macroeconomics",
            "possible_business_impact": "Stable interest rates allow manufacturing and service businesses to predict financing costs without unexpected spikes in debt servicing.",
            "possible_consumer_impact": "Household borrowers will likely see existing loan EMIs remain unchanged, although cost-of-living relief depends on whether food inflation cools down.",
            "possible_economic_impact": "The projected 7.2% growth rate suggests sustained economic momentum, supported by rural consumption and capital investment.",
            "possible_market_relevance": "Stock and bond markets tend to favor interest rate predictability; equity benchmarks may reflect steady corporate borrowing stability.",
            "sentiment": "Neutral",
            "confidence": 92,
            "uncertainties": [
                "Unpredictable weather and monsoon distribution affecting vegetable and pulse yields",
                "Timing of potential rate cuts by global central banks creating currency fluctuations",
                "Pace of international crude oil price variations"
            ],
            "source_quality_notes": [
                "Official monetary policy announcement with verified vote count and statistics",
                "Clear quotes directly from central bank leadership"
            ]
        }
    },
    "tech_ai_investment": {
        "title": "Global Tech Leader Announces $10 Billion Cloud & AI Data Center Expansion Across Asia",
        "category": "Technology & Infrastructure",
        "text": """SINGAPORE — Global cloud and technology giant Hyperscale Corp on Wednesday announced an unprecedented $10 billion capital expenditure program to construct next-generation artificial intelligence data centers across India, Japan, and Southeast Asia over the next four years.

Chief Executive Officer Sarah Chen confirmed that the multi-billion-dollar investment will fund state-of-the-art semiconductor clusters, high-capacity submarine fiber cables, and dedicated renewable solar farms to power server infrastructure. The initiative is projected to generate over 12,000 high-skilled engineering and operational jobs in recipient metropolitan hubs.

The company's operating margin rose to 28% in the latest quarter, driven by a 35% surge in enterprise cloud revenue. However, executives cautioned that heavy upfront depreciation expenses and semiconductor procurement bottlenecks could weigh temporarily on short-term free cash flow.

Regional government officials welcomed the announcement, noting that domestic AI infrastructure is essential for national digital competitiveness and secure sovereign cloud storage.""",
        "analysis": {
            "headline": "Tech Giant Commits $10 Billion to Expand AI Cloud Data Centers in Asia",
            "short_summary": "Hyperscale Corp has unveiled a $10 billion 4-year investment plan to build AI-ready data centers and clean energy infrastructure across Asia, creating an estimated 12,000 specialized jobs.",
            "simple_explanation": "A major technology company is spending $10 billion to build massive specialized computer centers (called data centers) across Asia. These facilities are needed to run artificial intelligence programs, cloud software, and internet services. While this requires a huge amount of upfront spending, it demonstrates strong confidence in the booming demand for AI technology and will bring high-paying technical jobs and greener energy solutions to the region.",
            "key_points": [
                "What happened: Hyperscale Corp announced a $10 billion capital investment program for AI data centers.",
                "Who is involved: Hyperscale Corp, CEO Sarah Chen, regional tech partners, and host country governments.",
                "Why it matters: Artificial intelligence requires immense computing power, and building local data centers speeds up services and secures data.",
                "Important numbers: $10 billion total capital expenditure over 4 years; 12,000 new jobs; 28% operating margin; 35% cloud revenue growth.",
                "Possible business effect: Suppliers of semiconductor chips, cooling systems, and renewable energy may see surging contract demand.",
                "Possible consumer effect: Faster internet services and localized AI tools for businesses and everyday users.",
                "What remains uncertain: Potential supply shortages of specialized computer chips and regulatory approval timelines for land and power grids."
            ],
            "financial_terms": [
                {
                    "term": "Capital Expenditure (CapEx)",
                    "simple_definition": "Money spent by a company to acquire, upgrade, and maintain physical assets such as buildings, servers, and technology.",
                    "context_in_article": "The $10 billion spending program to build new physical data centers."
                },
                {
                    "term": "Operating Margin",
                    "simple_definition": "The percentage of revenue left over after paying for variable costs of production like wages and raw materials.",
                    "context_in_article": "Reported at 28%, indicating healthy operational profitability."
                },
                {
                    "term": "Free Cash Flow",
                    "simple_definition": "The cash a company generates after accounting for cash outflows to support operations and maintain its capital assets.",
                    "context_in_article": "Noted as temporarily affected by heavy upfront data center investments."
                },
                {
                    "term": "Depreciation",
                    "simple_definition": "An accounting method of allocating the cost of a tangible asset over its useful physical life.",
                    "context_in_article": "Hardware and servers will incur ongoing depreciation costs."
                }
            ],
            "entities": {
                "companies": ["Hyperscale Corp"],
                "banks": [],
                "government_orgs": ["Regional Technology Ministries"],
                "countries": ["India", "Japan", "Singapore"],
                "financial_institutions": [],
                "people": ["Sarah Chen"],
                "economic_indicators": ["Capital Expenditure ($10B)", "Operating Margin (28%)", "Revenue Growth (35%)"]
            },
            "sector": "Technology & Cloud Computing",
            "possible_business_impact": "Local software development companies, enterprise clients, and cloud startups could gain access to lower-latency computing power.",
            "possible_consumer_impact": "Consumers may benefit from more responsive AI applications and enhanced employment opportunities in tech corridors.",
            "possible_economic_impact": "Direct foreign investment on this scale stimulates clean energy adoption and high-value digital manufacturing.",
            "possible_market_relevance": "Tech hardware and clean energy suppliers may witness positive investor sentiment, although high upfront CapEx can trim short-term dividend yields.",
            "sentiment": "Positive",
            "confidence": 90,
            "uncertainties": [
                "Availability of high-end AI GPU chips from global foundries",
                "Regional power grid stability and water cooling environmental approvals",
                "Geopolitical export control regulations regarding advanced compute clusters"
            ],
            "source_quality_notes": [
                "Corporate press release verified with detailed financial metric disclosures"
            ]
        }
    }
}


def get_demo_article_names() -> Dict[str, str]:
    """Return dictionary of demo key -> readable title."""
    return {k: v["title"] for k, v in DEMO_ARTICLES.items()}


def get_demo_article(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve demo article payload by its key."""
    return DEMO_ARTICLES.get(key)


def run_demo_analysis(demo_key: str = "rbi_monetary_policy") -> Tuple[bool, Dict[str, Any], str]:
    """
    Run an instant offline demonstration of the complete analysis pipeline.
    Saves to the local SQLite database and returns the validated result.
    """
    demo_item = DEMO_ARTICLES.get(demo_key) or DEMO_ARTICLES["rbi_monetary_policy"]
    article_text = demo_item["text"]
    analysis_data = demo_item["analysis"]

    # Validate against schema
    is_valid, validated_obj, err = validate_analysis_payload(analysis_data)
    final_dict = validated_obj.model_dump() if (is_valid and validated_obj) else analysis_data

    # Save to database
    try:
        save_analysis(
            analysis_data=final_dict,
            article_text=article_text,
            source_url="Built-in Demo Sample"
        )
    except Exception as e:
        # Database save failure should not break the demo UI
        print(f"Warning: Demo database save failed: {e}")

    return True, final_dict, ""


def process_article(
    input_text: str,
    source_url: Optional[str] = None,
    force_demo: bool = False,
    demo_key: str = "rbi_monetary_policy"
) -> Dict[str, Any]:
    """
    Main analysis pipeline:
    1. Check for force_demo or missing API key -> use Demo Mode
    2. Extract & clean text if URL supplied
    3. Validate text length
    4. Call AI service
    5. Save analysis to SQLite
    6. Return structured result
    """
    if force_demo:
        success, data, err = run_demo_analysis(demo_key)
        return {
            "success": success,
            "is_demo": True,
            "data": data,
            "error": err,
            "source_url": source_url or "Demo Mode",
            "article_text": DEMO_ARTICLES.get(demo_key, {}).get("text", "")
        }

    # If no URL provided and no text provided
    if not input_text and not source_url:
        return {
            "success": False,
            "is_demo": False,
            "data": {},
            "error": "Please provide article text or a valid URL to analyze.",
            "source_url": None,
            "article_text": ""
        }

    # Step 1: Extract if URL is provided
    target_text = input_text
    extracted_title = ""

    if source_url:
        extracted = extract_article_from_url(source_url)
        if not extracted["success"]:
            return {
                "success": False,
                "is_demo": False,
                "data": {},
                "error": extracted["error"],
                "source_url": source_url,
                "article_text": ""
            }
        target_text = extracted["text"]
        extracted_title = extracted["title"]
    else:
        target_text = clean_article_text(input_text)

    # Step 2: Validate text length
    is_valid, validation_msg = validate_article_text(target_text)
    if not is_valid:
        return {
            "success": False,
            "is_demo": False,
            "data": {},
            "error": validation_msg,
            "source_url": source_url,
            "article_text": target_text
        }

    # Step 3: Check API key availability
    if not is_api_key_configured():
        return {
            "success": False,
            "is_demo": False,
            "data": {},
            "error": (
                "OpenAI API key is not configured. Add it to your .env file or "
                "click 'Run Demo Analysis' to test the full application."
            ),
            "source_url": source_url,
            "article_text": target_text
        }

    # Step 4: AI Analysis
    ai_success, analysis_data, ai_error = analyze_with_ai(target_text)
    if not ai_success:
        return {
            "success": False,
            "is_demo": False,
            "data": {},
            "error": ai_error,
            "source_url": source_url,
            "article_text": target_text
        }

    # If headline was empty, fallback to extracted title
    if extracted_title and not analysis_data.get("headline"):
        analysis_data["headline"] = extracted_title

    # Supplement terms from local glossary if AI identified few terms
    if len(analysis_data.get("financial_terms", [])) < 2:
        extra_terms = extract_glossary_terms_from_text(target_text)
        current_names = {t.get("term", "").lower() for t in analysis_data.get("financial_terms", [])}
        for et in extra_terms:
            if et["term"].lower() not in current_names:
                analysis_data.setdefault("financial_terms", []).append({
                    "term": et["term"],
                    "simple_definition": et["simple_definition"],
                    "context_in_article": "Mentioned in article context."
                })

    # Step 5: Save to SQLite
    try:
        save_analysis(
            analysis_data=analysis_data,
            article_text=target_text,
            source_url=source_url
        )
    except Exception as db_err:
        # Log or note error, but don't crash display of results
        print(f"Database save error: {db_err}")

    return {
        "success": True,
        "is_demo": False,
        "data": analysis_data,
        "error": None,
        "source_url": source_url,
        "article_text": target_text
    }
