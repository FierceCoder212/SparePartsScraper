import json

from Helpers.SqlLiteHelper import SQLiteHelper

with open('url_data.json', 'r') as json_file:
    all_data = json.loads(json_file.read())
with open('part_2.json', 'r') as json_file:
    user_data = json.loads(json_file.read())
user_data = [d["SGL Unique Model Code"] for d in user_data]
sql_lite_helper = SQLiteHelper('All Scraped Data.db')
unique_codes = sql_lite_helper.get_sgl_codes()
model_data = [d for d in all_data if
              d["SGL Unique Model Code"] not in unique_codes and d["SGL Unique Model Code"] not in user_data]
with open('part_remaining.json', 'w') as remaining_data_file:
    remaining_data_file.write(json.dumps(model_data, indent=4))
