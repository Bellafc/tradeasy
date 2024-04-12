from flask import Flask, request, jsonify
from twilio. twiml.messaging_response import MessagingResponse
import os
from twilio.rest import Client
import mysql.connector
from mysql.connector import Error
import database as mydb
import pandas as pd 
import textEx
import database
import wanxiang
from flask import Flask, request, send_from_directory
import pdfQuoteGenerator
from datetime import datetime
import time
import glob
import warnings
import quotation

# Suppress all warnings
warnings.filterwarnings("ignore")

#connect_mysql
try:
    connection = mysql.connector.connect(
        host='quote.c9ac6sewqau0.ap-southeast-2.rds.amazonaws.com',
        database='quote',
        user='admin',
        password='admin123'
    )
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
except Error as e:
    print("Error while connecting to MySQL", e)


#connect EC2 instance
account_sid = 'AC79c2fe6511ac0c9a1c3881c384798e22'
auth_token = 'c9a5e13731974f3a5d548102fbd96629'
client = Client(account_sid, auth_token)
welcome_message = """
歡迎使用本系統，請根據下列指令操作以開始：

#Update：將最新的報價數據更新至資料庫。
#Gen Quote：此指令將生成最新的報價PDF檔案。
#Get PDF：此指令返回最新的PDF報價文件。
#Quote ID：根據產品編號返回相關的產品詳情。
#Exit：推出系統


請輸入您希望執行的操作指令：
"""
message = client.messages.create(
  from_='whatsapp:+14155238886',
  body=welcome_message,
  to='whatsapp:+85261520721'
)

print(message.sid)

app = Flask(__name__)

def _formatString(concatText:str,supplier:str,effectiveDate:str) -> tuple:
    
   #(productName, productTag, supplier, category, packing, origin, brand, effectiveDate, spec1, spec2, spec3, spec4, spec5, spec6, price, weightUnit, warehouse, notes)
    midpoint = len(concatText) // 2

    # Split the string into two halves
    first_half = concatText[:midpoint]
    second_half = concatText[midpoint:]       
    brand = textEx.getBrand(concatText)
    country = textEx.getCountry(first_half)
    product = textEx.getProduct(concatText)
    warehouse = textEx.getWarehoue(second_half)
    if warehouse:
        warehouse = warehouse[0]
    packing = textEx.getPacking(first_half)
    if packing == "":
        packing = "抄"
    price = textEx.getPriceWord(second_half)
    if price is None:
        return None
    weightUnit = textEx.getWeightUnit(second_half)
    category = textEx.getCategory(concatText)
    spec = textEx.getSpec(concatText)

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
 

    product_detail = (concatText,product, supplier, category, packing,country,brand, effectiveDate,spec1 , spec2 , spec3 , spec4 , spec5 , spec6,price,weightUnit,warehouse,"")

    return product_detail




def _insert_product(SQLconnection, productDetail:tuple ):
    database.insert_product(SQLconnection,productDetail)
    return None

def is_pdf_coming(request_values) -> bool:
    """
    Determine if the incoming WhatsApp message contains a PDF file.

    Args:
    request_values (Dict): The form data from the incoming request.

    Returns:
    bool: True if a PDF is detected, False otherwise.
    """
    num_media = int(request_values.get('NumMedia', 0))  # Number of media items in the message
    for i in range(num_media):
        media_content_type = request_values.get(f'MediaContentType{i}', '')
        if media_content_type == 'application/pdf':
            return True
    return False

user_states = {}
user_data = {}

@app.route('/static/pdfs/<filename>')
def serve_pdf(filename):
    # Make sure to validate the filename to avoid security issues
    return send_from_directory('static/pdfs', filename)

PDF_URL = ""

def _find_latest_pdf_directory(directory):
    # Construct the path pattern to match all PDF files in the directory
    path_pattern = os.path.join(directory, "*.pdf")
    
    # List all PDF files in the directory
    pdf_files = glob.glob(path_pattern)
    
    # Check if there are any PDF files found
    if not pdf_files:
        return None
    
    # Sort the files by modification time in descending order
    # The latest file will be the first one in the list
    latest_pdf = max(pdf_files, key=os.path.getmtime)
    print(latest_pdf)
    
    # Return the directory of the latest PDF file
    return "/"+latest_pdf

def send_quotation_review(sender):
    # Construct the message
    text = user_data[sender]['supplier'] + '\n'
    for product in user_data[sender]['product_detail']:
        product_values = [str(val) if val is not None else "" for val in [product[4], product[5], product[6], product[1], product[8], product[9], product[10], product[14], product[15], product[16]]]
        text += ' '.join(product_values) + '\n'

    # Update the state to await confirmation
    user_states[sender] = 'awaiting_word_quotation_confirmation'

    # Send the message
    msg = MessagingResponse().message()
    msg.body("Please review the product details. Reply 'Y' to confirm, or 'N' if you discover any issues.\n" + text)
    return str(msg)

def safe_str(value, default=""):
    """Convert a value to a string, replacing None with a default value."""
    if value is None:
        return default
    return str(value)

@app.route("/wa", methods=['POST'])
def receive_whatsapp_message():
    # Extracting the message SID, sender's number, and message body from the request
    message_sid = request.form.get('MessageSid', '')
    sender = request.form.get('From', '')
    message_body = request.form.get('Body', '')

    print(f"Message SID: {message_sid}, From: {sender}, Message: {message_body}")

    sender = request.form.get('From')
    incoming_msg = request.form.get('Body').strip()
    resp = MessagingResponse()
    msg = resp.message()
    recievedQuotation = False

    if incoming_msg.upper() == "#exit".upper():
        msg.body("退出系統...")
        if sender in user_states:
            del user_states[sender]
        if sender in user_data:
            del user_data[sender]

    if sender not in user_states:
        # New or reset user interaction
        if incoming_msg.upper() == "#update".upper():
            msg.body("請提供供應商")
            user_states[sender] = 'awaiting_supplier'
            user_data[sender] = {}
        elif incoming_msg.upper() == '#get PDF'.upper():
            pdf_path = _find_latest_pdf_directory("static/pdfs")
            resp.message("PDF報價單發送中...請稍候片刻...")
            ngrok_base_url = 'https://b820-54-153-171-62.ngrok-free.app'  # Update with your actual ngrok URL
            url = f'{ngrok_base_url}{pdf_path}'
            print(url) 
            resp.message(url)
            msg.media(url)    
        elif incoming_msg.upper() == '#quote id'.upper():
            msg.body("請提供 product id")
            user_states[sender] = 'awaiting_product_id'
            user_data[sender] = {}
        elif incoming_msg.upper() == "#gen quote".upper():
            resp.message("Generating Quotation PDF...")
            current_datetime = datetime.now()
            
            try:
                pdf_path = pdfQuoteGenerator.createQuotation(connection, current_datetime, days=3)
                msg.body("PDF報價單生成已完成,請輸入‘get quote’查閱報價...")

            except Exception as e:
                print(f"An error occurred: {e}")
      


        else:
            msg.body(welcome_message)
    

    elif user_states[sender] == 'awaiting_supplier':
        user_data[sender]['supplier'] = incoming_msg  # Store the supplier name
        msg.body("請問是 文字報價 還是 PDF報價？")
        user_states[sender] = 'awaiting_quotation_type'
    elif user_states[sender] == 'awaiting_product_id':
        text = "\n"
        rows = incoming_msg.strip().split('\n')
        for row in rows:
            if not row.strip():
                continue
            try:
                row_int = int(row.strip())  # Remove leading/trailing whitespace and convert to int
                product = quotation.getQuoteByID(connection,row_int)
                text += (safe_str(product['product_id'][0]) + " " +
                        safe_str(product['brand'][0]) + " " +
                        safe_str(product['productTag'][0]) + " " +
                        safe_str(product.get('price', "清")[0]) + " " +  # Corrected key 'price]'
                        safe_str(product['weightUnit'][0]) + " " +
                        safe_str(product['warehouse'][0]) + " " +
                        safe_str(product['supplier'][0]) + "\n")
            except ValueError:
                # If conversion fails, skip this row or handle it as needed
                print(f"Skipping non-integer row: {row}")
                continue  # Skip to the next iteration of the loop

        del user_states[sender]
        msg.body("閣下所需的 成本報價如下： " + text)

    elif user_states[sender] == 'awaiting_quotation_type':
        if incoming_msg in ["文字報價", "PDF報價","文字","PDF"]:
            user_data[sender]['quotation_type'] = incoming_msg
            # Here, you'd normally ask for the actual quotation text or PDF,
            # but for simplicity, let's assume it's the end of the process
            # and we're ready to update the database
            #update_database(user_data[sender])
            if incoming_msg == "文字報價" or incoming_msg == "文字":
                user_states[sender] = 'awaiting_word_quotation'
                msg.body("請根據以下格式提供數據: \nPacking|Origin|Brand|Product|Specifications|Price|Weight Unit|Warehouse .")
                
            else:
                msg.body("請提供PDF報價")
                user_states[sender] = 'awaiting_PDF_quotation'

        else:
            msg.body("Please specify '文字報價' or 'PDF報價'.")
    elif user_states[sender] == 'awaiting_word_quotation' and recievedQuotation == False:
        current_datetime = datetime.now()
        datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        rows = incoming_msg.strip().split('\n')
        products =[]
        for row in rows:
            if not row.strip():
                continue
            product_detail = _formatString(row,user_data[sender]['supplier'],datetime_str)
            if product_detail is not None:
                products.append(product_detail)
                print(product_detail)
                print('')
        if len(products) !=0:
            user_data[sender]['product_detail'] = products
            recievedQuotation = True

            text = user_data[sender]['supplier'] + '\n'
            for product in user_data[sender]['product_detail']:
                product_values = [str(val) if val is not None else "" for val in [product[4], product[5], product[6], product[1], product[8], product[9], product[10], product[14], product[15], product[16]]]
                text += ' '.join(product_values) + '\n'

            # Update the state to await confirmation
            user_states[sender] = 'awaiting_word_quotation_confirmation'

            # Send the message
            
            msg.body("*********\n請檢查數據是否準確，一經確認則無法修改\n 請輸入 'Y' 確認, 或 'N' 重新輸入\n*********\n\n" + text)


        else:
            msg.body("對不起,請重新輸入")


        

    elif user_states[sender] == 'awaiting_word_quotation_confirmation':
        if incoming_msg == 'Y' or incoming_msg == 'Yes':
            for product in user_data[sender]['product_detail']:
                _insert_product(connection,product)
            recievedQuotation = False
            del user_states[sender]
            msg.body("已更新報價")
        
        elif incoming_msg == 'N' or incoming_msg == 'No':
            user_states[sender] = 'awaiting_word_quotation'
            user_data[sender]['product_detail'] = []
            recievedQuotation = False
            msg.body("請重新輸入報價")
        else :
            msg.body("對不起,請重新輸入")

    elif user_states[sender] == 'awaiting_PDF_quotation':
        del user_states[sender]

    else:
        # Fallback or unknown state
        msg.body("對不起,我唔明白你的指令")
        # Optionally reset user state here
        if sender in user_states:
            del user_states[sender]
        if sender in user_data:
            del user_data[sender]

    return str(resp)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=False,port=5000)