import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from Helpers.SqlLiteHelper import SQLiteHelper
from Models.PartCategoryModel import PartCategoryModel
from Models.PartItemModel import PartItemModel
from Models.PartScraperModel import PartScraperModel


class PartScraper:
    def __init__(self, parts_model: list[PartScraperModel]):
        self.parts_model = parts_model
        self.parts_for_saving = []
        self.sql_lite_helper = SQLiteHelper('Scraped Parts.db')
        self.image_directory = 'Images'
        if not os.path.exists(self.image_directory):
            os.makedirs(self.image_directory)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-images")  # Disable images
        chrome_options.add_argument("--incognito")  # Run in incognito mode
        chrome_options.add_argument("--user-agent=Mozilla/5.0")  # Set a simple user agent string
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    def scrape_parts_models(self):
        index = 0
        for part in self.parts_model:
            print(f'Current Index {index} out of {len(self.parts_model)}')
            self.scrape_url(part_model=part)
            index += 1
        self.driver.quit()

    def scrape_url(self, part_model: PartScraperModel) -> None:
        print(f'Getting category from url : {part_model.url}')
        self.driver.get(part_model.url)
        part_category_models = self.get_part_categories(base_url=part_model.url)
        for category in part_category_models:
            self.get_category_part_items(part_category_model=category, code=part_model.model_code)
        if not part_category_models:
            self.insert_records([], part_model.model_code, '', '')

    def get_part_categories(self, base_url: str) -> list[PartCategoryModel]:
        error_count = 0
        retries = 0
        while True:
            try:
                parts_container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.row.model-line-categories#opened, div.row.model-lines#opened'))
                )
                if not parts_container:
                    raise TimeoutError()
                break
            except TimeoutError:
                error_count += 1
                print(f'Error at categories url : {base_url}')
                time.sleep(random.randint(2, 5))
                if error_count > 5:
                    retries += 1
                    if retries >= 2:
                        return []
                    self.driver.refresh()
        html_content = parts_container.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        parts_list = soup.select('div.model-line-category a')
        parts_data = [PartCategoryModel(url=part['href'], base_url=base_url, name=part.get_text(strip=True)) for part in
                      parts_list]
        return parts_data

    def get_category_part_items(self, part_category_model: PartCategoryModel, code: str) -> None:
        print(f'Getting items for url : {part_category_model.url}')
        self.driver.get(part_category_model.url)
        error_count = 0
        retries = 0
        while True:
            try:
                present = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div#model-line-category'))
                )
                if not present:
                    raise TimeoutError()
                break
            except TimeoutError:
                error_count += 1
                print(f'Error at parts url : {part_category_model.url}')
                time.sleep(random.randint(2, 5))
                if error_count > 5:
                    retries += 1
                    if retries >= 2:
                        return
                    self.driver.refresh()
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        table_parts = soup.select('table#tblParts tr.part')
        table_parts_items = [self.get_part_item(table_part=part) for part in table_parts]
        print(f'Downloading img from url : {part_category_model.url}')
        img_name = self.download_part_img(soup=soup, model_code=code, category_name=part_category_model.name)
        self.insert_records(table_parts_items=table_parts_items, sgl_code=code, section_name=part_category_model.name,
                            img_name=img_name)

    @staticmethod
    def get_part_item(table_part: Tag) -> PartItemModel:
        part_id = table_part.select_one('td.hotspotid, td.part-hotspotid')
        name = table_part.select_one('span.part-name').text
        code = table_part.select_one('td.part-code').text
        return PartItemModel(part_id=part_id.text if part_id else None, part_name=name, part_code=code)

    def download_part_img(self, soup: BeautifulSoup, model_code: str, category_name: str) -> str:
        img_url = soup.select_one('img#imgMain').get('src')
        print(f'Downloading img : {img_url}')
        while True:
            try:
                response = requests.get(img_url)
                break
            except Exception as ex:
                print(f'Exception at getting image : {str(ex)}')
                time.sleep(random.randint(2, 5))
        file_name = f'{self.sanitize_filename(f'{model_code}-{category_name}')}.jpg'
        if response.status_code == 200:
            with open(f'{self.image_directory}/{file_name}', 'wb') as file:
                file.write(response.content)
            return file_name
        else:
            print(f"Failed to download image from {img_url}")
            return ''

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Convert invalid filenames to valid filenames by replacing or removing invalid characters.
        """
        invalid_chars = r'[<>:"/\\|?*\']'
        sanitized_filename = re.sub(invalid_chars, '_', filename)
        sanitized_filename = sanitized_filename.strip()
        sanitized_filename = sanitized_filename[:255]
        return sanitized_filename

    def insert_records(self, table_parts_items: list[PartItemModel], sgl_code: str, section_name: str, img_name: str):
        print(f'Inserting {len(table_parts_items)} records into db')
        records = []
        for item in table_parts_items:
            record = {
                'sgl_unique_model_code': sgl_code.strip(),
                'section': section_name.strip(),
                'part_number': item.part_code.strip(),
                'description': item.part_name.strip(),
                'item_number': item.part_id.strip(),
                'section_diagram': img_name.strip()
            }
            records.append(record)
        if not table_parts_items:
            record = {
                'sgl_unique_model_code': sgl_code.strip(),
                'section': section_name.strip(),
                'part_number': '',
                'description': '',
                'item_number': '',
                'section_diagram': ''
            }
            records.append(record)
        self.sql_lite_helper.insert_many_records(records=records)
