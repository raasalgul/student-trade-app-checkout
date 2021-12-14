import logging

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import os
import json
from dotenv import load_dotenv
import requests

''' Loading Environment files '''
load_dotenv()

sqs_client = boto3.client(os.getenv("AWS_SQS"), region_name=os.getenv("AWS_REGION"))


def queueUtilities(table_name,hash_table_name,queue_name,request,catagory):
    dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
    try:
        response = {}
        '''Connect to the Accommodation table'''
        table = dynamoDbResource.Table(table_name)
        hashTable = dynamoDbResource.Table(hash_table_name)
        receiverEmail = ""
        receiverName = ""

        responseHashTable = hashTable.query(
            KeyConditionExpression=Key("hash").eq(request.json['hash']))
        if responseHashTable['Count'] > 1:
            for item in responseHashTable['Items']:
                if item['name'] == request.json['name']:
                    receiverEmail = item['email']
                    receiverName = item['name']
                    return
        else:
            if responseHashTable['Items'] is not None:
                receiverEmail = responseHashTable['Items'][0]['email']
                receiverName = responseHashTable['Items'][0]['name']

        dbResponse = table.query(
            KeyConditionExpression=Key("email").eq(receiverEmail) &
                                   Key("name").eq(receiverName))

        # logging.log("Table is connected")
        queueMsg = {"sendEmail": request.json['email'],
                    "to": receiverEmail,
                    "message": request.json['emailBody'],
                    "productName": request.json['name'],
                    "category": catagory
                    }

        msg = "Hi, " \
              "This email is from student trade app's \"{0}\" category." \
              "For the product name \"{1}\" has received this following email " \
              "\"{2}\". If you want to proceed with it please contact {3}".format(catagory,queueMsg['category'],
                                                                                  queueMsg['message'],queueMsg['sendEmail'])
        # retrive the URL of an existing Amazon SQS queue
        # response = sqs_client.get_queue_url(QueueName=queue_name)
        # queue_url = response['QueueUrl']
        #
        # print('\nmessage to send to the queue', queueMsg, '...\n')
        # response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(queueMsg))
        # # logging.log("New User added to the Dynamo Db")
        response = requests.post('https://uos8mod855.execute-api.us-east-1.amazonaws.com/prod/notificationLambda',
                                 json={"to":receiverEmail,"subject":catagory,"message":msg})
        logging.info("api gateway response {}".format(response))
    except ClientError as e:
        logging.error(e)
    return response