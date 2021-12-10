from checkout import app
import boto3
import os
from dotenv import load_dotenv
from flask import request

from checkout.utilities import queueUtilities

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_ACCOMMODATION_TABLE")

queue_name = os.getenv("QUEUE_NAME")
hash_table_name = os.getenv("DYNAMO_HASH_TABLE")

'''
Input might be emailId of the user who is sending this email, email (replace with hash of email,product name,
dateTime column) and product name, we will send a email to the product owner about this intrested person info 
along with the email id and email body of the sender.
'''


@app.route('/accommodation-cart', methods=['POST'])
def addAccommodation():
    # logging.log("addAccommodation() request is "+json.dumps(request.get_json()))
    response=queueUtilities(table_name,hash_table_name,queue_name,request,"Accommodation")

    return response
