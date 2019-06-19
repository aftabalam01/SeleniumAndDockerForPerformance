import boto3
import json
import os

from logger import Logger
from config import CONFIG
from botocore.exceptions import ClientError

Logger = Logger()

class AwsAPI(object):
    """
    Small wrapper for connecting to the aws api
    """
    def __init__(self, inputlogger=Logger.getLogger(__name__, level=CONFIG.get('logging').get('level')),
                 environment=os.environ.get('ENV',CONFIG.get('default_env'))):
        """
        init sets up logger and credentials for api
        :param inputlogger: custom logger
        """
        self.logger = inputlogger

        credentials = CONFIG.get('aws').get(environment)
        self.aws_region = credentials.get("region")
        self.aws_buckets = credentials.get('buckets')
        self.client = None

    def get_aws_client(self, resource_name):
        """
        Connect to a specific resource within AWS
        added aws_region in client so that default can be overridden from config
        :param resource_name: example resources: s3, ec2, sqs
        :return:
        """
        if not self.client:
            self.logger.info("Connecting to {} in AWS ".format(resource_name))
            try:
                self.client = boto3.client(resource_name,
                                           region_name=self.aws_region)
                self.logger.info("Connection successful!")
            except ClientError as error:
                self.logger.error(error)
        return self.client


    def send_sqs_message(self,sqs_queue_url,delay=10,message_json=None,MessageDeduplicationId=None):
        """
        queue_url :  aws sqs queue url where message needs to be sent
        delay : delay in message delivery in seconds
        message_json : json message
        """
        # creating sqs client
        client = self.get_aws_client(resource_name='sqs')
        try:
            # check if queue url and mesage_json is not None
            if sqs_queue_url and message_json:
                if 'fifo' in sqs_queue_url:
                    response = client.send_message(
                        QueueUrl=sqs_queue_url,
                        MessageGroupId='SQSMsgGroupID1',
                        MessageDeduplicationId=MessageDeduplicationId,
                        MessageBody=json.dumps(message_json)

                    )
                else:
                    response = client.send_message(
                        QueueUrl=sqs_queue_url,
                        DelaySeconds=delay,
                        MessageBody=json.dumps(message_json)

                    )

                #log response message id
                self.logger.info(response['MessageId']+" is sent")
            else :
                self.logger.error("No message is sent")  
        except ClientError as error:
            self.logger.error(error)

    def receive_sqs_message(self,sqs_queue_url,nummsg=1,visibilitytimeout=3600,waittime=10):
        """
        This method will return a list of Sqs messages and its receipthandle

        :param sqs_queue_url:
        :param nummsg:
        :return:
        """
        client = self.get_aws_client(resource_name='sqs')
        sqs_messages = []
        try:
            if sqs_queue_url:
                response = client.receive_message(
                    QueueUrl=sqs_queue_url,
                    AttributeNames=[
                        'SentTimestamp'
                    ],
                    MaxNumberOfMessages=nummsg,
                    MessageAttributeNames=[
                        'All'
                    ],
                    VisibilityTimeout=visibilitytimeout,
                    WaitTimeSeconds=waittime
                )

                if response:
                    try:
                        sqs_messages = response['Messages']
                    except:
                        sqs_messages = []  # retuning a blank message

        except ClientError as error:
            self.logger.error(error)
        return sqs_messages

    def delete_sqs_message(self,sqs_queue_url,receipt_handle):
        """
        This method deletes a message from SQS
        both parameters are required
        :param sqs_queue_url:
        :param receipt_handle:
        :return:
        """
        client = self.get_aws_client(resource_name='sqs')
        try:
            if sqs_queue_url and receipt_handle:
                response=client.delete_message(
                    QueueUrl=sqs_queue_url,
                    ReceiptHandle=receipt_handle
                )
                if response['ResponseMetadata']['HTTPStatusCode']==200:
                    deleted=True
                else:
                    deleted = False
        except ClientError as error:
            self.logger.error(error)
            deleted=False
        return deleted