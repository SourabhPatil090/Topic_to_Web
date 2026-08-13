import os
import socket
import urllib.request
import urllib.error
from urllib.parse import urlparse


def check_dns_and_http(url=None, timeout=5):
    url = url or os.getenv("OPENROUTER_BASE_URL", "https://api.openrouter.ai/v1/chat/completions")
    print(f"Checking URL: {url}")

    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    # DNS resolution
    try:
        print(f"Resolving host: {host}")
        addrs = socket.getaddrinfo(host, port)
        print(f"DNS resolution successful. {len(addrs)} addresses returned.")
    except Exception as e:
        print(f"DNS resolution FAILED for {host}: {e}")
        return 1

    # Simple HTTP HEAD request
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "check-openrouter/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            print(f"HTTP response: {resp.status} {resp.reason}")
            return 0
    except urllib.error.HTTPError as he:
        print(f"HTTP error: {he.code} {he.reason}")
        return 2
    except urllib.error.URLError as ue:
        print(f"URL error during HTTP request: {ue.reason}")
        return 3
    except Exception as e:
        print(f"Unexpected error during HTTP request: {e}")
        return 4


if __name__ == '__main__':
    exit(check_dns_and_http())
