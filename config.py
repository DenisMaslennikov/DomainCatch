import logging
from collections import namedtuple
from pathlib import Path

Whois = namedtuple("Whois", "url port")
ProxyList = namedtuple("ProxyList", "url parser_class type")
Registrar = namedtuple("Registrar", "url module klass")

# Максимальное количество доменов которое можно зарегистрировать за сессию.
MAX_DOMAINS_FOR_REGISTRAR = 9999

PROXY_CHECKING_THREADS = 500

TRY_PER_PROXY = 5

PROXY_LISTS = [
    ProxyList(
        "https://proxylist.geonode.com/api/proxy-list?limit=500&page={}&sort_by=lastChecked&sort_type=desc",
        "GeonodeParser",
        "mix",
    ),
    ProxyList(
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "PlainTextParser",
        "socks5",
    ),
    ProxyList(
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "PlainTextParser",
        "socks4",
    ),
    ProxyList(
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "PlainTextParser",
        "http",
    ),
]

PROXY_CHECK_URL = "https://www.myip.com/"

# Для отладки без прокси. Время на которое засыпает поток между запросами к whois
# WHOIS_TREAD_SLEEP_SECONDS = 1

# Список whois серверов в формате ("url", "port")
WHOIS_SERVERS = {
    "com": [
        Whois("whois.verisign-grs.com", 43),
        Whois("whois.internic.net", 43),
        Whois("whois.crsnic.net", 43),
        # Whois("whois.iana.org", 43),
    ],
    "net": [
        Whois("whois.verisign-grs.com", 43),
        Whois("whois.internic.net", 43),
        Whois("whois.crsnic.net", 43),
        # Whois("whois.iana.org", 43),
    ],
}

DOMAIN_REGISTRATOR = []

ROOT_PATH = Path(__file__).parent

DOMAINS_FILE = ROOT_PATH / "resources" / "domains.txt"

THREADS_PER_DOMAIN = 1

LOG_LEVEL = logging.INFO
