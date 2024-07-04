class PartItemModel:

    def __init__(self, part_id: str, part_name: str, part_code: str):
        self.part_id = '' if part_id is None else part_id
        self.part_name = part_name
        self.part_code = part_code