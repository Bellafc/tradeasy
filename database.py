import mysql.connector
from mysql.connector import Error
import pandas as pd

def create_table(connection):
    try:
        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS Tradeasy_quotation (
            id INT AUTO_INCREMENT PRIMARY KEY,
            productName VARCHAR(255),
            productTag VARCHAR(255),
            supplier VARCHAR(255),
            category ENUM('Beef', 'Pork', 'Chicken', 'Poultry', 'Lamb', 'Fish', 'Seafood', 'Shrimp', 'Meatballs', 'Premade', 'Vegetables', 'Retail', 'Others'),
            packing VARCHAR(255),
            origin VARCHAR(255),
            brand VARCHAR(255),
            effectiveDate DATE,
            spec1 VARCHAR(255),
            spec2 VARCHAR(255),
            spec3 VARCHAR(255),
            spec4 VARCHAR(255),
            spec5 VARCHAR(255),
            spec6 VARCHAR(255),
            price DECIMAL(10, 2),
            weightUnit ENUM('KG', 'LB', 'PC', 'CTN'),
            warehouse ENUM('嘉里温控貨倉1', '嘉里温控貨倉2', '沙田冷倉1倉', '沙田冷倉2倉', '其士冷藏倉庫', '光輝1倉', '光輝2倉', '威強凍倉', '亞洲生活冷倉', '嘉威倉', '百匯倉', '萬集倉', '萬安倉', '送貨'),
            notes TEXT
        );'''
        cursor.execute(create_table_query)
        print("Table created successfully")
    except mysql.connector.Error as error:
        print(f"Failed to create table in MySQL: {error}")
    finally:
        if connection.is_connected():
            cursor.close()

def insert_product(connection, product_details):
    try:
        cursor = connection.cursor()
        insert_query = '''INSERT INTO Tradeasy_quotation (productName, productTag, supplier, category, packing, origin, brand, effectiveDate, spec1, spec2, spec3, spec4, spec5, spec6, price, weightUnit, warehouse, notes)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'''
        cursor.execute(insert_query, product_details)
        connection.commit()
        print("Product inserted successfully")
    except mysql.connector.Error as error:
        print(f"Failed to insert product: {error}")
    finally:
        if connection.is_connected():
            cursor.close()

def delete_product(connection, product_id):
    try:
        cursor = connection.cursor()
        delete_query = "DELETE FROM Tradeasy_quotation WHERE id = %s;"
        cursor.execute(delete_query, (product_id,))
        connection.commit()
        print("Product deleted successfully")
    except mysql.connector.Error as error:
        print(f"Failed to delete product: {error}")
    finally:
        if connection.is_connected():
            cursor.close()

def update_product(connection, product_details):
    try:
        cursor = connection.cursor()
        update_query = '''UPDATE Tradeasy_quotation
                          SET productName = %s, price = %s, notes = %s
                          WHERE id = %s;'''
        cursor.execute(update_query, product_details)
        connection.commit()
        print("Product updated successfully")
    except mysql.connector.Error as error:
        print(f"Failed to update product: {error}")
    finally:
        if connection.is_connected():
            cursor.close()

def query_data(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()  # Fetch all records from the last executed statement

        print("Total number of rows in table: ", cursor.rowcount)
        print("\nPrinting each row")

        for row in records:
            print("Product ID: ", row[0])
            print("Product Name: ", row[1])
            print("Category: ", row[3])
            print("Price: ", row[15])
            print("Warehouse: ", row[16])
            print("\n")

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            cursor.close()


def query_data_dataframe(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        columns = cursor.column_names
        
        df = pd.DataFrame(result, columns=columns)
        return df

    except Error as e:
        print("Error reading data from MySQL table", e)
        return None
    finally:
        if connection.is_connected():
            cursor.close()

