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
