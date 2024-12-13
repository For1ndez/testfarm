import json
import requests
import time
import random
from colorama import Fore, Style, init

init(autoreset=True)

CONFIG_PATH = "config.json"
COLLECT_URL = "https://api.tonverse.app/galaxy/collect"
INFO_URL = "https://api.tonverse.app/user/info"
CREATE_URL = "https://api.tonverse.app/stars/create"
GET_GALAXY_URL = "https://api.tonverse.app/galaxy/get"

class Logger:
    def __init__(self, title):
        self.title = f"{Fore.CYAN}{title}{Style.RESET_ALL}"

    def log(self, message):
        print(f"{self.title} {message}")

logger = Logger(">>>    AutoClicker Private  <<<   ")

def load_config(path):
    """Загрузка конфигурации из файла."""
    with open(path, "r") as file:
        return json.load(file)

def generate_device_specific_headers(user_agent):
    """Генерация правдоподобных заголовков для одного устройства."""
    return {
        "Host": "api.tonverse.app",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "\"Windows\"" if "Windows" in user_agent else "\"macOS\"",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": user_agent,
        "sec-ch-ua": random.choice([
            "\"Chromium\";v=\"131\", \"Microsoft Edge\";v=\"131\", \"Not_A_Brand\";v=\"99\"",
            "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not_A_Brand\";v=\"99\""
        ]),
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://app.tonverse.app",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.tonverse.app/",
        "Accept-Language": random.choice(["en-US,en;q=0.9", "ru-RU,ru;q=0.9,en-US;q=0.8"]),
        "Accept-Encoding": "gzip, deflate",
        "X-Application-Version": "0.7.18" 
    }

def get_galaxy_id(session, user_agent):
    """Получить galaxy_id из ответа API."""
    headers = generate_device_specific_headers(user_agent)
    data = {"session": session}  # Тело запроса
    try:
        response = requests.post(GET_GALAXY_URL, headers=headers, data=data)
        response_json = response.json()

        if "response" in response_json and "id" in response_json["response"]:
            galaxy_id = response_json["response"]["id"]
            print(f"Получен galaxy_id: {galaxy_id}")
            return galaxy_id

        # Если ошибка в ответе
        if "error" in response_json:
            error_code = response_json["error"].get("code", "Неизвестный код")
            error_text = response_json["error"].get("text", "Неизвестная ошибка")
            print(f"Ошибка API: Код {error_code}, Сообщение: {error_text}")
        else:
            print("Неожиданный ответ API:", response_json)

    except Exception as e:
        print(f"Ошибка при выполнении запроса get_galaxy_id: {e}")

    return None

def get_user_info(session, user_agent):
    """Получить информацию о пользователе, включая dust и dust_produce."""
    headers = generate_device_specific_headers(user_agent)
    data = {"session": session, "id": "undefined"}
    try:
        response = requests.post(INFO_URL, headers=headers, data=data)
        return response.json()
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return {}

def collect_dust(session, user_agent):
    """Сбор звёздной пыли."""
    headers = generate_device_specific_headers(user_agent)
    data = {"session": session}
    try:
        response = requests.post(COLLECT_URL, headers=headers, data=data)
        response_json = response.json()
        if response_json.get("response", {}).get("success") == 1:
            dust = response_json["response"].get("dust", 0)
            print(f"Собрано {dust} единиц звёздной пыли!")
        else:
            print("Не удалось собрать звёздную пыль:", response_json)
    except Exception as e:
        print(f"Ошибка: {e}")

def create_stars(session, user_agent, galaxy_id):
    """Создать 100 звёзд и отправить запрос на galaxy/get."""
    headers = generate_device_specific_headers(user_agent)
    data = {
        "session": session,
        "galaxy_id": galaxy_id,
        "stars": "100"
    }
    try:
        response = requests.post(CREATE_URL, headers=headers, data=data)
        print("Ответ на создание звёзд:", response.json())
        if response.status_code == 200 and response.json().get("response", {}).get("success") == 1:
            print("Создание звёзд успешно. Выполняем запрос на galaxy/get...")
            get_galaxy_id(session, user_agent)  # Выполнение запроса на /galaxy/get
    except Exception as e:
        print(f"Ошибка при создании звёзд: {e}")

def imitate_background_activity(session, user_agent):
    """Имитация фоновой активности через POST-запросы."""
    urls = [
        "https://api.tonverse.app/user/awards",
        "https://api.tonverse.app/galaxy/random",
        "https://api.tonverse.app/user/rating"
    ]
    url = random.choice(urls)
    headers = generate_device_specific_headers(user_agent)
    data = {"session": session}
    try:
        response = requests.post(url, headers=headers, data=data)
        print(f"Фоновый запрос к {url}. Статус: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при фоновой активности: {e}")

def main():

    logger.log("by Crypto_GR... Buy $STRR on MemePad")
    logger.log("Скрипт запускается...")

    config = load_config(CONFIG_PATH)
    accounts = config.get("accounts", [])
    if not accounts:
        print("Нет аккаунтов для обработки.")
        return

    while True:
        for account in accounts:
            session = account.get("session")
            user_agent = account.get("user_agent")

            if not session or not user_agent:
                print("Пропущен аккаунт из-за отсутствия данных (session или user_agent).")
                continue

            print(f"Обработка аккаунта с User-Agent: {user_agent}")

            # Получить galaxy_id перед каждым циклом
            galaxy_id = get_galaxy_id(session, user_agent)
            if not galaxy_id:
                print("Galaxy ID не получен, пропуск аккаунта.")
                continue

            user_info = get_user_info(session, user_agent)
            available_dust = user_info.get("response", {}).get("dust", 0)
            dust_produce = user_info.get("response", {}).get("dust_produce", 0)
            required_dust = dust_produce * 1.5

            print(f"Доступная пыль: {available_dust}, Производимая в час: {dust_produce}, Требуется: {required_dust:.2f}")

            if available_dust >= required_dust:
                print("Достаточно пыли. Создаём звёзды...")
                create_stars(session, user_agent, galaxy_id)
            else:
                print("Недостаточно пыли. Собираем...")
                collect_dust(session, user_agent)

            if random.random() > 0.3:  # 30% вероятности
                imitate_background_activity(session, user_agent)

            # Случайная задержка между запросами
            delay = random.randint(30, 120)  # 30-120 секунд
            print(f"Ожидание {delay} секунд перед следующим запросом...")
            time.sleep(delay)

        # Задержка перед следующим циклом обработки
        delay_minutes = random.randint(8, 40)
        delay_seconds = delay_minutes * 60
        print(f"Ожидание {delay_minutes} минут перед следующим циклом...")
        time.sleep(delay_seconds)

if __name__ == "__main__":
    main()
