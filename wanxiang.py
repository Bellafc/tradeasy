import pdfplumber
import pandas as pd
import numpy as np
import os
import textEx
from datetime import datetime

def readAllWanXiangPDF(dir:str) -> pd.DataFrame:
    column_names = ['产地', '貨名','倉位', '到取价', '單位','备注']
    all_pages_df = pd.DataFrame(columns=column_names)
    all_pages_df.insert(6, 'date',None) 

    for filename in os.listdir(dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(dir, filename)

            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=column_names)
                        df=df.dropna()
                        df.insert(6, 'date', filename)
                        
                        try:
                            all_pages_df = pd.concat([all_pages_df, df], ignore_index=True)
                        except:
                            print(f"Error merging data from {filename},{page}")
    all_pages_df = all_pages_df[all_pages_df['貨名']!='']

    return all_pages_df

def readWanXiangPDF(dir:str) -> pd.DataFrame:
    column_names = ['产地', '貨名','倉位', '到取价', '單位','备注']
    all_pages_df = pd.DataFrame(columns=column_names)
    all_pages_df.insert(6, 'date',None) 

    file_path = dir

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=column_names)
                df=df.dropna()
                filename = os.path.basename(file_path)
                df.insert(6, 'date', filename)
                
                try:
                    all_pages_df = pd.concat([all_pages_df, df], ignore_index=True)
                except:
                    print(f"Error merging data from {filename},{page}")
    all_pages_df = all_pages_df[all_pages_df['貨名']!='']

    return all_pages_df

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
        

def getWanXiangQuote(df: pd.DataFrame) -> pd.DataFrame:
    
    df['specs'] = df['貨名'].apply(textEx.getSpec)
    df['productName'] = df['貨名']
    df['productTag'] = df['貨名'].apply(textEx.getProduct)
    df['supplier'] = '萬祥'
    df['category'] = df['貨名'].apply(textEx.getCategory)
    df['packing']=df['貨名'].apply(textEx.getPacking)
    df['origin'] = df['产地'].apply(textEx.getCountry)
    df['brand'] = df['貨名'].apply(textEx.getBrand)
    df['effectiveDate'] = df['date'].str.replace('萬祥', '').str.replace(".pdf","").map(lambda x : datetime.strptime(x, "%Y%m%d"))
    df[['spec1', 'spec2', 'spec3', 'spec4', 'spec5', 'spec6']] = df['specs'].apply(lambda x: pd.Series(_specToList(x)))
    df['price'] = df['到取价'].map(lambda x: textEx.getPrice(x))
    df['weightUnit'] = df['單位'].apply(textEx.getWeightUnit)
    df['warehouse']=df['倉位'].apply(textEx.getWarehoue)
    df['notes']= df['备注']

    df = df.explode('warehouse')
    df['warehouse'] = df['warehouse'].astype(str)

    required_columns = [
    'productName', 'productTag', 'supplier', 'category', 'packing',
    'origin', 'brand', 'effectiveDate', 'spec1', 'spec2', 'spec3',
    'spec4', 'spec5', 'spec6', 'price', 'weightUnit', 'warehouse', 'notes'
    ]
    df=df[required_columns]
    return df