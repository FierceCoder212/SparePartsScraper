import json
import math

from Helpers.SqlLiteHelper import SQLiteHelper


def split_list(lst, n):
    part_size = len(lst) / n
    parts = []
    for i in range(n):
        start_index = int(math.floor(i * part_size))
        end_index = int(math.floor((i + 1) * part_size))
        part = lst[start_index:end_index]
        parts.append(part)

    return parts


def save_parts_as_json(parts):
    for i, part in enumerate(parts):
        filename = f"part_{i + 1}.json"
        with open(filename, 'w') as f:
            json.dump(part, f, indent=4)


sql_lite_helper = SQLiteHelper('Scraped Parts.db')
unique_codes = sql_lite_helper.get_sgl_codes()

# Load JSON data
with open('url_data.json', 'r') as json_file:
    data = json.loads(json_file.read())
model_data = [d for d in data if
              d["SGL Unique Model Code"] not in unique_codes]

n = 5  # Number of parts to split the list into

# Split the list into n parts
parts = split_list(model_data, n)

# Save each part as a new JSON file
save_parts_as_json(parts)
