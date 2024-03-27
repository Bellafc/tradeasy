# the get method is currently using local csv in long run it should be updated to AWS
import pandas as pd
import os
import re


def readData(targetTable :str,method:str) -> dict:
    
    if method == "LOCAL":
        dir = os.getcwd() + "/conversion_table/"
        match targetTable:
            case "BRAND":
                dir = dir + "brand_conversion.csv"
            case "COUNTRY":
                dir = dir + "country_conversion.csv"
            case "SPEC":
                dir = dir + "spec_conversion.csv"
            case "PRODUCT":
                dir = dir + "product_conversion.csv"
            case "WAREHOUSE":
                dir = dir + "warehouse_conversion.csv"
            case _:
                raise TypeError("Undefined type : " + targetTable )

        df = pd.read_csv(dir)
        if targetTable == "PRODUCT":
            #product is a special case. There is a "category" column which affects the algorithm 
            df = df.drop(["category"], axis=1)
        
        df = df.map(lambda x: x.lower() if isinstance(x, str) else x).T    
        new_columns = df.iloc[0]
        df_new = df[1:].reset_index(drop=True)
        df_new.columns = new_columns
        result_dict = df_new.to_dict('list')
        dataDict = {k: [i for i in v if type(i) != float] for k, v in result_dict.items()}
        return dataDict
    
    elif method == "AWS":
        return
            

    return 

def compareString(stringValue:str, textlist:list)-> str:
    for text in textlist:
        if str(text) in str(stringValue) :
            return True
    return False

def match(concatText:str, dataDict:dict,) -> str:
    for key, value in dataDict.items():
        if compareString(concatText,list(value)) or key in concatText:
            return key
    return None

def matchList(concatText:str, dataDict:dict,) -> list:
    returnList = []
    for key, value in dataDict.items():
        if compareString(concatText,list(value)) or (key in concatText):
            returnList.append(key)
            
    return returnList


def getBrand(concatText:str) -> str :
    # this function return the strandard brand name 
    standardName = ""
    brandDict = readData("BRAND","LOCAL")
    standardName = match(concatText,brandDict)

    if standardName == "":
        print("no match is found")
    
    return standardName

def getCountry(concatText:str) -> str :
    standardCountry = ""
    CountryDict = readData("COUNTRY","LOCAL")
    standardCountry = match(concatText,CountryDict)

    if standardCountry == "":
        print("no match is found")
    return standardCountry

def getSpec(concatText:str) -> list:
    standardSpec = []
    specDict = readData("SPEC","LOCAL")
    standardSpec = matchList(concatText,specDict)
    if not standardSpec:
        print("no match is found")
    return standardSpec

def getProduct(concatText:str) -> str:
    standardProduct = ""
    productDict = readData("PRODUCT","LOCAL")
    standardProduct = matchList(concatText, productDict)
    if standardProduct == "":
        print("no match is found")
    return standardProduct

def getWarehoue(concatText:str) -> list:
    standardWarehoue = []
    warehouseDict = readData("WAREHOUSE","LOCAL")
    standardWarehoue = matchList(concatText,warehouseDict)
    if not standardWarehoue:
        print("no match is found")
    return standardWarehoue