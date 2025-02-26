import pycurl
import logging
import datetime
from io import BytesIO
from bs4 import BeautifulSoup

API_URL_ALTSEASON = "https://robo.trading/ru/market/altseason/"
API_URL_BTC_DOMINANCE = "https://ru.tradingview.com/markets/cryptocurrencies/dominance/"

def get_page_content(url):
    """Выполняет запрос по curl и возвращает HTML-страницу"""
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.HTTPHEADER, [
        "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language: ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,ar;q=0.6,zh-TW;q=0.5,zh;q=0.4",
        "cache-control: no-cache",
        "pragma: no-cache",
        "priority: u=0, i",
        "referer: https://www.google.com/",
        "sec-ch-ua: \"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile: ?0",
        "sec-ch-ua-platform: \"Windows\"",
        "sec-fetch-dest: document",
        "sec-fetch-mode: navigate",
        "sec-fetch-site: cross-site",
        "sec-fetch-user: ?1",
        "upgrade-insecure-requests: 1",
        "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
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
    
    soup = BeautifulSoup(response_data, "html.parser")
    table_rows = soup.find_all("tr")
    for row in table_rows:
        columns = row.find_all("td")
        if len(columns) == 3:
            date_text = columns[0].text.strip()
            index_text = columns[2].text.strip().replace("%", "")
            
            today_date = datetime.datetime.now().strftime("%d.%m.%Y")
            if date_text == today_date:
                return today_date, int(index_text)
    
    logging.error("Не удалось найти данные за сегодняшний день!")
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
