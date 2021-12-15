import logging

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import hashlib

''' Loading Environment files '''
load_dotenv()

# sqs_client = boto3.client(os.getenv("AWS_SQS"), region_name=os.getenv("AWS_REGION"))


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

        feedMsg = {
            "transaction":catagory,
            "to":receiverName,
            "time":datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                }

        feedData = {}

        msg = "Hi\n, " \
              "This email is from student trade app's \"{0}\" category.\n" \
              "For the product name \"{1}\" has received this following email " \
              "\"{2}\". If you want to proceed with it please contact {3} \n Thank You".format(catagory,queueMsg['productName'],
              receiverName,queueMsg['sendEmail'])

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
        table = dynamoDbResource.Table(os.getenv("DYNAMO_FEED_TABLE"))
        strToHash = feedMsg.get("to") + feedMsg.get("time")
        hash = hashlib.sha224(strToHash.encode())
        feedData['hash'] = hash.hexdigest()
        feedData['addedDate'] = feedMsg.get("time")
        feedData['data'] = feedMsg
        feedData['isTrue'] = "true"
        response = table.put_item(Item=feedData)
        logging.info("Feed table response {}".format(response))
    except ClientError as e:
        logging.error(e)
        return {"status":e}
    return {"status":"Sucess"}