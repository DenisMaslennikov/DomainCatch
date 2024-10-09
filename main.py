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
    while True:
        domain = buy_domains_queue.get()  # Извлекаем домен из очереди
        if domain is None:  # Если получен сигнал завершения
            break
        # Логика покупки домена
        logger.debug(f"Покупка домена {domain}...")


def main() -> None:
    domains_for_check = get_domain_list_from_file(config.DOMAINS_FILE)
    domains_for_delete = set()
    lock = threading.Lock()

    # Создаем очередь для доменов для покупки
    buy_domains_queue = multiprocessing.Queue()

    # Запускаем процесс для покупки доменов
    purchase_process = multiprocessing.Process(
        target=purchase_domains, args=(buy_domains_queue,)
    )
    purchase_process.start()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config.THREADS_PER_DOMAIN
    ) as executor:
        # Создаем и отправляем задания на выполнение в пул потоков
        futures = {
            executor.submit(
                check_domain, domain, domains_for_delete, lock, buy_domains_queue
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
