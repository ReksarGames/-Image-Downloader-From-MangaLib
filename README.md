
# HTML and Image Downloader using Selenium and asyncio

## Overview

This repository contains scripts for downloading HTML pages and images from a given URL template using Selenium, BeautifulSoup, and asyncio. The scripts are designed to efficiently handle downloading content for multiple chapters and pages, making them ideal for applications such as web scraping manga or other serialized web content.

## Requirements

- Python 3.7+
- Selenium
- BeautifulSoup4
- aiohttp
- webdriver_manager

Install the required packages using pip:
```sh
pip install selenium beautifulsoup4 aiohttp webdriver_manager
```

## HTML Downloader

### Script: `download_htmlPage_MangaLib.py`

This script downloads HTML pages from a specified URL template. It is designed to handle multiple chapters and pages, with built-in retries and error handling.

#### Key Functions:
- `create_folder_if_not_exists(folder)`: Creates a folder if it doesn't already exist.
- `fetch_page_source(url)`: Fetches the page source using Selenium in headless mode.
- `download_html_page(url, chapter_folder, page_number)`: Downloads and saves the HTML page source to a file.
- `download_html_for_chapter(url_template, chapter, folder_name)`: Downloads all pages for a specific chapter.
- `download_html(url_template, start_chapter, end_chapter, folder_name)`: Manages downloading HTML pages for a range of chapters.

#### Usage:
```python
url_template = 'https://example.com/chapter_{chapter}/page_{page}'
start_chapter = 1
end_chapter = 30
folder_name = 'html_pages'

# Run the downloader
loop = asyncio.get_event_loop()
loop.run_until_complete(download_html(url_template, start_chapter, end_chapter, folder_name))
```

### Explanation

HTML pages are downloaded instead of individual images because downloading images separately can cause the process to halt due to server issues such as non-responsiveness or 400-series errors. HTML pages provide a more stable and faster download process.

## Image Downloader

### Script: `download_images.py`

This script downloads images from HTML pages specified by a URL template. It uses BeautifulSoup to parse HTML and aiohttp for asynchronous HTTP requests.

#### Key Functions:
- `create_folder_if_not_exists(folder)`: Creates a folder if it doesn't already exist.
- `download_image(session, img_url, img_name)`: Downloads an image and saves it to a file.
- `fetch_page_source(url)`: Fetches the page source using Selenium in headless mode.
- `download_images_from_page(url, chapter_folder)`: Downloads all images from a specified page.
- `download_images_for_chapter(url_template, chapter, folder_name)`: Downloads all images for a specific chapter.
- `download_images(url_template, start_chapter, end_chapter, folder_name)`: Manages downloading images for a range of chapters.

#### Usage:
```python
url_template = 'https://example.com/chapter_{chapter}/page_{page}'
start_chapter = 1
end_chapter = 2
folder_name = 'images'

# Setup for parallel execution
executor = ThreadPoolExecutor(max_workers=5)
loop = asyncio.get_event_loop()

# Run the downloader
loop.run_until_complete(download_images(url_template, start_chapter, end_chapter, folder_name))
```

## Notes

- Adjust the `url_template`, `start_chapter`, `end_chapter`, and `folder_name` variables to match your specific use case.
- Ensure that you have the appropriate permissions to scrape and download content from the target website.
- The scripts include retry mechanisms and delays to handle temporary issues with the target server and avoid being blocked.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
