import concurrent.futures
import multiprocessing
import queue

import config
from logger import logger
from proxy import process_proxy_lists, alive_proxys
from service import get_domain_list_from_file, check_domain

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
        logger.info(f"Покупка домена {domain}...")
        if domains_success_count == config.MAX_DOMAINS_FOR_REGISTRAR:
            logger.debug("Все домены куплены выхожу")
            break


def main() -> None:
    domains_for_check = get_domain_list_from_file(config.DOMAINS_FILE)
    free_domains = set()
    process_proxy_lists()
    logger.info(f"Собрано {len(alive_proxys)} прокси")

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
                check_domain,
                domain,
                free_domains,
                buy_domains_queue,
                list(alive_proxys),
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
