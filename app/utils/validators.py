from urllib.parse import urlparse

BLOCKED_HOSTS = frozenset({'localhost', '127.0.0.1', '::1', '0.0.0.0'})
ALLOWED_SCHEMES = frozenset({'http', 'https'})


def validate_url(url: str) -> bool:
    """Validate URL for safety (SSRF protection).

    Checks:
    - URL has scheme and netloc
    - Only http/https schemes allowed
    - No localhost/private addresses
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
        if result.scheme not in ALLOWED_SCHEMES:
            return False
        host = result.netloc.split(':')[0].lower()
        if host in BLOCKED_HOSTS:
            return False
        return True
    except Exception:
        return False
