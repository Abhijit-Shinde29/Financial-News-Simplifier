"""
AI Service module for Financial News Simplifier.
Interacts with the OpenAI API using the official SDK, enforces strict ethical
and educational guidelines, requests structured JSON output, and validates schemas.
"""

import json
from typing import Dict, Any, Tuple
from openai import OpenAI, OpenAIError, AuthenticationError, RateLimitError, APIConnectionError

from config import OPENAI_API_KEY, OPENAI_MODEL, is_api_key_configured
from utils.validators import validate_analysis_payload, AnalysisResult


# Prompt instructing the AI with strict educational and non-advisory constraints
SYSTEM_PROMPT = """You are a senior financial analyst and educator specialized in simplifying complex financial news for students, beginners, and general readers.

Your task is to analyze the provided financial news article and output a strictly formatted JSON object adhering to the schema specified below.

MANDATORY RULES & ETHICAL GUIDELINES:
1. EDUCATIONAL PURPOSE ONLY: You must NEVER provide personalized investment advice, buy/sell recommendations, trading calls, price targets, or guaranteed predictions.
2. DO NOT HALLUCINATE: Rely strictly on the facts, statistics, numbers, quotes, and names explicitly present in the provided article. Do not invent details.
3. PRESERVE ACCURACY: Retain all dates, monetary amounts, percentages, and company names exactly as reported.
4. DISTINGUISH FACTS FROM OPINIONS: Clearly distinguish factual events from analyst quotes, speculation, or executive projections.
5. NEUTRAL, PROBABILISTIC LANGUAGE: For impact and market relevance, avoid deterministic claims. Always use cautious phrasing such as: "may affect", "could influence", "the article suggests", "possible relevance", "remains uncertain".
6. IF INSUFFICIENT DATA: If the article lacks context on any aspect, state explicitly "Insufficient information in source text".
7. SIMPLIFY COMPLEX JARGON: In the 'simple_explanation' and 'financial_terms' fields, write in everyday conversational English that a high school student or complete beginner can easily understand without losing the core financial truth.

JSON SCHEMA REQUIREMENT:
You must respond with valid JSON only, using this exact structure:
{
    "headline": "Clear, informative simplified headline",
    "short_summary": "2-3 sentence executive summary explaining what happened",
    "simple_explanation": "Beginner-friendly narrative explaining the event in plain words (around 80-150 words)",
    "key_points": [
        "What happened: ...",
        "Who is involved: ...",
        "Why it matters: ...",
        "Important figures/numbers: ...",
        "Possible business effect: ...",
        "Possible consumer effect: ...",
        "What remains uncertain: ..."
    ],
    "financial_terms": [
        {
            "term": "Term Name (e.g., Repo Rate)",
            "simple_definition": "Plain language explanation",
            "context_in_article": "How this specific term is used in this article"
        }
    ],
    "entities": {
        "companies": ["Name 1", "Name 2"],
        "banks": ["Bank 1"],
        "government_orgs": ["Org 1"],
        "countries": ["Country 1"],
        "financial_institutions": ["Institution 1"],
        "people": ["Person 1"],
        "economic_indicators": ["Indicator 1"]
    },
    "sector": "Sector name (e.g. Banking, Technology, Energy, Macroeconomics, Automotive)",
    "possible_business_impact": "Neutral explanation of how businesses in the sector or economy may be affected",
    "possible_consumer_impact": "Neutral explanation of potential effects on individual consumers, loans, prices, or jobs",
    "possible_economic_impact": "Neutral explanation of potential broader macroeconomic implications",
    "possible_market_relevance": "Neutral explanation of how financial markets, investors, or asset classes might view this news",
    "sentiment": "Positive" | "Negative" | "Neutral" | "Mixed" | "Uncertain",
    "confidence": 85,
    "uncertainties": [
        "First major unknown or missing variable from the article",
        "Second factor depending on future regulatory or economic conditions"
    ],
    "source_quality_notes": [
        "Assessment of factual reporting vs opinion content in the text"
    ]
}
"""


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client instance with the configured API key."""
    if not is_api_key_configured():
        raise ValueError(
            "OpenAI API key is not configured. Please add your OPENAI_API_KEY in the .env file."
        )
    return OpenAI(api_key=OPENAI_API_KEY)


def analyze_with_ai(article_text: str, custom_model: str = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    Call OpenAI API to simplify and analyze the provided financial news article.
    
    Returns:
    (success: bool, analysis_data: dict, error_message: str)
    """
    if not is_api_key_configured():
        return (
            False,
            {},
            "OpenAI API key is not configured. Add it to your .env file or activate Demo Mode."
        )

    model_to_use = custom_model or OPENAI_MODEL

    try:
        client = get_openai_client()

        user_content = f"Please analyze this financial news article:\n\n{article_text}"

        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # Low temperature for factual precision
        )

        raw_output = response.choices[0].message.content
        if not raw_output:
            return False, {}, "OpenAI API returned an empty response. Please retry."

        try:
            parsed_json = json.loads(raw_output)
        except json.JSONDecodeError as je:
            return False, {}, f"Failed to parse AI JSON response: {str(je)}"

        # Validate with Pydantic
        is_valid, validated_obj, val_err = validate_analysis_payload(parsed_json)
        if not is_valid or not validated_obj:
            # Fall back to using parsed_json directly if minor field deviations exist
            return True, parsed_json, f"Partial schema validation: {val_err}"

        return True, validated_obj.model_dump(), ""

    except AuthenticationError:
        return (
            False,
            {},
            "OpenAI Authentication Failed: The API key provided is invalid or expired. Check your .env file."
        )
    except RateLimitError:
        return (
            False,
            {},
            "OpenAI Rate Limit Exceeded: You have hit the rate limit or quota on your OpenAI account. Please check your billing or quota."
        )
    except APIConnectionError:
        return (
            False,
            {},
            "Network Connection Error: Could not connect to OpenAI API servers. Please check your internet connection."
        )
    except OpenAIError as oe:
        return False, {}, f"OpenAI API Error: {str(oe)}"
    except Exception as e:
        return False, {}, f"Unexpected AI analysis error: {str(e)}"
