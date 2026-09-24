"""Simple fetch helpers for job-posting URLs."""

import json
import re
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


def _is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _extract_linkedin_job_id(url: str) -> str:
    patterns = [
        r"/jobs(?:/view|/listing|/details)?/?(?:[^/]+/)?(\d+)",
        r"[?&](?:currentJobId|jobId|job_id)=(\d+)",
        r"/jobs/view/(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract a LinkedIn job ID from: {url}")


def _build_jina_reader_url(url: str) -> str:
    base = url.strip().rstrip("/")
    if base.startswith("https://"):
        return "https://r.jina.ai/http://" + base[len("https://") :]
    if base.startswith("http://"):
        return "https://r.jina.ai/http://" + base[len("http://") :]
    return f"https://r.jina.ai/http://{base}"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _extract_text_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    candidates: list[str] = []

    for selector in [
        "#job-details",
        ".jobs-description__content",
        ".description__text",
        ".jobs-box__group",
        "article",
        "main",
        "body",
    ]:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if text:
                candidates.append(text)

    for script in soup.find_all("script", type="application/ld+json"):
        raw = script.string or script.get_text()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue

        def walk(value: Any) -> list[str]:
            results: list[str] = []
            if isinstance(value, dict):
                if value.get("@type") == "JobPosting" and value.get("description"):
                    results.append(str(value["description"]))
                for child in value.values():
                    results.extend(walk(child))
            elif isinstance(value, list):
                for item in value:
                    results.extend(walk(item))
            return results

        for item in walk(data):
            if item:
                candidates.append(item)

    for meta in soup.find_all("meta"):
        if meta.get("property") in {"og:title", "og:description"}:
            content = meta.get("content")
            if content:
                candidates.append(content)

    text = "\n\n".join(candidates)
    text = _clean_text(text)
    return text or None


def _looks_like_job_description(text: str) -> bool:
    normalized = text.lower()
    if len(normalized) < 80:
        return False
    keywords = [
        "responsibilities",
        "qualifications",
        "requirements",
        "experience",
        "skills",
        "job description",
        "about the role",
        "what you'll do",
        "what you will do",
        "we are looking for",
        "apply now",
    ]
    return any(keyword in normalized for keyword in keywords) or "salary" in normalized


def _fetch_url(url: str) -> requests.Response:
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response


def get_job_text(url: str) -> str:
    """Fetch and normalize a LinkedIn job posting into readable plain text."""
    job_url = (url or "").strip()
    if not _is_valid_url(job_url):
        raise ValueError(f"Invalid job URL: {url!r}")

    try:
        job_id = _extract_linkedin_job_id(job_url)
    except ValueError as exc:
        raise RuntimeError(f"Could not read job information from URL: {job_url}") from exc

    guest_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    candidate_urls = [guest_url, _build_jina_reader_url(job_url)]

    for candidate in candidate_urls:
        try:
            response = _fetch_url(candidate)
            text = _extract_text_from_html(response.text) if "linkedin.com/jobs-guest" in candidate else _clean_text(response.text)
            if text and _looks_like_job_description(text):
                return text
        except (requests.RequestException, ValueError):
            continue

    raise RuntimeError(f"Unable to read job description from URL: {job_url}")


def fetch_job_description(url: str) -> str:
    """Backward-compatible alias for URL-based job text retrieval."""
    return get_job_text(url)
