# the get method is currently using local csv in long run it should be updated to AWS
import pandas as pd

def readData(targetTable :str) -> pd.DataFrame:
    resultTable = pd.DataFrame()
    match targetTable:
        case "BRAND":
            resultTable = ""
        case "COUNTRY":
            resultTable = ""
        case "SPEC":
            resultTable = ""
        case "PRODUCT":
            resultTable = ""
        case "WAREHOUSE":
            resultTable = ""
        case _:
            raise TypeError("not a point we support")
            

    return 

def match(concatText:str, brand:str) -> bool:
    matched = False
    return matched

def getBrand(concatText:str) -> str :
    # this function return the strandard brand name 
    standardName = ""
    brandList = readData("BRAND")
    for brand in brandList:
        if (match(concatText,brand)):
            standardName = brand
            break
    
    if standardName == "":
        print("no match is found")
    
    return standardName

def getCountry(str) -> str :
    standardCountry = ""
    return standardCountry

def getSpec(str) -> list:
    standardSpec = []
    return standardSpec

def getProduct(str) -> str:
    standardProduct = ""
    return standardProduct

def getWarehoue(str) -> list:
    standardWarehoue = []
    return standardWarehoue