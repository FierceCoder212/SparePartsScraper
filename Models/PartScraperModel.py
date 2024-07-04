from Models.PartCategoryModel import PartCategoryModel


class PartScraperModel:

    def __init__(self, model_code: str, url: str):
        self.model_code = model_code
        self.url = url
        self.categories = []
