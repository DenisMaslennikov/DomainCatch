from multiprocessing import Queue
from os import PathLike
import random
from threading import Lock
from time import sleep

import config
from logger import logger
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


def check_domain(domain: str, free_domains: set[str], buy_domains_queue: Queue) -> None:
    """Проверка домена через WHOIS."""
    zone = domain.split(".")[-1]
    while True:  # Запускаем бесконечный цикл для повторной проверки
        if zone in config.WHOIS_SERVERS:
            whois_server = random.choice(config.WHOIS_SERVERS[zone])
            whois = whois_query_with_proxy(
                domain,
                whois_server.url,
                whois_server.port,
            )
            if f'No match for "{domain.upper()}"' in whois:
                if domain not in free_domains:
                    # Добавляем домен в очередь для покупки
                    buy_domains_queue.put(domain)
                    free_domains.add(domain)
                    logger.debug(f"Домен {domain} добавлен в очередь для покупки.")
                break
            if not "pendingDelete" in whois:
                logger.debug(f"Домен {domain} не помечен к удалению")
                break

        # TODO Убрать когда будут прокси
        sleep(config.WHOIS_TREAD_SLEEP_SECONDS)
