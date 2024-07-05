import asyncio
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from Helpers.SqlLiteHelper import SQLiteHelper
from Models.PartScraperModel import PartScraperModel
from Scrapers.PartScraper import PartScraper

sql_lite_helper = SQLiteHelper('Scraped Parts.db')
unique_codes = sql_lite_helper.get_sgl_codes()

# Load JSON data
with open(r"D:\Workspace\Projects\SparePartsScrapper\DataParts\New Parts\part_2_remaining.json", 'r',) as json_file:
    data = json.loads(json_file.read())
model_data = [PartScraperModel(model_code=d["SGL Unique Model Code"], url=d["Catalogue Link"]) for d in data if
              d["SGL Unique Model Code"] not in unique_codes]

print(f'Total data {len(model_data)}')

# Function to split the list into chunks
def chunkify(lst, n):
    """Splits the list into n chunks."""
    return [lst[i::n] for i in range(n)]


# Function to scrape data
def scrape_data(model_data_chunk):
    scraper = PartScraper(parts_model=model_data_chunk)
    scraper.scrape_parts_models()


# Number of threads based on the number of headers
no_of_threads = 20
model_data_chunks = chunkify(model_data, no_of_threads)

# Run the scrape_data function in concurrent threads
with ThreadPoolExecutor(max_workers=no_of_threads) as executor:
    futures = [
        executor.submit(scrape_data, i)
        for i in model_data_chunks
    ]
    for future in as_completed(futures):
        future.result()  # Process each future as it completes
