# import boto3
# #from lambda_function.handler import handler
# import os
# import unittest
# from moto import mock_iam, mock_sts
# import mock
# from base import aws_credentials
# @mock_sts
# @mock_iam
# @mock.patch.dict(os.environ, {'FORCE_CREATE_NEW_KEY': True}, clear=True)
# @mock.patch.dict(os.environ, {'TFC_DEPLOYER_NAME': "tfc_deployer"}, clear=True)
# @mock.patch.dict(os.environ, {'TFC_ORG': "tfc_deployer"}, clear=True)
# @mock.patch.dict(os.environ, {'TFC_WORKSPACE_ID': "i12345"}, clear=True)
# @mock.patch.dict(os.environ, {'TFC_TOKEN': "mytoken"}, clear=True)
# class TestHandler(unittest.TestCase):
#     def setUp(self):
#         aws_credentials()
#         self.iam = boto3.client('iam')
#
#     def test_force_new_key(self):
#         print(os.environ)
#         #result = handler({}, {})
#      #   print(result)
#
#

