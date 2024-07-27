from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor


def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


async def download_image(session, img_url, img_name):
    try:
        async with session.get(img_url) as img_response:
            if img_response.status == 200:
                with open(img_name, 'wb') as img_file:
                    img_file.write(await img_response.read())
                print(f"Изображение сохранено: {img_name}")
            else:
                print(f"Не удалось загрузить изображение: {img_url}, статус: {img_response.status}")
    except Exception as e:
        print(f"Ошибка при загрузке изображения {img_url}: {e}")


def fetch_page_source(url):
    options = Options()
    options.headless = True  # Работать в фоновом режиме, без открытия окна браузера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'img')))
        page_source = driver.page_source
    finally:
        driver.quit()

    return page_source


async def download_images_from_page(url, chapter_folder):
    retries = 3
    for attempt in range(retries):
        try:
            page_source = await loop.run_in_executor(executor, fetch_page_source, url)
            break
        except Exception as e:
            print(f"Ошибка при получении страницы {url}: {e}. Попытка {attempt + 1} из {retries}")
            if attempt == retries - 1:
                return

    # Использование BeautifulSoup для извлечения URL изображений
    soup = BeautifulSoup(page_source, 'html.parser')
    img_tags = soup.find_all('img')
    img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]

    print(f"Найдено {len(img_urls)} изображений на странице {url}")

    if not img_urls:
        print(f"Нет изображений на странице {url}")
        return

    # Скачивание изображений параллельно
    async with aiohttp.ClientSession() as session:
        tasks = []
        for img_url in img_urls:
            # Иногда URL могут быть относительными, нужно преобразовать их в абсолютные
            if not img_url.startswith('http'):
                img_url = url + img_url
            img_name = os.path.join(chapter_folder, os.path.basename(img_url))
            tasks.append(download_image_with_status_check(session, img_url, img_name))
        await asyncio.gather(*tasks)


async def download_image_with_status_check(session, img_url, img_name):
    retries = 3
    for attempt in range(retries):
        try:
            async with session.head(img_url) as response:
                if response.status in (403, 404):
                    print(f"Доступ запрещен или изображение не найдено: {img_url}, статус: {response.status}")
                    return
            await download_image(session, img_url, img_name)
            return
        except Exception as e:
            print(f"Ошибка при проверке статуса изображения {img_url}: {e}")
        await asyncio.sleep(2)  # Время ожидания между попытками


async def download_images_for_chapter(url_template, chapter, folder_name):
    chapter_folder = os.path.join(folder_name, f"chapter_{chapter}")
    create_folder_if_not_exists(chapter_folder)

    page = 1
    while True:
        url = url_template.replace("{chapter}", str(chapter)).replace("{page}", str(page))
        print(f"Загрузка главы {chapter}, страницы {page} с URL: {url}")

        await download_images_from_page(url, chapter_folder)

        # Проверяем, есть ли изображения на странице
        if not os.listdir(chapter_folder):
            break

        page += 1  # Переход к следующей странице


async def download_images(url_template, start_chapter, end_chapter, folder_name):
    tasks = []
    for chapter in range(start_chapter, end_chapter + 1):
        tasks.append(download_images_for_chapter(url_template, chapter, folder_name))
    await asyncio.gather(*tasks)


# Пример использования функции
url_template = 'https://mangalib.me/caico-ribenji/v1/c{chapter}?page={page}'
start_chapter = 1
end_chapter = 2  # Укажите конечную главу
folder_name = 'images'

# Настройка для параллельного выполнения
executor = ThreadPoolExecutor(max_workers=5)  # Ограничьте количество потоков до 5 для стабильности
loop = asyncio.get_event_loop()

# Запуск асинхронного кода
loop.run_until_complete(download_images(url_template, start_chapter, end_chapter, folder_name))
