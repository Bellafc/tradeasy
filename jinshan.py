import pdfplumber
import pandas as pd
import numpy as np
import os
import textEx
from datetime import datetime


def readAllJinShanPDF(dir:str) -> pd.DataFrame:
    column_names = ['重量', '貨名', '單價', '單位', '倉位', '重量', '貨名', '單價', '單位', '倉位', '重量', '貨名', '單價', '單位', '倉位']

    all_pages_df = pd.DataFrame(columns=column_names)
    all_pages_df.insert(5, 'date',None) 
    all_pages_df.insert(11, 'date2',None)  
    all_pages_df.insert(17, 'date3', None) 

    for filename in os.listdir(dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(dir, filename)

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        # 动态获取列名
                        try:
                            df = pd.DataFrame(table[1:], columns=column_names)
                            df.insert(5, 'date', filename) 
                            df.insert(11, 'date2', filename) 
                            df.insert(17, 'date3', filename)
                        except:
                            df=pd.DataFrame(table[1:])
                        try:
                            all_pages_df = pd.concat([all_pages_df, df], ignore_index=True)
                        except:
                            print(f"Error merging data from {filename},{page}")
    df1 = all_pages_df.iloc[:, :6]
    df2 = all_pages_df.iloc[:, 6:12]
    df3 = all_pages_df.iloc[:, 12:18]
    df2.columns = df1.columns
    df3.columns = df1.columns
    df_concatenated_corrected = pd.concat([df1, df2, df3], axis=0).reset_index(drop=True)
    df_concatenated_corrected=df_concatenated_corrected.dropna()
    df = df_concatenated_corrected.applymap(lambda x: x.strip() if isinstance(x, str) else x).replace('', np.nan)
    df_cleaned = df.dropna(subset=["貨名"], how='any').reset_index(drop=True)
    df_cleaned = df_cleaned.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    return df_cleaned


def readJinShanPDF(dir:str) -> pd.DataFrame:
    column_names = ['重量', '貨名', '單價', '單位', '倉位', '重量', '貨名', '單價', '單位', '倉位', '重量', '貨名', '單價', '單位', '倉位']

    all_pages_df = pd.DataFrame(columns=column_names)
    all_pages_df.insert(5, 'date',None) 
    all_pages_df.insert(11, 'date2',None)  
    all_pages_df.insert(17, 'date3', None) 

  
    file_path = dir

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                # 动态获取列名
                try:
                    df = pd.DataFrame(table[1:], columns=column_names)
                    df.insert(5, 'date', os.path.basename(file_path)) 
                    df.insert(11, 'date2', os.path.basename(file_path)) 
                    df.insert(17, 'date3', os.path.basename(file_path))
                except:
                    df=pd.DataFrame(table[1:])
                try:
                    all_pages_df = pd.concat([all_pages_df, df], ignore_index=True)
                except:
                    print(f"Error merging data from {os.path.basename(file_path)},{page}")
                    
    df1 = all_pages_df.iloc[:, :6]
    df2 = all_pages_df.iloc[:, 6:12]
    df3 = all_pages_df.iloc[:, 12:18]
    df2.columns = df1.columns
    df3.columns = df1.columns
    df_concatenated_corrected = pd.concat([df1, df2, df3], axis=0).reset_index(drop=True)
    df_concatenated_corrected=df_concatenated_corrected.dropna()
    df = df_concatenated_corrected.applymap(lambda x: x.strip() if isinstance(x, str) else x).replace('', np.nan)
    df_cleaned = df.dropna(subset=["貨名"], how='any').reset_index(drop=True)
    df_cleaned = df_cleaned.applymap(lambda x: x.lower() if isinstance(x, str) else x)

    return df_cleaned

def _specToList(spec :list) -> list:

    # Sort 'spec' in alphabetical order
    spec.sort()

    # Initialize variables with empty strings
    spec1 = spec2 = spec3 = spec4 = spec5 = spec6 = ""

    # Assign values from 'spec' to 'spec1' to 'spec6' based on the length of 'spec'
    if len(spec) > 0:
        spec1 = spec[0]
    if len(spec) > 1:
        spec2 = spec[1]
    if len(spec) > 2:
        spec3 = spec[2]
    if len(spec) > 3:
        spec4 = spec[3]
    if len(spec) > 4:
        spec5 = spec[4]
    if len(spec) > 5:
        spec6 = spec[5]

    return [spec1,spec2,spec3,spec4,spec5,spec6]
        

def getJinShanQuote(df: pd.DataFrame) -> pd.DataFrame:
    
    df['specs'] = df['貨名'].apply(textEx.getSpec)
    df['brand'] = df['貨名'].apply(textEx.getBrand)
    for index, row in df.iterrows():
        if row['brand'] is not None:
            df.at[index, 'productName'] = row['貨名'].replace(row['brand'], '')
        else:
            df.at[index, 'productName'] = row['貨名']
    df['productTag'] = df['貨名'].apply(textEx.getProduct)
    df['supplier'] = '金山'
    df['category'] = df['貨名'].apply(textEx.getCategory)
    df['packing']=df['重量'].apply(textEx.getPacking)
    df['origin'] = df['貨名'].apply(textEx.getCountry)
    df['effectiveDate'] = df['date'].str.replace('.pdf', '').replace(" ", "-").replace("-updated","")
    for i in range(len(df)):
        try:
            df['effectiveDate'][i] = datetime.strptime(df['effectiveDate'][i], "%d-%b-%y")
        except ValueError:
            try:
                df['effectiveDate'][i] = datetime.strptime(df['effectiveDate'][i], "%d-%B-%y")
            except ValueError:
                df['effectiveDate'][i]=df['effectiveDate'][i]
    df[['spec1', 'spec2', 'spec3', 'spec4', 'spec5', 'spec6']] = df['specs'].apply(lambda x: pd.Series(_specToList(x)))
    df['price'] = df['單價'].str.replace('$','').replace(" ","")
    df['weightUnit'] = df['單位'].apply(textEx.getWeightUnit)
    df['warehouse']=df['倉位'].apply(textEx.getWarehoue)
    df['notes']= None

    df = df.explode('warehouse')
    df['warehouse'] = df['warehouse'].astype(str)

    required_columns = [
    'productName', 'productTag', 'supplier', 'category', 'packing',
    'origin', 'brand', 'effectiveDate', 'spec1', 'spec2', 'spec3',
    'spec4', 'spec5', 'spec6', 'price', 'weightUnit', 'warehouse', 'notes'
    ]
    df=df[required_columns]
    return df