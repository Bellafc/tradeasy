def getProductByCategory(connection, category:str, effectiveDate: datetime, days: int = 2) -> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Calculate the date range
        start_date = effectiveDate - timedelta(days=days)
        end_date = effectiveDate 

        # Define the SQL query, using placeholders for parameters
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE category = %s
        AND effectiveDate BETWEEN %s AND %s
        ORDER BY effectiveDate;
        """

        # Execute the query with the specified parameters
        cursor.execute(query, (category, start_date, end_date))

        # Fetch all the results
        result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()

    return df

def getProductBySupplier(connection, supplier:str, effectiveDate: datetime, days: int = 2)-> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Calculate the date range
        start_date = effectiveDate - timedelta(days=days)
        end_date = effectiveDate 

        # Define the SQL query, using placeholders for parameters
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE supplier = %s
        AND effectiveDate BETWEEN %s AND %s
        ORDER BY effectiveDate;
        """

        # Execute the query with the specified parameters
        cursor.execute(query, (supplier, start_date, end_date))

        # Fetch all the results
        result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        dfCol = df.columns
        # Ensures products are unique and most likely effective 
        df_sorted = df.sort_values(by=['productTag', 'brand', 'supplier','origin', 'spec1', 'weightUnit', 'effectiveDate'])
        #update with latest quotation
        
        df_new = df_sorted.drop_duplicates(subset=['productTag', 'brand','supplier', 'origin', 'spec1', 'weightUnit'], keep='last')
        df_sorted_by_price = df_new.sort_values(by='price', ascending=True)
        df_new = df_sorted_by_price.drop_duplicates(subset=['productTag', 'brand', 'supplier', 'origin', 'spec1', 'weightUnit'], keep='first')
         # reorganize column
        df_new = df_new.sort_values(by="productTag")
        df = df_new[dfCol]
        


    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()

    return df



def getBestQuote(connection,effectiveDate: datetime, days: int = 5) -> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Calculate the date range
        start_date = effectiveDate - timedelta(days=days)
        end_date = effectiveDate 

        # Define the SQL query, using placeholders for parameters
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE effectiveDate BETWEEN %s AND %s
        ORDER BY effectiveDate;
        """

        # Execute the query with the specified parameters
        cursor.execute(query, (start_date, end_date))


        # Fetch all the results
        result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        dfCol = df.columns
        # Ensures products are unique and most likely effective 
        df_sorted = df.sort_values(by=['productTag', 'brand', 'supplier','origin', 'spec1', 'weightUnit', 'effectiveDate'])
        #update with latest quotation
        
        df_new = df_sorted.drop_duplicates(subset=['productTag', 'brand','supplier', 'origin', 'spec1', 'weightUnit'], keep='last')
        df_sorted_by_price = df_new.sort_values(by='price', ascending=True)
        df_new = df_sorted_by_price.drop_duplicates(subset=['productTag', 'brand', 'supplier', 'origin', 'spec1', 'weightUnit'], keep='first')
         # reorganize column
        df_new = df_new.sort_values(by="productTag")
        df = df_new[dfCol]
        


    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()
    
    return df

def getBestQuote_SunLok(connection,effectiveDate: datetime, days: int = 30) -> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Calculate the date range
        start_date = effectiveDate - timedelta(days=days)
        end_date = effectiveDate 

        # Define the SQL query, using placeholders for parameters
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE effectiveDate BETWEEN %s AND %s AND supplier = "新樂"
        ORDER BY effectiveDate;
        """

        # Execute the query with the specified parameters
        cursor.execute(query, (start_date, end_date))


        # Fetch all the results
        result = cursor.fetchall()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        dfCol = df.columns
        # Ensures products are unique and most likely effective 
        df_sorted = df.sort_values(by=['productTag', 'brand', 'supplier','origin', 'spec1', 'weightUnit', 'effectiveDate'])
        #update with latest quotation
        
        df_new = df_sorted.drop_duplicates(subset=['productTag', 'brand','supplier', 'origin', 'spec1', 'weightUnit'], keep='last')
        df_sorted_by_price = df_new.sort_values(by='price', ascending=True)
        df_new = df_sorted_by_price.drop_duplicates(subset=['productTag', 'brand', 'supplier', 'origin', 'spec1', 'weightUnit'], keep='first')
         # reorganize column
        df_new = df_new.sort_values(by="productTag")
        df = df_new[dfCol]
        


    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()
    
    return df

def getQuoteByID(connection, product_id) -> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Define the SQL query, using a placeholder for the product_id parameter
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE product_id = %s;
        """

        # Execute the query with the specified parameter
        cursor.execute(query, (product_id,))

        # Fetch all the results
        result = cursor.fetchall()

        # If result is empty, return an empty DataFrame
        if not result:
            return pd.DataFrame()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()

    return df

def getQuoteBySupplier(connection, supplier) -> pd.DataFrame:
    try:
        cursor = connection.cursor()

        # Define the SQL query, using a placeholder for the product_id parameter
        query = """
        SELECT *
        FROM Tradeasy_quotation
        WHERE supplier = %s;
        """

        # Execute the query with the specified parameter
        cursor.execute(query, (supplier,))

        # Fetch all the results
        result = cursor.fetchall()

        # If result is empty, return an empty DataFrame
        if not result:
            return pd.DataFrame()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

    except Error as e:
        print(f"Error: {e}")
        df = pd.DataFrame()  # Return an empty DataFrame in case of error

    finally:
        if cursor is not None:
            cursor.close()

    return df


