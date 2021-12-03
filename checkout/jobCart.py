# from boto3.dynamodb.conditions import Key
# from flask import request
# from checkout import app
# import boto3
# import logging
# from botocore.exceptions import ClientError
# import os
# from dotenv import load_dotenv
# import json
# from datetime import datetime
#
# ''' Loading Environment files '''
# load_dotenv()
#
# ''' Configuring AWS dynamo db '''
# dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
# ''' Configuring AWS Cognito '''
# cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
# table_name = os.getenv("DYNAMO_JOB_TABLE")
#
# sqs_client = boto3.client(os.getenv("AWS_SQS"), region_name=os.getenv("AWS_REGION"))
# queue_name = os.getenv("QUEUE_NAME")
# hash_queue_name = os.getenv("DYNAMO_HASH_TABLE")
#
# '''
# Input might be emailId of the user who is sending this email, email (replace with hash of email,product name,
# dateTime column) and product name, we will send a email to the product owner about this intrested person info
# along with the email id and email body of the sender.
# '''
#
#
# @app.route('/accommodation-cart', methods=['POST'])
# def addAccommodation():
#     # logging.log("addAccommodation() request is "+json.dumps(request.get_json()))
#     response = {}
#     try:
#         '''Connect to the Accommodation table'''
#         table = dynamoDbResource.Table(table_name)
#         hashTable = dynamoDbResource.Table(hash_queue_name)
#         receiverEmail = ""
#         receiverName = ""
#
#         responseHashTable = hashTable.query(
#             KeyConditionExpression=Key("hash").eq(request.json['hash']))
#         if responseHashTable['Count'] > 1:
#             for item in responseHashTable['Items']:
#                 if item['name'] == request.json['name']:
#                     receiverEmail = item['email']
#                     receiverName = item['name']
#                     return
#         else:
#             if responseHashTable['Items'] is not None:
#                 receiverEmail = responseHashTable['Items'][0]['email']
#                 receiverName = responseHashTable['Items'][0]['name']
#
#         dbResponse=table.query(
#                 KeyConditionExpression = Key("email").eq(receiverEmail) &
#         Key("name").eq(receiverName))
#
#         # logging.log("Table is connected")
#         queueMsg = {"sendEmail": request.json['email'],
#                 "toEmail": receiverEmail,
#                 "emailBody": request.json['emailBody'],
#                  "productName": request.json['name']
#                 }
#         # retrive the URL of an existing Amazon SQS queue
#         response = sqs_client.get_queue_url(QueueName=queue_name)
#         queue_url = response['QueueUrl']
#
#         print('\nmessage to send to the queue', queueMsg, '...\n')
#         response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(queueMsg))
#         # logging.log("New User added to the Dynamo Db")
#     except ClientError as e:
#         logging.error(e)
#     return response
