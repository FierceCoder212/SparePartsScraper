from Helpers.SqlLiteHelper import SQLiteHelper

all_sql_lite_helper = SQLiteHelper('All Scraped Data.db')
user_sql_lite_helper = SQLiteHelper(r'D:\Workspace\Projects\SparePartsScrapper\Scraped Parts.db')

user_data = user_sql_lite_helper.get_all()
all_sql_lite_helper.insert_many_records_tuple(user_data)
