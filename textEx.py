import pandas as pd
import os
import re
import regex
import csv


def _readData(targetTable :str,method:str) -> dict:
    
    if method == "LOCAL":
        dir = os.getcwd() + "/conversion_table/"
        if targetTable == "BRAND":
            dir += "brand_conversion.csv"
        elif targetTable == "COUNTRY":
            dir += "country_conversion.csv"
        elif targetTable == "SPEC":
            dir += "spec_conversion.csv"
        elif targetTable == "PRODUCT":
            dir += "product_conversion.csv"
        elif targetTable == "WAREHOUSE":
            dir += "warehouse_conversion.csv"
        elif targetTable == "SUPPLIER":
            dir += "supplier_conversion.csv"
        elif targetTable == "CATEGORY":
            dir += "product_conversion.csv"
        elif targetTable == "PACKING":
            dir += "packing_conversion.csv"
        elif targetTable == "WEIGHTUNIT":
            dir += "weightunit_conversion.csv"
        else:
            raise TypeError("Undefined type: " + targetTable)

        df = pd.read_csv(dir)
        if targetTable == "PRODUCT":
            #product is a special case. There is a "category" column which affects the algorithm 
            df = df.drop(["category"], axis=1)
        elif targetTable == "CATEGORY":
            df = df[['category', 'Standard_product']]
            categories_order = ['Wagyu'] + sorted(df['category'].unique().tolist())
            categories_order.remove('Wagyu')
            df['category'] = pd.Categorical(df['category'], categories=categories_order, ordered=True)
            

            # Group by 'category' and convert to dictionary
            category_dict = df.groupby('category')['Standard_product'].apply(list).to_dict()

            if 'Wagyu' in category_dict:
                wagyu_products = category_dict['Wagyu']
                # Create a new dictionary with "Wagyu" first
                new_category_dict = {'Wagyu': wagyu_products}
                # Add the rest of the categories except "Wagyu"
                for category, products in category_dict.items():
                    if category != 'Wagyu':
                        new_category_dict[category] = products
                category_dict = new_category_dict
                
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

def _compareString(stringValue: str, textlist: list) -> bool:
    stringValueLower = stringValue.lower()  # Convert stringValue to lowercase
    for text in textlist:
        if str(text).lower() in stringValueLower:  # Convert text to lowercase and compare
            return True
    return False

def _compareString_v2(stringValue: str, textlist: list) -> (bool, bool):
    stringValueLower = stringValue.lower()
    partial_match = False
    exact_match = False
    for text in textlist:
        text_lower = str(text).lower()
        if text_lower in stringValueLower:
            partial_match = True
            # Check for exact matches by splitting words and checking
            if text_lower == stringValueLower or f" {text_lower} " in f" {stringValueLower} "  :
                exact_match = True
                break
    return partial_match, exact_match

def _match_v2(concatText: str, dataDict: dict) -> str:
    concatTextLower = concatText.lower()
    best_match = None
    for key, value in dataDict.items():
        partial_match, exact_match = _compareString_v2(concatTextLower, [key] + list(value) )
        
        # Prioritize exact matches first
        if exact_match:
            if key.lower() == concatTextLower:
                return key  # Return immediately if the key itself is an exact match
            if not best_match:
                best_match = key
        elif partial_match and not best_match:
            best_match = key  # Consider partial matches if no exact match has been found yet

    return best_match

def _match(concatText: str, dataDict: dict) -> str:
    concatTextLower = concatText.lower()  # Convert concatText to lowercase for case-insensitive comparison
    for key, value in dataDict.items():
        if _compareString(concatTextLower, list(value)) or key.lower() in concatTextLower:
            return key
    return None

def _matchList(concatText: str, dataDict: dict) -> list:
    returnList = []
    concatTextLower = concatText.lower()  # Convert concatText to lowercase for case-insensitive comparison
    for key, value in dataDict.items():
        if _compareString(concatTextLower, list(value)) or (key.lower() in concatTextLower):
            returnList.append(key)
            
    return returnList


def getBrand(concatText:str) -> str :
    # this function return the strandard brand name 
    standardName = ""
    brandDict = _readData("BRAND","LOCAL")
    standardName = _match_v2(concatText,brandDict)

    if standardName == "":
        print("no _match is found :" + concatText)
    
    if standardName is not None:
        return standardName.upper()
    
    return standardName

def getCountry(concatText:str) -> str :
    standardCountry = ""
    CountryDict = _readData("COUNTRY","LOCAL")
    standardCountry = _match_v2(concatText,CountryDict)

    if standardCountry == "":
        print("no _match is found :" + concatText)
        return ""
    return standardCountry

def getSpec(concatText:str) -> list:
    standardSpec = []
    specDict = _readData("SPEC","LOCAL")
    standardSpec = _matchList(concatText,specDict)
    if not standardSpec:
        print("no _match is found")
    return [s.upper() if isinstance(s, str) else s for s in standardSpec]

def getProduct(concatText:str) -> str:
    standardProduct = ""
    productDict = _readData("PRODUCT","LOCAL")
    standardProduct = _match_v2(concatText, productDict)
    if standardProduct == "":
        print("no _match is found")
    if standardProduct is not None:
        return standardProduct.upper()

    return ""
    

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
    supplier = _match_v2(concatText,supplierDict)
    if supplier == "":
        print("no _match is found")
    return supplier
    

def getCategory(concatText:str) -> str:
    product = getProduct(concatText)
    if product != "":
        categoryDict = _readData("CATEGORY","LOCAL")
        category = _match_v2(product,categoryDict)
        if category is not None:
            return category.upper()
        

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
    packing = _match_v2(concatText,packingDict)
    if packing == None:
        print("no _match is found")
    return packing

def getPrice(concatText: str) -> float:
    # Direct and simplified regex pattern focusing on capturing numeric values
    # Optionally preceded by $ and followed by zero or more spaces and then units or the end of the string
    pattern = r"\$?\s*(\d+(?:\.\d+)?)\s*(?:KG|LB|/KG|/P|b|/lb|/磅|/包|/k|\Z)?"
    
    # Searching for all matches, considering case insensitivity for units
    matches = re.findall(pattern, concatText, flags=re.IGNORECASE)

    if matches:
        # Assuming the first match is the relevant price
        try:
            return float(matches[-1])
        except ValueError:
            print(f"Conversion issue with: '{concatText}', found: {matches[0]}")
            return 0.0

    print(f"No valid price found in: '{concatText}'")
    return None

def getPriceWord(concatText: str) -> float:
    # Regex pattern focusing on capturing numeric values preceded by $ or before specified symbols
    pattern = r"(?:^|\$|\b(?:/|P|p|B|b|KG|k|磅|公斤|LB|lb|包|kg)\b)(\d+(?:\.\d+)?)"
    
    # Searching for all matches, considering case insensitivity for units
    matches = re.findall(pattern, concatText, flags=re.IGNORECASE)

    if matches:
        # Assuming the last match is the relevant price
        try:
            return float(matches[-1])
        except ValueError:
            print(f"Conversion issue with: '{concatText}', found: {matches[0]}")
            return None

    print(f"No valid price found in: '{concatText}'")
    return None  

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
        return "lb"
    return weightUnit[-1]

def _add_tag_to_row(target_file: str, row_number: int, new_tag: str):
    """
    Adds a new tag to the last column of a specific row in a CSV file, filling any empty columns first.
    
    Args:
    target_file (str): The path to the CSV file.
    row_number (int): The row number (1-based index) to modify.
    new_tag (str): The tag to add to the last column of the specified row.
    """
    try:
        # Read all rows from the file
        with open(target_file, mode='r', newline='') as file:
            rows = list(csv.reader(file))

        # Check if the specified row number is within the range of existing rows
        if 0 < row_number <= len(rows):
            # Target the specific row (convert row_number from 1-based to 0-based)
            target_row = rows[row_number - 1]

            # Find the first empty column in the row, if any
            try:
                empty_index = target_row.index('')
                target_row[empty_index] = new_tag  # Fill the first empty column found
            except ValueError:
                # No empty columns found, append new tag to the end
                target_row.append(new_tag)
            
            # Write the modified rows back to the file
            with open(target_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            print("Tag added successfully.")
        else:
            print(f"Row {row_number} does not exist in the file.")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def _find_tag_in_csv(target_file: str, tag: str) -> int:
    """
    Search for a tag in a CSV file. Returns the row number where the tag is found.
    If the tag is not found, returns -1.

    Args:
    target_file (str): The path to the CSV file.
    tag (str): The tag to search for.

    Returns:
    int: The row number of the found tag, or -1 if the tag is not found.
    """
    try:
        with open(target_file, mode='r', newline='') as file:
            reader = csv.reader(file)
            # Iterate through rows in the file
            for index, row in enumerate(reader):
                if tag in row:  # Check if tag is in any column of the row
                    return index + 1  # Return row number (1-based index)
    except FileNotFoundError:
        print("File not found.")
        return -1  # Optionally, could raise an exception or handle differently
    except Exception as e:
        print(f"An error occurred: {e}")
        return -1

    return -1  # Return -1 if the tag is not found in any row

def _add_tag_to_last_row(target_file: str, new_tag: str):
    """
    Appends a new tag to the last row of a CSV file.

    Args:
    target_file (str): The path to the CSV file.
    new_tag (str): The tag to append to the last row.
    """
    try:
        # Open the file in append mode
        with open(target_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Append a new row with the new tag
            writer.writerow([])
            writer.writerow([new_tag])
        print("Tag added successfully to the last row.")
    except FileNotFoundError:
        print("File not found. Please check the path.")
    except Exception as e:
        print(f"An error occurred: {e}")

def _add_tag_to_last_row_category(target_file: str, new_tag: str,category):
    """
    Appends a new tag to the last row of a CSV file.

    Args:
    target_file (str): The path to the CSV file.
    new_tag (str): The tag to append to the last row.
    """
    try:
        # Open the file in append mode
        with open(target_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Append a new row with the new tag
            writer.writerow([])
            writer.writerow([category,new_tag])
        print("Tag added successfully to the last row.")
    except FileNotFoundError:
        print("File not found. Please check the path.")
    except Exception as e:
        print(f"An error occurred: {e}")

def _canFindTag(rowNum:int)->bool :
    if rowNum == -1:
        return False;
    else:
        return True

def addCommonName(target_file: str, newCommonName: str, oldCommonName = None, category = None) -> bool:

    dir = os.getcwd() + "/conversion_table/"
    if target_file == "BRAND":
        dir += "brand_conversion.csv"
    elif target_file == "COUNTRY":
        dir += "country_conversion.csv"
    elif target_file == "SPEC":
        dir += "spec_conversion.csv"
    elif target_file == "PRODUCT":
        dir += "product_conversion.csv"
    elif target_file == "WAREHOUSE":
        dir += "warehouse_conversion.csv"
    elif target_file == "SUPPLIER":
        dir += "supplier_conversion.csv"
    elif target_file == "PACKING":
        dir += "packing_conversion.csv"
    elif target_file == "WEIGHTUNIT":
        dir += "weightunit_conversion.csv"
    else:
        raise TypeError("Undefined type: " + target_file)
        return False
    


    if oldCommonName is not None:
        rowNum = _find_tag_in_csv(dir,oldCommonName) # find the corresponding row of the current tag
        if not _canFindTag(rowNum):
            print("找不到所需的標籤")
            return False
        else: #old name does exist
            newRowNum = _find_tag_in_csv(dir,newCommonName) 
            
            if not _canFindTag(newRowNum):
                _add_tag_to_row(dir,rowNum,newCommonName)
                print("tag successfully added")
                return True
            else:
                print("標籤已經存在a")
                return False
    else:
        rowNum = _find_tag_in_csv(dir,newCommonName)
        
        if not _canFindTag(rowNum): # cannot found tag

            if target_file != "PRODUCT":
                _add_tag_to_last_row(dir,newCommonName)
                return True
            else: # is product
                if category is not None:
                    _add_tag_to_last_row_category(dir,category,newCommonName)
                    return True
                else:
                    print("缺少category")
                    return False
        else:
            print("標籤已經存在b")
            return False
        



