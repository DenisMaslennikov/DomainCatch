import logging
from collections import namedtuple
from pathlib import Path

Whois = namedtuple("Whois", "url port")
Registrar = namedtuple("Registrar", "url module klass")

# Список whois серверов в формате ("url", "port")
WHOIS_SERVERS = {
    "com": [
        Whois("whois.verisign-grs.com", 43),
        Whois("whois.internic.net", 43),
        Whois("whois.crsnic.net", 43),
        Whois("whois.iana.org", 43),
    ],
    "net": [
        Whois("whois.verisign-grs.com", 43),
        Whois("whois.internic.net", 43),
        Whois("whois.crsnic.net", 43),
        Whois("whois.iana.org", 43),
    ],
}

DOMAIN_REGISTRATOR = []

ROOT_PATH = Path(__file__).parent

DOMAINS_FILE = ROOT_PATH / "resources" / "domains.txt"

THREADS_PER_DOMAIN = 3

LOG_LEVEL = logging.DEBUG
