from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    "zip",
    "mov",
    "country",
    "kim",
    "gq",
    "tk",
    "ml",
    "ga",
    "cf",
    "work",
}


@dataclass
class SafetyResult:
    is_safe: bool
    warnings: list[str]


def analyze_url(url: str) -> SafetyResult:
    warnings: list[str] = []
    parsed = urlparse(url.strip())

    if parsed.scheme not in {"http", "https"}:
        warnings.append("URL is not HTTP/HTTPS.")

    if parsed.scheme == "http":
        warnings.append("Connection is not encrypted (HTTP).")

    hostname = parsed.hostname or ""
    netloc = parsed.netloc or ""

    if "@" in netloc:
        warnings.append("URL contains username/password segment.")

    if hostname.startswith("xn--") or ".xn--" in hostname:
        warnings.append("Domain uses punycode and may be deceptive.")

    if hostname:
        try:
            ip_address(hostname)
            warnings.append("URL points to a raw IP address.")
        except ValueError:
            pass

    if hostname:
        labels = hostname.split(".")
        if len(labels) > 4:
            warnings.append("Domain has many subdomains.")

        tld = labels[-1].lower() if labels else ""
        if tld in SUSPICIOUS_TLDS:
            warnings.append(f"Top-level domain .{tld} is commonly abused.")

        if len(hostname) > 60:
            warnings.append("Domain is unusually long.")

    if len(parsed.query) > 200:
        warnings.append("URL query string is unusually long.")

    return SafetyResult(is_safe=len(warnings) == 0, warnings=warnings)
