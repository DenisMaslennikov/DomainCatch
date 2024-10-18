from abc import ABC, abstractmethod
from collections import namedtuple
from math import ceil
from multiprocessing import Queue
from typing import Any
import concurrent.futures

import requests
from bs4 import BeautifulSoup

import config
from logger import logger

ProxyCheckingQueue = Queue()
alive_proxys = set()

Proxy = namedtuple("Proxy", "ip port type")


class ProxyParser(ABC):

    def __init__(self, url: str, type: str):
        self.url = url
        self.type = type

    @abstractmethod
    def process_proxys(self):
        """Метод интерфейса для обработки прокси из источника"""
        pass


class GeonodeParser(ProxyParser):
    """Парсер прокси с geonode."""

    def _proces_page(self, page: dict[str, Any]):
        """Обрабатываем страницу результатов."""
        data = page["data"]
        for proxy in data:
            if proxy["anonymityLevel"] == "transparent":
                continue
            ProxyCheckingQueue.put(
                Proxy(proxy["ip"], proxy["port"], proxy["protocols"][0])
            )

    def _get_all_pages(self):
        """Получение всех страниц"""
        response = requests.get(self.url.format(1)).json()

        pages = ceil(response["total"] / response["limit"])
        self._proces_page(response)
        for page in range(1, pages + 1):
            response = requests.get(self.url.format(page)).json()
            self._proces_page(response)

    def process_proxys(self):
        """Метод интерфейса для сбора проксей."""
        self._get_all_pages()


class PlainTextParser(ProxyParser):
    """Парсер прокси в текстовом формате."""

    def process_proxys(self):
        """Метод интерфейса для сбора прокси"""
        response = requests.get(self.url).text
        proxys = response.split()
        for proxy in proxys:
            ip, port = proxy.split(":")
            ProxyCheckingQueue.put(Proxy(ip, port, self.type))


def check_proxy(proxy: Proxy):
    """Проверяет прокси"""
    request_proxy = {
        "http": f"{proxy.type}://{proxy.ip}:{proxy.port}",
        "https": f"{proxy.type}://{proxy.ip}:{proxy.port}",
    }
    i_try = 0
    while i_try < config.TRY_PER_PROXY:
        try:
            _check_ip = requests.get(
                config.PROXY_CHECK_URL, proxies=request_proxy, timeout=5
            )
            soup = BeautifulSoup(_check_ip.text, "lxml")
            ip = soup.find("span", attrs={"id": "ip"}).text
            if ip == proxy.ip:
                alive_proxys.add(proxy)
                logger.debug(f"Найден живой прокси {proxy}")
        except Exception:
            pass
            i_try += 1
        # logger.debug(f"Прокси мертв {proxy}")


def process_proxy_lists():
    """Обрабатывает все прокси листы из конфига."""
    for proxy_list in config.PROXY_LISTS:
        proxy_processor = globals().get(proxy_list.parser_class)(
            proxy_list.url, proxy_list.type
        )
        proxy_processor.process_proxys()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=config.PROXY_CHECKING_THREADS
    ) as executor:
        while not ProxyCheckingQueue.empty():
            proxy = ProxyCheckingQueue.get()  # Получаем прокси из очереди
            executor.submit(check_proxy, proxy)
