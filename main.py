import concurrent.futures
import multiprocessing
import queue
import random
import threading
from time import sleep

import config
from logger import logger
from service import get_domain_list_from_file, check_domain
from whois import whois_query_with_proxy

buy_domains_queue = queue.Queue()


def purchase_domains(buy_domains_queue):
    """Процесс для покупки доменов"""
    domains_success_count = 0
    while True:
        domain = buy_domains_queue.get()  # Извлекаем домен из очереди
        if domain is None:  # Если получен сигнал завершения
            break
        # Логика покупки домена
        domains_success_count += 1
        logger.debug(f"Покупка домена {domain}...")
        if domains_success_count == config.MAX_DOMAINS_FOR_REGISTRAR:
            logger.debug("Все домены куплены выхожу")
            break


def main() -> None:
    domains_for_check = get_domain_list_from_file(config.DOMAINS_FILE)
    free_domains = set()

    # Создаем очередь для доменов для покупки
    buy_domains_queue = multiprocessing.Queue()

    # Запускаем процесс для покупки доменов
    purchase_process = multiprocessing.Process(
        target=purchase_domains, args=(buy_domains_queue,)
    )
    purchase_process.start()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config.THREADS_PER_DOMAIN * len(domains_for_check)
    ) as executor:
        # Создаем и отправляем задания на выполнение в пул потоков
        futures = {
            executor.submit(
                check_domain, domain, free_domains, buy_domains_queue
            ): domain
            for domain in domains_for_check
            for _ in range(config.THREADS_PER_DOMAIN)
        }

        while futures:
            for future in concurrent.futures.as_completed(futures):
                domain = futures[future]
                try:
                    future.result()  # Проверяем результат потока
                except Exception as e:
                    logger.error(f"Ошибка для домена {domain}: {e}")
                # Удаляем завершенные задания из словаря
                del futures[future]

    # Отправляем сигнал завершения процессу покупки
    buy_domains_queue.put(None)
    purchase_process.join()  # Ждем завершения процесса покупки


if __name__ == "__main__":
    main()
