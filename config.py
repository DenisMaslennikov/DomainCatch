import logging
from collections import namedtuple
from pathlib import Path

Whois = namedtuple("Whois", "url port")
Registrar = namedtuple("Registrar", "url module klass")

# Максимальное количество доменов которое можно зарегистрировать за сессию.
MAX_DOMAINS_FOR_REGISTRAR = 1

# Для отладки без прокси. Время на которое засыпает поток между запросами к whois
WHOIS_TREAD_SLEEP_SECONDS = 1

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

THREADS_PER_DOMAIN = 1

LOG_LEVEL = logging.DEBUG
