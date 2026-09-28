"""
News parser and HTML article extractor for Financial News Simplifier.
Extracts title and main article text from URLs using requests and BeautifulSoup4.
"""

import re
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

from config import USER_AGENT, REQUEST_TIMEOUT, MAX_ARTICLE_CHARS
from utils.validators import validate_url, validate_article_text


def clean_article_text(raw_text: str) -> str:
    """
    Clean extracted text by removing extraneous whitespace, non-printable characters,
    inline ads remnants, and normalizing line breaks.
    """
    if not raw_text:
        return ""

    # Replace multiple spaces/tabs with single space
    cleaned = re.sub(r"[ \t]+", " ", raw_text)

    # Normalize paragraph breaks
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)

    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    # Truncate if exceedingly large
    if len(cleaned) > MAX_ARTICLE_CHARS:
        cleaned = cleaned[:MAX_ARTICLE_CHARS] + "\n...[Content truncated for analysis limit]"

    return cleaned


def extract_article_from_url(url: str) -> Dict[str, Any]:
    """
    Safely download and extract clean article text and title from a web URL.
    Handles HTTP errors, connection timeouts, and scraping obstacles gracefully.
    
    Returns a dictionary:
    {
        "success": bool,
        "title": str,
        "text": str,
        "error": Optional[str],
        "status_code": Optional[int]
    }
    """
    is_valid, validation_msg = validate_url(url)
    if not is_valid:
        return {
            "success": False,
            "title": "",
            "text": "",
            "error": validation_msg,
            "status_code": None,
        }

    target_url = validation_msg  # Contains normalized URL

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    try:
        response = requests.get(
            target_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )

        status_code = response.status_code

        if status_code == 403:
            return {
                "success": False,
                "title": "",
                "text": "",
                "error": "Access forbidden (HTTP 403). The website restricts automated access. Please copy and paste the article text manually.",
                "status_code": 403,
            }

        if status_code == 404:
            return {
                "success": False,
                "title": "",
                "text": "",
                "error": "Article page not found (HTTP 404). Please verify the link.",
                "status_code": 404,
            }

        if status_code >= 400:
            return {
                "success": False,
                "title": "",
                "text": "",
                "error": f"Unable to reach the web page (HTTP {status_code}). Please paste the article text manually.",
                "status_code": status_code,
            }

        html_content = response.text
        if not html_content or len(html_content.strip()) < 100:
            return {
                "success": False,
                "title": "",
                "text": "",
                "error": "The webpage returned empty or insufficient content. Please paste the article text manually.",
                "status_code": status_code,
            }

        soup = BeautifulSoup(html_content, "html.parser")

        # Strip non-content and layout tags
        for element in soup([
            "script", "style", "noscript", "svg", "header", "footer",
            "nav", "aside", "form", "button", "iframe", "figure", "figcaption"
        ]):
            element.decompose()

        # Extract Title
        title = ""
        og_title = soup.find("meta", property="og:title")
        twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
        h1_tag = soup.find("h1")

        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        elif twitter_title and twitter_title.get("content"):
            title = twitter_title["content"].strip()
        elif h1_tag and h1_tag.get_text():
            title = h1_tag.get_text().strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Extract main text
        article_candidates = (
            soup.find("article") or
            soup.find(attrs={"itemprop": "articleBody"}) or
            soup.find(class_=re.compile(r"article[-_]?body|story[-_]?content|post[-_]?content|entry[-_]?content", re.I)) or
            soup.find("main")
        )

        paragraphs = []
        if article_candidates:
            p_tags = article_candidates.find_all("p")
            paragraphs = [p.get_text(separator=" ", strip=True) for p in p_tags if len(p.get_text(strip=True)) > 20]

        # Fallback to all page paragraphs if container wasn't identified
        if not paragraphs:
            all_p = soup.find_all("p")
            paragraphs = [p.get_text(separator=" ", strip=True) for p in all_p if len(p.get_text(strip=True)) > 25]

        combined_text = "\n\n".join(paragraphs)
        cleaned_text = clean_article_text(combined_text)

        # Validate extracted content length
        is_sufficient, err_msg = validate_article_text(cleaned_text)
        if not is_sufficient:
            return {
                "success": False,
                "title": title,
                "text": cleaned_text,
                "error": f"Unable to extract sufficient article text from this website ({err_msg}). Many news sites render via JavaScript or enforce paywalls. Please paste the article text manually.",
                "status_code": status_code,
            }

        return {
            "success": True,
            "title": title or "Extracted Financial Article",
            "text": cleaned_text,
            "error": None,
            "status_code": status_code,
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "title": "",
            "text": "",
            "error": "The website request timed out. Please check your internet connection or paste the article text manually.",
            "status_code": None,
        }
    except requests.exceptions.SSLError:
        return {
            "success": False,
            "title": "",
            "text": "",
            "error": "SSL certificate verification failed for this website. Please paste the article text manually.",
            "status_code": None,
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "title": "",
            "text": "",
            "error": f"Could not connect to the website ({str(e)}). Please paste the article text manually.",
            "status_code": None,
        }
    except Exception as e:
        return {
            "success": False,
            "title": "",
            "text": "",
            "error": f"An unexpected error occurred while parsing the article: {str(e)}. Please paste the article text manually.",
            "status_code": None,
        }
