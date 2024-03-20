##-----------------------  GET STANDARD LIST --------------------------------------------------------------------------------------------------------------------------##
####brand
def get_brand_dict(brand_df):
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

##origin
def get_origin_list():
    return ['西', '巴', '德', '丹', '波', '澳', '中', '匈牙利', '德', '俄', '愛', '墨', '荷', '阿', '荷 蘭', '挪 威', '英 國', '英', '紐', '法 國', '爱', '加', '美', '德國']

##product
def get_product_dict(product_df):
    df_clean = product_df.dropna(axis=1, how='all')
    df_melted = df_clean.melt(id_vars=['category'], value_name='product').dropna(subset=['product']).drop('variable', axis=1)
    df_grouped = df_melted.groupby('category')['product'].apply(list).reset_index()
    product_dict = df_grouped.set_index('category')['product'].to_dict()
    product_dict['Pork'].pop()
    product_dict['Pork'].remove('筒骨')
    product_list = []
    for key, values in product_dict.items():
        for value in values:
            product_list.append(value)
    value = product_dict.pop('Meatball')
    product_dict['Meatball'] = value
    product_dict['Beef'].append('牛')
    product_dict['Chicken'].append('雞')
    product_dict['Chicken'].append('鸡')
    product_dict['Lamb'].append('羊')
    product_dict['Pork'].append('豬')
    product_dict['Poultry'].append('鴨')
    return product_dict, product_list

##grade
def get_grade_dict(grade_df):
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
    grade_list = []
    for key, values in grade_dict.items():
        grade_list.append(key)
        grade_list.extend(values)
    return grade_dict, grade_list

## Country
def get_country_dict(country_df):
    country_df = country_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    country_df = country_df.T
    new_columns = country_df.iloc[0]
    df_new = country_df[1:].reset_index(drop=True)
    df_new.columns = new_columns
    result_dict = df_new.to_dict('list')
    country_dict = {k: [i for i in v if type(i) != float] for k, v in result_dict.items()}
    country_dict.pop('standard_country')
    country_list = []
    for key, values in country_dict.items():
        country_list.append(key)
        try:
            country_list.extend(values)
        except:
            print(key)
    return country_dict, country_list




brand_df = pd.read_csv("brand_conversion_table.csv")
brand_dict = get_brand_dict(brand_df)
brand_list = get_brand_list(brand_dict)

origin_list = get_origin_list()

product_df = pd.read_csv("Product_conversion_table.csv")
product_dict, product_list = get_product_dict(product_df)

grade_df = pd.read_csv("grade_conversion.csv")
grade_dict, grade_list = get_grade_dict(grade_df)

country_df = pd.read_csv("country_conversion.csv")
country_dict, country_list = get_country_dict(country_df)
##-------------------------------------------  GET COLUMNS --------------------------------------------------------------------------------------------------------------------------##


def get_origin(row, origin_list):
    for origin_item in origin_list:
        if origin_item in row['貨名']:
            return origin_item
    return None

def get_brand(row, brand_list):
    for brand_item in brand_list:
        if brand_item in row['貨名']:
            parts = row['貨名'].split(brand_item, 1)
            return brand_item
    return None

def get_name(row, brand, product_list):
    for product_item in product_list:
        if product_item in row['貨名']:
            return product_item
    if brand:
        parts = row['貨名'].split(brand, 1)
        name = parts[-1].strip() if len(parts) > 1 else row['貨名'].strip()
    else:
        name = row['貨名'].strip()
    return name

def get_grade(row, grade_list):
    grade = ""
    for grade_item in grade_list:
        if grade_item in row['貨名']:
            grade += grade_item + ','
    return grade.rstrip(',')

def get_specs(row):
    specs = row['grade'].split(',')
    spec1 = specs[0] if len(specs) > 0 else ''
    spec2 = specs[1] if len(specs) > 1 else ''
    spec3 = specs[2] if len(specs) > 2 else ''
    spec4 = specs[3] if len(specs) > 3 else ''
    spec5 = specs[4] if len(specs) > 4 else ''
    return pd.Series([spec1, spec2, spec3, spec4, spec5])

def get_category(row, product_dict):
    for category, products in product_dict.items():
        for product in products:
            if product in row['name']:
                return category
    return ''

def get_product_name(row):
    return row['貨名'].replace(row['Origin'], '')

def get_supplier(row):
    return '金山'


df_cleaned['Origin'] = df_cleaned.apply(lambda row: get_origin(row, origin_list), axis=1)
df_cleaned['brand'] = df_cleaned.apply(lambda row: get_brand(row, brand_list), axis=1)
df_cleaned['name'] = df_cleaned.apply(lambda row: get_name(row, row['brand'], product_list), axis=1)
df_cleaned['grade'] = df_cleaned.apply(lambda row: get_grade(row, grade_list), axis=1)
df_cleaned["grade"] = df_cleaned["grade"].str.replace("choice,ch", "choice")
df_cleaned[['spec1', 'spec2', 'spec3', 'spec4', 'spec5']] = df_cleaned.apply(get_specs, axis=1, result_type='expand')
df_cleaned['category'] = df_cleaned.apply(lambda row: get_category(row, product_dict), axis=1)
df_cleaned['product_name'] = df_cleaned.apply(get_product_name, axis=1)
df_cleaned['supplier'] = df_cleaned.apply(get_supplier, axis=1)
