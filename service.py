from os import PathLike
import random
from threading import Lock

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


def check_domain(domain, domains_for_delete, lock, buy_domains_queue):
    """Проверка домена через WHOIS с синхронизацией потоков"""
    while True:  # Запускаем бесконечный цикл для повторной проверки
        zone = domain.split(".")[-1]
        if zone in config.WHOIS_SERVERS:
            whois_server = random.choice(config.WHOIS_SERVERS[zone])
            whois = whois_query_with_proxy(
                domain,
                whois_server.url,
                whois_server.port,
            )
            if f'No match for "{domain.upper()}"' in whois:
                with lock:
                    if domain not in domains_for_delete:
                        # Добавляем домен в очередь для покупки
                        buy_domains_queue.put(domain)
                        domains_for_delete.add(domain)
                        logger.debug(f"Домен {domain} добавлен в очередь для покупки.")
                        break  # Выход из цикла, так как домен помечен для удаления
        sleep(1)  # Небольшая пауза перед повторной проверкой
