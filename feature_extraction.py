
import re
import math
import ipaddress
from collections import Counter
from urllib.parse import urlparse

import tldextract


def extract_features(url):

    # Basic input validation
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Please enter a URL.")

    url = url.strip()

    # Reject spaces inside URL
    if any(char.isspace() for char in url):
        raise ValueError("URL must not contain spaces.")

    # Add scheme if missing
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url

    parsed = urlparse(url)

    # Allow only HTTP and HTTPS
    if parsed.scheme.lower() not in ["http", "https"]:
        raise ValueError("Only HTTP and HTTPS URLs are supported.")

    hostname = (parsed.hostname or "").lower()

    if not hostname:
        raise ValueError("Invalid URL. Please enter a valid website URL.")

    # Validate port
    try:
        parsed.port
    except ValueError:
        raise ValueError("Invalid port number in URL.")

    # Check whether hostname is an IP address
    try:
        ipaddress.ip_address(hostname)
        is_ip = 1

    except ValueError:
        is_ip = 0

        # Validate domain format
        extracted = tldextract.extract(hostname)

        if (
            not extracted.domain
            or not extracted.suffix
            or "." not in hostname
            or len(hostname) > 253
        ):
            raise ValueError("Invalid domain. Please enter a valid website URL.")

    # Extract domain and TLD
    extracted = tldextract.extract(hostname)

    domain = extracted.domain
    tld = extracted.suffix
    subdomain = extracted.subdomain

    # URL character counts
    url_len = len(url)
    letter_cnt = sum(c.isalpha() for c in url)
    digit_cnt = sum(c.isdigit() for c in url)
    special_cnt = sum(not c.isalnum() for c in url)

    # Ratios
    letter_ratio = letter_cnt / url_len if url_len else 0
    digit_ratio = digit_cnt / url_len if url_len else 0
    spec_ratio = special_cnt / url_len if url_len else 0

    # Shannon entropy
    counts = Counter(url)

    entropy = -sum(
        (count / url_len) * math.log2(count / url_len)
        for count in counts.values()
    ) if url_len else 0

    # Extract all 22 model features
    features = {
        "url_len": url_len,
        "dom_len": len(domain + "." + tld) if tld else len(domain),
        "is_ip": is_ip,
        "tld_len": len(tld),
        "subdom_cnt": len(subdomain.split(".")) if subdomain else 0,
        "letter_cnt": letter_cnt,
        "digit_cnt": digit_cnt,
        "special_cnt": special_cnt,
        "eq_cnt": url.count("="),
        "qm_cnt": url.count("?"),
        "amp_cnt": url.count("&"),
        "dot_cnt": url.count("."),
        "dash_cnt": url.count("-"),
        "under_cnt": url.count("_"),
        "letter_ratio": letter_ratio,
        "digit_ratio": digit_ratio,
        "spec_ratio": spec_ratio,
        "is_https": int(parsed.scheme.lower() == "https"),
        "slash_cnt": url.count("/"),
        "entropy": entropy,
        "path_len": len(parsed.path),
        "query_len": len(parsed.query)
    }

    return features
