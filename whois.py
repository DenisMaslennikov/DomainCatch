import socket
from typing import Any

import socks  # Для работы с SOCKS-прокси


def whois_query_with_proxy(
    domain: str,
    server: str,
    port: int = 43,
    proxy_host: Any = None,
    proxy_port: Any = None,
    proxy_type: str = None,
    proxy_username: str = None,
    proxy_password: str = None,
):
    """Проверка вхуиса через прокси."""
    # Настройка прокси
    if proxy_host and proxy_port:
        if proxy_type.lower() == "socks5":
            socks.set_default_proxy(
                socks.SOCKS5,
                proxy_host,
                proxy_port,
                username=proxy_username,
                password=proxy_password,
            )
        elif proxy_type.lower() == "socks4":
            socks.set_default_proxy(
                socks.SOCKS4,
                proxy_host,
                proxy_port,
                username=proxy_username,
                password=proxy_password,
            )
        elif proxy_type.lower() == "http":
            socks.set_default_proxy(
                socks.HTTP,
                proxy_host,
                proxy_port,
                username=proxy_username,
                password=proxy_password,
            )

        socket.socket = socks.socksocket
        # Переопределяем сокеты для работы через прокси

    # Создаем сокет и подключаемся к WHOIS-серверу
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server, port))

        # Отправляем запрос в формате: domain\r\n
        query = f"{domain}\r\n"
        s.send(query.encode("utf-8"))

        # Получаем ответ от сервера
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data

    # Декодируем ответ в строку и возвращаем
    return response.decode("utf-8")
