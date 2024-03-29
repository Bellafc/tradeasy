import pandas as pd
import os
import re
import regex


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
            case "SUPPLIER":
                dir = dir + "supplier_conversion.csv"
            case "CATEGORY":
                dir = dir + "category_conversion.csv"
            case "PACKING":
                dir = dir + "packing_conversion.csv"
            case "WEIGHTUNIT":
                dir = dir + "weightunit_conversion.csv"
            case _:
                raise TypeError("Undefined type : " + targetTable )

        df = pd.read_csv(dir)
        if targetTable == "PRODUCT":
            #product is a special case. There is a "category" column which affects the algorithm 
            df = df.drop(["category"], axis=1)
        elif targetTable == "CATEGORY":
            category_dict = df.groupby('category')['Standard_product'].apply(list).to_dict()
            return category_dict
        
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
    stringValueLower = stringValue.lower()  # Convert stringValue to lowercase
    for text in textlist:
        if str(text).lower() in stringValueLower:  # Convert text to lowercase and compare
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
    standardProduct = _match(concatText, productDict)
    if standardProduct == "":
        print("no _match is found")
    return standardProduct

def getWarehoue(concatText:str) -> list:
    # Searches the given string `concatText` for warehouse names and returns a list of found names.
    # Initializes an empty list `standardWarehoue` to store the matching warehouse names.
    # Retrieves a dictionary or list of warehouse names from a local data source through `_readData` with "WAREHOUSE" and "LOCAL" as parameters.
    # Calls `_matchList` to search `concatText` against `warehouseDict`, looking for matches.
    # If matches are found, `standardWarehoue` is updated with the list of matching names; if not, prints a message indicating no match.
    # Returns a list of identified warehouse names, which can be empty if no matches are found.

    standardWarehoue = []
    warehouseDict = _readData("WAREHOUSE","LOCAL")
    standardWarehoue = _matchList(concatText,warehouseDict)
    if not standardWarehoue:
        print("no _match is found")
    return standardWarehoue

def getSupplier(concatText:str) ->str:
    # Searches the given string for a supplier name and returns it.
    # Initializes an empty string `supplier` to store the found supplier name.
    # Retrieves a dictionary or list of supplier names from a local data source via `_readData` with "SUPPLIER" and "LOCAL" as arguments.
    # Uses `_matchList` function to compare `concatText` with `supplierDict` for any matching supplier names.
    # If a matching supplier name is found, `supplier` is set to this name; if not, a message is printed indicating no match.
    # Returns the name of the matched supplier, or an empty string if no match is found.

    supplier = ""
    supplierDict = _readData("SUPPLIER","LOCAL")
    supplier = _match(concatText,supplierDict)
    if supplier == "":
        print("no _match is found")
    return supplier
    

def getCategory(concatText:str) -> str:
    product = getProduct(concatText)
    if product != "":
        categoryDict = _readData("CATEGORY","LOCAL")
        category = _match(concatText,categoryDict)
        return category

    return ""

def getPacking(concatText:str) ->str:
    # Searches the given string `concatText` for packing types and returns the found type.
    # Initializes an empty string `packing` for storing the result.
    # Retrieves a dictionary or list of known packing types from a local data source via `_readData` with "PACKING" and "LOCAL" as parameters.
    # Uses `_matchList` to search `concatText` against `packingDict` for a match.
    # If a match is found, `packing` is updated with the matching packing type; if not, a message indicating no match is printed.
    # Returns the identified packing type, or an empty string if no match is found.

    packing = ""
    packingDict = _readData("PACKING","LOCAL")
    packing = _match(concatText,packingDict)
    if packing == "":
        print("no _match is found")
    return packing

def getPrice(concatText:str) -> float:
    # This function takes a single string argument named `concatText` and returns a floating-point number.
    # It utilizes a regular expression (regex) to search the input text for price figures.
    # The regex pattern is designed to identify numbers (with or without decimal points) that are immediately
    # followed by specific markers or units such as '$', '/', 'KG', 'LB', '/KG', '/P', 'b', '/lb', '/磅', '/包', or '/k',
    # ensuring a broad range of price formats can be recognized and extracted. These markers indicate currency symbols
    # or units of measure but are not included in the match.
    # If a price is found, the first matched number is converted to a float and returned.
    # If no price information is detected, a message is printed to indicate no match was found, and 0.0 is returned.
    # The primary use of this function is to efficiently extract numerical price information from strings that contain
    # pricing data in various formats.
    
    
    pattern = r'(?:(?<=\$)\d+(?:\.\d+)?|\d+(?:\.\d+)?)(?:(?=/)|(?=KG)|(?=LB)|(?=/KG)|(?=/P)|(?=b)|(?=/lb)|(?=/磅)|(?=/包)|(?=/k))'
    match = regex.findall(pattern, concatText)
    if match:
        return float(match[0])
    else:
        print("No match found.")
        return 0.0
    

def getWeightUnit(concatText:str) -> str:
    # This function searches for and returns the weight unit found in a given string `concatText`.
    # It initializes an empty string `weightUnit` to store the found weight unit.
    # The `weightUnitDict` is obtained by calling `_readData` with parameters "WEIGHTUNIT" and "LOCAL",
    # which presumably reads a predefined list or dictionary of weight units from a local data source.
    # `_matchList` function is then called with `concatText` and `weightUnitDict` to search for a matching weight unit in the text.
    # If a match is found, `weightUnit` is set to the matching unit; otherwise, a message is printed indicating no match was found.
    # Finally, the found weight unit (or an empty string if no match is found) is returned.

    weightUnit = []
    weightUnitDict = _readData("WEIGHTUNIT","LOCAL")
    weightUnit = _matchList(concatText,weightUnitDict)
    if not weightUnit :
        print("no _match is found")
    return weightUnit[-1]

