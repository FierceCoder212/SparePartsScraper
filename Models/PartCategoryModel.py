from urllib.parse import urljoin
from Models.PartItemModel import PartItemModel

class PartCategoryModel:

    def __init__(self, url: str, base_url: str, name: str):
        self.url = urljoin(base=base_url, url=url)
        self.name = name
        self.img = None
        self.items = []

    def set_items(self, items: list[PartItemModel]):
        self.items = items