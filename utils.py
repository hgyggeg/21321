import pycurl
import logging
import datetime
import json
from io import BytesIO
from bs4 import BeautifulSoup

# Новая API-ручка
API_URL_ALTSEASON = "https://www.blockchaincenter.net/en/altcoin-season-index/"
API_URL_BTC_DOMINANCE = "https://ru.tradingview.com/markets/cryptocurrencies/dominance/"
API_URL_BTC_PRICE = "https://crypto.com/price/ru/bitcoin"

def get_page_content(url):
    """Выполняет запрос по curl и возвращает HTML-страницу"""
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.HTTPHEADER, [
        "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6,zh-TW;q=0.5,zh;q=0.4",
        "Cache-Control: no-cache",
        "Connection: keep-alive",
        "Pragma: no-cache",
        "Referer: https://www.google.com/",
        "Sec-Fetch-Dest: document",
        "Sec-Fetch-Mode: navigate",
        "Sec-Fetch-Site: cross-site",
        "Sec-Fetch-User: ?1",
        "Upgrade-Insecure-Requests: 1",
        "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        'sec-ch-ua: "Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile: ?0",
        'sec-ch-ua-platform: "Windows"'
    ])
    curl.setopt(pycurl.FOLLOWLOCATION, True)
    curl.setopt(pycurl.TIMEOUT, 10)

    try:
        curl.perform()
        curl.close()
        return buffer.getvalue().decode("utf-8-sig").strip()
    except Exception as e:
        logging.error(f"Ошибка при запросе {url}: {e}")
        return None

def get_altseason_index():
    """Парсит HTML-страницу для получения индекса альтсезона"""
    response_data = get_page_content(API_URL_ALTSEASON)
    if not response_data:
        return None, None
    
    # Ищем JSON с данными altcoin season index
    try:
        start_index = response_data.find("chartdata2[90] = ")
        if start_index == -1:
            logging.error("Не удалось найти данные altseason index на странице!")
            return None, None
        
        start_index += len("chartdata2[90] = ")
        end_index = response_data.find(";", start_index)
        json_data = response_data[start_index:end_index].strip()

        # Преобразуем строку JSON в словарь
        altseason_data = json.loads(json_data)

        today_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Ожидаемый формат даты
        index_value = None

        # Ищем данные за сегодняшний день
        for entry in altseason_data:
            if entry["time"] == today_date:
                index_value = int(entry["value"])
                break

        if index_value is None:
            logging.error("Не удалось найти данные за сегодняшний день!")
            return None, None

        return today_date, index_value
    except Exception as e:
        logging.error(f"Ошибка при парсинге данных altseason index: {e}")
        return None, None
    
def get_btc_dominance():
    """Парсит HTML-страницу для получения доминации BTC"""
    response_data = get_page_content(API_URL_BTC_DOMINANCE)
    if not response_data:
        return None
    
    soup = BeautifulSoup(response_data, "html.parser")
    dom_element = soup.find("div", class_="apply-overflow-tooltip value-GgmpMpKr")
    if dom_element:
        return dom_element.text.strip()
    else:
        logging.error("Не удалось найти доминацию BTC на странице!")
        return None
    
def get_btc_price():
    """Парсит HTML-страницу для получения курса BTC"""
    response_data = get_page_content(API_URL_BTC_PRICE)
    if not response_data:
        return None

    try:
        soup = BeautifulSoup(response_data, "html.parser")
        script_tag = soup.find("script", string=lambda text: text and "usd_price" in text)

        if not script_tag:
            logging.error("Не найден скрипт с ценой BTC!")
            return None

        script_content = script_tag.string
        start_index = script_content.find('"usd_price":') + len('"usd_price":')
        end_index = script_content.find(",", start_index)

        btc_price = script_content[start_index:end_index].strip()
        btc_price = int(float(btc_price))  # Приводим к целому числу

        return btc_price
    except Exception as e:
        logging.error(f"Ошибка при парсинге цены BTC: {e}")
        return None