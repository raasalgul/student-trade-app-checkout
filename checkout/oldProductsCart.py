from boto3.dynamodb.conditions import Key

from checkout import application
import boto3
import os
from dotenv import load_dotenv
import json
from flask import request

''' Loading Environment files '''
load_dotenv()

''' Configuring AWS Cognito '''
cognitoClient = boto3.client(os.getenv("AWS_COGNITO"), region_name=os.getenv("AWS_REGION"))
table_name = os.getenv("DYNAMO_OLDPRODUCTS_TABLE")

sqs_client = boto3.client(os.getenv("AWS_SQS"), region_name=os.getenv("AWS_REGION"))

queue_name = os.getenv("SMS_QUEUE_NAME")
hash_table_name = os.getenv("DYNAMO_HASH_TABLE")


@application.route('/old-product', methods=['POST'])
def oldProduct():
    try:
        dynamoDbResource = boto3.resource(os.getenv("AWS_DYNAMO"), region_name=os.getenv("AWS_REGION"))
        table = dynamoDbResource.Table(table_name)
        hashTable = dynamoDbResource.Table(hash_table_name)
        receiverEmail = ""
        receiverName = ""
        # logging.log("addAccommodation() request is "+json.dumps(request.get_json()))

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
        res = {
            "productHash": request.json['hash'],
            "requesterEmail": request.json['email'],
            "productName": receiverName,
            "cost":dbResponse['Items'][0]['price']

        }
        response = sqs_client.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        response = sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(res))
    except Exception as e:
        return {"status":e}
    return {"status":"success"}
