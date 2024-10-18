from multiprocessing import Queue
from os import PathLike
import random
from time import sleep

import config
from logger import logger
from proxy import Proxy
from whois import whois_query_with_proxy


def get_domain_list_from_file(path: PathLike) -> list[str]:
    """
    Получение списка доменов из файла.
    :param path: Путь к файлу с доменами.
    :return: Список доменов.
    """
    with open(path, "r") as f:
        domains = f.readlines()
    domains = [domain.strip() for domain in domains]
    return domains


def check_domain(
    domain: str,
    free_domains: set[str],
    buy_domains_queue: Queue,
    proxy_list: list[Proxy] = None,
) -> None:
    """Проверка домена через WHOIS."""
    zone = domain.split(".")[-1]
    proxy = None
    while True:  # Запускаем бесконечный цикл для повторной проверки
        if proxy_list is not None:
            proxy: Proxy | None = random.choice(proxy_list)

        if zone in config.WHOIS_SERVERS:
            whois_server = random.choice(config.WHOIS_SERVERS[zone])
            try:
                whois = whois_query_with_proxy(
                    domain,
                    whois_server.url,
                    whois_server.port,
                    proxy_host=proxy.ip if proxy else None,
                    proxy_port=int(proxy.port) if proxy else None,
                    proxy_type=proxy.type if proxy else None,
                )
                if f'No match for "{domain.upper()}"' in whois:
                    if domain not in free_domains:
                        # Добавляем домен в очередь для покупки
                        buy_domains_queue.put(domain)
                        free_domains.add(domain)
                        logger.info(f"Домен {domain} добавлен в очередь для покупки.")
                    break
                if not "pendingDelete" in whois:
                    logger.info(f"Домен {domain} не помечен к удалению")
                    break
            except Exception as e:
                proxy_list.remove(proxy)
                logger.debug(
                    f"Ошибка подключения к серверу {whois_server} использованный прокси {proxy}. Домен {domain}. Текст "
                    f"ошибки: {e}"
                )

        # sleep(config.WHOIS_TREAD_SLEEP_SECONDS)
