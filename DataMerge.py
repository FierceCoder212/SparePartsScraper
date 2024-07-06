# from Helpers.SqlLiteHelper import SQLiteHelper
#
# all_sql_lite_helper = SQLiteHelper('Databases\\All Scraped Data.db')
# user_sql_lite_helper = SQLiteHelper(r'Scraped Parts.db')
#
# user_data = user_sql_lite_helper.get_all()
# all_sql_lite_helper.insert_many_records_tuple(user_data)
import os.path

from Helpers.SqlLiteHelper import SQLiteHelper

base_path = 'Databases'
all_data_path = 'Scraped Data.db'
all_sql_lite_helper = SQLiteHelper(os.path.join(base_path, all_data_path))
count = 0
user_data = SQLiteHelper('Scraped Parts.db').get_all()
count += len(user_data)
print(f'Total count {count}')
all_sql_lite_helper.insert_many_records_tuple(user_data)
