# the get method is currently using local csv in long run it should be updated to AWS
import pandas as pd
import os
import re


def _readData(targetTable :str,method:str) -> dict:
    
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

def _compareString(stringValue:str, textlist:list)-> str:
    for text in textlist:
        if str(text) in str(stringValue) :
            return True
    return False

def _match(concatText:str, dataDict:dict,) -> str:
    for key, value in dataDict.items():
        if _compareString(concatText,list(value)) or key in concatText:
            return key
    return None

def _matchList(concatText:str, dataDict:dict,) -> list:
    returnList = []
    for key, value in dataDict.items():
        if _compareString(concatText,list(value)) or (key in concatText):
            returnList.append(key)
            
    return returnList


def getBrand(concatText:str) -> str :
    # this function return the strandard brand name 
    standardName = ""
    brandDict = _readData("BRAND","LOCAL")
    standardName = _match(concatText,brandDict)

    if standardName == "":
        print("no _match is found")
    
    return standardName

def getCountry(concatText:str) -> str :
    standardCountry = ""
    CountryDict = _readData("COUNTRY","LOCAL")
    standardCountry = _match(concatText,CountryDict)

    if standardCountry == "":
        print("no _match is found")
    return standardCountry

def getSpec(concatText:str) -> list:
    standardSpec = []
    specDict = _readData("SPEC","LOCAL")
    standardSpec = _matchList(concatText,specDict)
    if not standardSpec:
        print("no _match is found")
    return standardSpec

def getProduct(concatText:str) -> str:
    standardProduct = ""
    productDict = _readData("PRODUCT","LOCAL")
    standardProduct = _matchList(concatText, productDict)
    if standardProduct == "":
        print("no _match is found")
    return standardProduct

def getWarehoue(concatText:str) -> list:
    standardWarehoue = []
    warehouseDict = _readData("WAREHOUSE","LOCAL")
    standardWarehoue = _matchList(concatText,warehouseDict)
    if not standardWarehoue:
        print("no _match is found")
    return standardWarehoue