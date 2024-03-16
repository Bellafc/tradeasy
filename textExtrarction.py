import pandas as pd

def get_brand_dict():
    brand_df = pd.read_csv("/content/drive/MyDrive/brand_conversion_table.csv")
    brand_df = brand_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    brand_df = brand_df.T
    new_columns = brand_df.iloc[0]
    df_new = brand_df[1:].reset_index(drop=True)
    df_new.columns = new_columns
    result_dict = df_new.to_dict('list')
    brand_dict = {k: [i for i in v if type(i) != float] for k, v in result_dict.items()}
    brand_dict['ibp'].append("i. b. p.")
    brand_dict['ibp'].append("i. b. p")
    brand_dict['frimesa'].append("frimsa")
    brand_dict['fortefrigo'] = None
    brand_dict['lkj'] = None
    brand_dict['nossobeef'] = None
    brand_dict['national'] = None
    brand_dict['swift'] = None
    brand_dict['kiwi'] = None
    return brand_dict

def get_brand_list(brand_dict):
    brand_list = []
    for key, values in brand_dict.items():
        brand_list.append(key)
        try:
            brand_list.extend(values)
        except:
            print(key)
    return brand_list

def get_origin_list():
    origin_list = ['西', '巴', '德', '丹', '波', '澳', '中', '匈牙利', '德', '俄', '愛', '墨', '荷', '阿', '荷 蘭', '挪 威', '英 國', '英', '紐', '法 國', '爱', '加', '美', '德國']
    return origin_list

def get_product_dict():
    product_df = pd.read_csv("/content/drive/MyDrive/Product_conversion_table.csv")
    df_clean = product_df.dropna(axis=1, how='all')
    df_melted = df_clean.melt(id_vars=['category'], value_name='product').dropna(subset=['product']).drop('variable', axis=1)
    df_grouped = df_melted.groupby('category')['product'].apply(list).reset_index()
    product_dict = df_grouped.set_index('category')['product'].to_dict()
    product_dict['Pork'].pop()
    product_dict['Pork'].remove('筒骨')
    return product_dict

def get_product_list(product_dict):
    product_list = []
    for key, values in product_dict.items():
        for value in values:
            product_list.append(value)
    return product_list

def get_grade_dict():
    grade_df = pd.read_csv("/content/drive/MyDrive/grade_conversion.csv")
    grade_df = grade_df.T
    grade_df = grade_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    new_columns = grade_df.iloc[0]
    df_new = grade_df[1:].reset_index(drop=True)
    df_new.columns = new_columns
    result_dict = df_new.to_dict('list')
    grade_dict = {k: [i for i in v if type(i) != float] for k, v in result_dict.items()}
    del grade_dict['m']
    del grade_dict['s']
    del grade_dict['l']
    del grade_dict['a']
    return grade_dict

def get_grade_list(grade_dict):
    grade_list = []
    for key, values in grade_dict.items():
        grade_list.append(key)
        grade_list.extend(values)
    return grade_list
def split_name(row):
    origin, brand, name, grade = None, None, None, ""

    for origin_item in origin_list:
        if origin_item in row['貨名']:
            origin = origin_item
            break

    for brand_item in brand_list:
        if brand_item in row['貨名']:
            parts = row['貨名'].split(brand_item, 1)
            brand = brand_item
            break

    for grade_item in grade_list:
        if grade_item in row['貨名']:
            grade += grade_item + ','

    for product_item in product_list:
        if product_item in row['貨名']:
            name = product_item
            break
        if not name:
          parts = row['貨名'].split(brand_item, 1)
          name =parts[-1].strip() if len(parts) > 1 else row['貨名'].strip()


    return pd.Series([origin, brand, name, grade])

def split_grade(df):
    df_cleaned = df.copy()
    grade_split = df_cleaned['grade'].str.split(',')
    df_cleaned['spec1'] = grade_split.str[0]
    df_cleaned['spec2'] = grade_split.str[1]
    df_cleaned['spec3'] = grade_split.str[2]
    df_cleaned['spec4'] = grade_split.str[3]
    df_cleaned['spec5'] = grade_split.str[4]
    df_cleaned = df_cleaned.fillna('')
    return df_cleaned

