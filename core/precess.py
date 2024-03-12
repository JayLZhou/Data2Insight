import csv
import json

# 初始化一个空字典来存储信息
db_info = {
    'db_id': 'austin_crimes',
    'table_names_original': [],
    'table_names': [],
    'column_names_original': [],
    'column_names': [],
    'column_types': [],
    'primary_keys': [],  # 这里需要额外信息，假设暂时留空
    'foreign_keys': [],  # 同上，需要额外信息
    # 其余字段根据实际情况添加
}
db_info['table_names_original'].append("austin_Crime")
# 读取CSV文件
with open('/home/yingli/work/MAC-SQL/data/foo/test_databases/austin_Crime/database_description/austin_crime.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        import pdb
        # pdb.set_trace()
        # table_name_original = row['table_name']
        column_name_original = row['\ufefforiginal_column_name']
        column_names = row['column_name']
        column_type = row['data_format']

        column_name = column_name_original.lower()
        
        # 更新db_info字典
        
        db_info['column_names_original'].append((0, column_name_original))
        db_info['column_names'].append((0, column_name))
        db_info['column_types'].append(column_type)

# 计算额外的统计信息
db_info['table_count'] = len(db_info['table_names'])
# 其余统计字段根据需要计算

# 写入到JSON文件
with open('db_info.json', 'w') as json_file:
    json.dump(db_info, json_file, indent=4)
