#!/usr/bin/env python3
"""Fetch proxy data and generate multi-platform domain rule files."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API_URL = "https://emos.best/api/wiki/proxy"
USER_AGENT = "emos-proxy-rule-generator/1.0 (+https://github.com/<user>/emos-proxy-rule)"
REQUEST_TIMEOUT = 30
RULE_AUTHOR = "binary"
UPDATE_TZ = ZoneInfo("Asia/Shanghai")

ROOT_DIR = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT_DIR / "rules"

LOON_FILE = RULES_DIR / "emos-loon.list"
SURGE_FILE = RULES_DIR / "emos-surge.list"
SHADOWROCKET_FILE = RULES_DIR / "emos-shadowrocket.list"
QUANTUMULT_X_FILE = RULES_DIR / "emos-quantumultx.list"
MIHOMO_LIST_FILE = RULES_DIR / "emos-mihomo.list"
MIHOMO_YAML_FILE = RULES_DIR / "emos-mihomo.yaml"
SING_BOX_FILE = RULES_DIR / "emos-sing-box.json"

HOST_LABEL_RE = re.compile(r"^(?:xn--)?[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def fetch_data() -> list[dict]:
    """Fetch raw JSON array from the remote API."""
    request = Request(
        API_URL,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
    except URLError as exc:
        raise RuntimeError(f"Network error while requesting API: {exc}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Request timeout after {REQUEST_TIMEOUT} seconds: {exc}") from exc

    if status != 200:
        raise RuntimeError(f"API request failed with HTTP status {status}")

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to parse JSON response: {exc}") from exc

    if not isinstance(data, list):
        raise RuntimeError("Unexpected response type: expected a JSON array")

    return data


def extract_domains(items: Iterable[dict]) -> list[str]:
    """Extract, normalize, deduplicate and sort hostnames."""
    domains: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            continue

        raw_url = item.get("url")
        if not isinstance(raw_url, str):
            continue

        hostname = parse_hostname(raw_url)
        if hostname:
            domains.add(hostname)

    return sorted(domains)


def parse_hostname(raw_url: str) -> str | None:
    """Parse URL and return a validated hostname."""
    value = raw_url.strip()
    if not value:
        return None

    parsed = urlparse(value)
    if not parsed.scheme:
        parsed = urlparse(f"http://{value}")

    hostname = parsed.hostname
    if not hostname:
        return None

    hostname = hostname.rstrip(".").lower()
    if not hostname or "." not in hostname:
        return None

    try:
        hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    if not is_valid_hostname(hostname):
        return None

    return hostname


def is_valid_hostname(hostname: str) -> bool:
    """Return whether hostname is syntactically valid and domain-like."""
    if len(hostname) > 253:
        return False

    labels = hostname.split(".")
    if len(labels) < 2:
        return False

    has_alpha = any(any(ch.isalpha() for ch in label) for label in labels)
    if not has_alpha:
        return False

    return all(HOST_LABEL_RE.fullmatch(label) for label in labels)


def generate_loon_rules(domains: list[str], updated_at: str) -> str:
    lines = [
        "# Name: emos-loon",
        f"# Author: {RULE_AUTHOR}",
        f"# Updated: {updated_at}",
        "# Format: Loon domain list",
        "",
    ]
    lines.extend(f"DOMAIN,{domain}" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_surge_rules(domains: list[str], updated_at: str) -> str:
    lines = [
        "# Name: emos-surge",
        f"# Author: {RULE_AUTHOR}",
        f"# Updated: {updated_at}",
        "# Format: Surge rule list",
        "",
    ]
    lines.extend(f"DOMAIN,{domain},DIRECT" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_shadowrocket_rules(domains: list[str], updated_at: str) -> str:
    lines = [
        "# Name: emos-shadowrocket",
        f"# Author: {RULE_AUTHOR}",
        f"# Updated: {updated_at}",
        "# Format: Shadowrocket rule list",
        "",
    ]
    lines.extend(f"DOMAIN,{domain},DIRECT" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_quantumult_x_rules(domains: list[str], updated_at: str) -> str:
    lines = [
        "# Name: emos-quantumultx",
        f"# Author: {RULE_AUTHOR}",
        f"# Updated: {updated_at}",
        "# Format: Quantumult X rule list",
        "",
    ]
    lines.extend(f"HOST,{domain},DIRECT" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_mihomo_rules(domains: list[str], updated_at: str) -> str:
    lines = [
        "# Name: emos-mihomo-direct",
        f"# Author: {RULE_AUTHOR}",
        f"# Updated: {updated_at}",
        "# Format: Mihomo rules list",
        "",
    ]
    lines.extend(f"DOMAIN,{domain},DIRECT" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_mihomo_provider(domains: list[str], updated_at: str) -> str:
    lines = [
        f"# Updated: {updated_at}",
        "payload:",
    ]
    lines.extend(f"  - DOMAIN,{domain}" for domain in domains)
    return "\n".join(lines) + "\n"


def generate_sing_box_ruleset(domains: list[str]) -> str:
    ruleset = {
        "version": 1,
        "rules": [
            {
                "domain": domains,
            }
        ],
    }
    return json.dumps(ruleset, ensure_ascii=False, indent=2) + "\n"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(content)


def main() -> int:
    try:
        data = fetch_data()
    except RuntimeError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    domains = extract_domains(data)
    updated_at = datetime.now(UPDATE_TZ).strftime("%Y-%m-%d %H:%M:%S")
    if not data:
        print("[WARN] API returned an empty array; generating files with headers only.")
    elif not domains:
        print("[WARN] No valid domains extracted from response; generating empty rule bodies.")

    outputs = {
        LOON_FILE: generate_loon_rules(domains, updated_at),
        SURGE_FILE: generate_surge_rules(domains, updated_at),
        SHADOWROCKET_FILE: generate_shadowrocket_rules(domains, updated_at),
        QUANTUMULT_X_FILE: generate_quantumult_x_rules(domains, updated_at),
        MIHOMO_LIST_FILE: generate_mihomo_rules(domains, updated_at),
        MIHOMO_YAML_FILE: generate_mihomo_provider(domains, updated_at),
        SING_BOX_FILE: generate_sing_box_ruleset(domains),
    }

    for file_path, file_content in outputs.items():
        write_file(file_path, file_content)

    print(f"[OK] Extracted {len(domains)} unique domains.")
    print("[OK] Generated files:")
    for file_path in outputs:
        print(f" - {file_path.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
