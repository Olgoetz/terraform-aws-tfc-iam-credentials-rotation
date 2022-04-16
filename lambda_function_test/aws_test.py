import datetime
from unittest import TestCase, mock
import boto3
import os
from lambda_function.aws import AWS
from moto import mock_iam
from base import aws_credentials

def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

@mock_iam
@mock.patch.dict(os.environ, {'TFC_DEPLOYER_NAME': "tfc_deployer"}, clear=True)
class TestAWSFunctions(TestCase):

    def setUp(self):
        aws_credentials()
        self.iam = boto3.client('iam')
        self.user_name = os.environ['TFC_DEPLOYER_NAME']
        self.iam.create_user(UserName=self.user_name)

    def test_create_access_key(self):
        result = AWS().create_access_key(userName=self.user_name)
        self.assertEqual(result['Status'], "Active")

    def test_list_access_keys(self):
        self.iam.create_access_key(UserName=self.user_name)
        result = AWS().list_access_keys(userName=self.user_name)
        self.assertEqual(len(result), 1)

    def test_delete_access_key(self):
        # Test if no age is provided
        result_1 = self.iam.create_access_key(UserName=self.user_name)['AccessKey']
        result_2 = AWS().delete_access_key(accessKeyId=result_1['AccessKeyId'], createDate=result_1['CreateDate'], userName=self.user_name)
        self.assertIs(result_2, True)

        # Test if key is older than 30 days, delete it
        result_3 = self.iam.create_access_key(UserName=self.user_name)['AccessKey']
        result_4 = AWS().delete_access_key(accessKeyId=result_3['AccessKeyId'], createDate=datetime.datetime(2021,4,15,11,54,10), age=30, userName=self.user_name)
        self.assertIs(result_4, True)







