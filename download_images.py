from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import asyncio
import random

def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def fetch_page_source(url):
    options = Options()
    options.headless = True  # Работать в фоновом режиме, без открытия окна браузера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  # Увеличено время ожидания до 60 секунд
        page_source = driver.page_source
    finally:
        driver.quit()

    return page_source

async def download_html_page(url, chapter_folder, page_number):
    retries = 5
    for attempt in range(retries):
        try:
            page_source = await asyncio.wait_for(loop.run_in_executor(None, fetch_page_source, url), timeout=90)  # Увеличено время ожидания до 90 секунд
            if "<html" in page_source and "</html>" in page_source:  # Проверка наличия ключевых элементов
                break
        except asyncio.TimeoutError:
            print(f"Превышено время ожидания для страницы {url}, попытка {attempt + 1} из {retries}...")
            if attempt == retries - 1:
                print(f"Не удалось загрузить страницу {url} после {retries} неудачных попыток.")
                return
        await asyncio.sleep(random.uniform(2, 5))  # Добавлена задержка между попытками

    # Сохранение HTML страницы в файл
    html_file_name = os.path.join(chapter_folder, f"{page_number:03d}.html")
    with open(html_file_name, 'w', encoding='utf-8') as file:
        file.write(page_source)
    print(f"HTML страница сохранена: {html_file_name}")

async def download_html_for_chapter(url_template, chapter, folder_name):
    chapter_folder = os.path.join(folder_name, f"chapter_{chapter}")
    create_folder_if_not_exists(chapter_folder)

    page = 1
    while True:
        url = url_template.replace("{chapter}", str(chapter)).replace("{page}", str(page))
        print(f"Загрузка главы {chapter}, страницы {page} с URL: {url}")

        await download_html_page(url, chapter_folder, page)

        # Проверяем, была ли скачана страница
        html_file_name = os.path.join(chapter_folder, f"{page:03d}.html")
        if not os.path.exists(html_file_name):
            print(f"Не удалось скачать страницу для главы {chapter}, страницы {page}, переход к следующей главе.")
            break

        page += 1  # Переход к следующей странице

async def download_html(url_template, start_chapter, end_chapter, folder_name):
    for chapter in range(start_chapter, end_chapter + 1):
        await download_html_for_chapter(url_template, chapter, folder_name)

# Пример использования функции
url_template = 'https://mangalib.me/cheolhyeolgeomga-sanyang-gaeui-hoegw/v1/c{chapter}?page={page}'
start_chapter = 1
end_chapter = 30  # Укажите конечную главу
folder_name = 'html_pages'

# Запуск асинхронного кода
loop = asyncio.get_event_loop()
loop.run_until_complete(download_html(url_template, start_chapter, end_chapter, folder_name))
