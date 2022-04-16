import boto3
import botocore.exceptions
from .common import Logger
from datetime import datetime, timedelta


class AWS:

    def __init__(self):
        self._iam_client = boto3.client('iam')
        self._sts_client = boto3.client('sts')

    def get_account_id(self):
        return self._sts_client.get_caller_identity()['Account']

    def create_user(self, userName):
        """
        Creates a user for tfe deployments.

        :return str: message
        """

        all_users = self._iam_client.list_users()["Users"]
        all_user_names = [el['UserName'] for el in all_users]

        if userName not in all_user_names:
            try:
                self._iam_client.create_user(userName)
            except botocore.exceptions.ClientError as e:
                Logger().getlogger.error(e)
        else:
            Logger().getlogger.info(f"{userName} already exists. Nothing to do.")
        return {"Message": "User created"}

    def create_access_key(self, userName):
        """
        Create a AWS ACCESS KEY ID and AWS SECRET ACCESS KEY

        :return dict: dict holding metadata
        """

        try:
            response = self._iam_client.create_access_key(UserName=userName)
            Logger().getlogger.info("New credentials generated!")
        except botocore.exceptions.ClientError as e:
            Logger().getlogger.error(e)
            return False

        return {
            "UserName": response['AccessKey']['UserName'],
            "AWS_ACCESS_KEY_ID": response['AccessKey']['AccessKeyId'],
            "AWS_SECRET_ACCESS_KEY": response['AccessKey']['SecretAccessKey'],
            "Status": response['AccessKey']['Status']
            }

    def list_access_keys(self, userName):
        """Returns all available access keys.

        :return list: access keys
        """

        try:
            access_keys = self._iam_client.list_access_keys(UserName=userName)['AccessKeyMetadata']

        except botocore.exceptions.ClientError as e:

            Logger().getlogger.error(e)
            return False

        return access_keys

    def delete_access_key(self, accessKeyId, createDate, userName, age=None):
        """Deletes an access key based on the creation date.

        :return bool: True if deletion was successful
        """

        if not age:
            try:
                self._iam_client.delete_access_key(UserName=userName, AccessKeyId=accessKeyId)
                Logger().getlogger.info(f"{accessKeyId} deleted!")
                return True
            except botocore.exceptions.ClientError as e:
                Logger().getlogger.error(e)

        # Check if the key is outdated
        tz = createDate.tzinfo
        past = datetime.now(tz) - timedelta(days=age)
        if past > createDate:
            Logger().getlogger.info(f'Deleting {accessKeyId} as it is older than {age} days')
            try:
                self._iam_client.delete_access_key(UserName=userName,AccessKeyId=accessKeyId)
                Logger().getlogger.info(f"{accessKeyId} deleted!")
                return True
            except botocore.exceptions.ClientError as e:
                Logger().getlogger.error(e)

        return False
