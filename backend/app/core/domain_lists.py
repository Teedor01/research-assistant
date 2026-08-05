"""Curated domain signal lists. Kept separate from config.py since these are
data, not tunable runtime settings... edit this file directly to adjust."""

HIGH_AUTHORITY_SUFFIXES = (".gov", ".edu")

HIGH_AUTHORITY_DOMAINS = {
    "w3.org", "ietf.org", "iso.org",
    "docs.python.org", "developer.mozilla.org", "docs.microsoft.com",
    "kubernetes.io", "docs.docker.com",
}

KNOWN_TECHNICAL_DOMAINS = {
    "arxiv.org", "ieee.org", "acm.org",
    "engineering.fb.com", "netflixtechblog.com", "aws.amazon.com",
    "cloud.google.com", "research.google", "openai.com", "anthropic.com",
    "stackoverflow.com", "github.com",
}

LOW_QUALITY_DOMAIN_PATTERNS = (
    "content-farm", "articles-hub", "listicle",  # illustrative — extend as observed
)