import json
import os
from .common import Logger
from .tfc import Terraform
from .aws import AWS
import sys

# Env variables
CUSTOM_CA_BUNDLE_PATH = os.getenv('CUSTOM_CA_BUNDLE', None)
TFC_TOKEN = os.getenv("TFC_TOKEN", None)
TFC_ORG = os.getenv("TFC_ORG", None)
TFC_URL = os.getenv('TFC_URL', "https://app.terraform.io")
TFC_WORKSPACE_ID = os.getenv('TFC_WORKSPACE_ID', None)
TFC_DEPLOYER_NAME = os.getenv('TFC_DEPLOYER_NAME', None)
TFC_VARS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
SSL_VERIFY = bool(os.getenv('SSL_VERIFY', True))
FORCE_CREATE_NEW_KEY = bool(os.getenv('FORCE_CREATE_NEW_KEY', False))
RENEWAL_TIME = int(os.getenv('RENEWAL_TIME', 30))


if CUSTOM_CA_BUNDLE_PATH is not None:
    os.environ['AWS_CA_BUNDLE'] = CUSTOM_CA_BUNDLE_PATH

# Check if necessary env variables have bee set
envs_to_check = [TFC_ORG, TFC_WORKSPACE_ID, TFC_TOKEN]

if None in envs_to_check or "" in envs_to_check:
    Logger().getlogger.error("You must provide the following env variables: TFC_ORG, TFC_WORKSPACE_ID, TFC_TOKEN")
   # sys.exit(1)

TFC = Terraform(tfc_token=TFC_TOKEN, tfc_url=TFC_URL, tfc_org=TFC_ORG, tfc_workspace_id=TFC_WORKSPACE_ID, ssl_verify=SSL_VERIFY)
AWS = AWS()


def handler(event,context):
    Logger().getlogger.info(json.dumps(event))
    account_id = AWS.get_account_id()

    # Deploy a user for tfc deployments
   # AWS.create_user(userName=TFC_DEPLOYER_NAME)

    # Get all access keys
    all_access_keys = AWS.list_access_keys(userName=TFC_DEPLOYER_NAME)

    # Make sure that no AWS_SESSION_TOKEN exists
    try:
        variable_id = TFC.get_workspace_variable(variable_name='AWS_SESSION_TOKEN')['Id']
        TFC.delete_workspace_variable(variable_name='AWS_SESSION_TOKEN', variable_id=variable_id)
    except TypeError:
        pass

    # I. Case: Revoke all keys and create a new one ####
    if FORCE_CREATE_NEW_KEY:

        Logger().getlogger.info("Deleting all keys!")

        for k in all_access_keys:
            AWS.delete_access_key(accessKeyId=k['AccessKeyId'], createDate=k['CreateDate'], userName=TFC_DEPLOYER_NAME)

        new_key = AWS.create_access_key(userName=TFC_DEPLOYER_NAME)

        # Create the variables in the tfc workspace
        for var in TFC_VARS:
            result = TFC.create_workspace_variable(variable_name=var, val=new_key[var], csp_id=account_id)

            # Update variable
            if result is False:

                # List variables in order to get the id of the specified one
                result = TFC.get_workspace_variable(variable_name=var)
                TFC.update_workspace_variable(variable_name=result['Name'], variable_id=result['Id'], new_val=new_key[var], csp_id=account_id)

        return {
            "StatusCode": 200,
            "Body": json.dumps({"Message": "All credentials have been revoked and fresh "
                                           "AWS credentials have been created!"})
        }

    # II. Case: Create new access key if no access keys are available yet ####
    if len(all_access_keys) == 0:

        Logger().getlogger.info("No access keys found. Creating a new one!")

        # Create new credentials
        new_key = AWS.create_access_key(userName=TFC_DEPLOYER_NAME)

        # Create the variables in the tfc workspace
        for var in TFC_VARS:
            result = TFC.create_workspace_variable(variable_name=var, val=new_key[var], csp_id=account_id)

            # Update variable
            if result is False:
                # List variables in order to get the id of the specified one
                result = TFC.get_workspace_variable(variable_name=var)
                TFC.update_workspace_variable(variable_name=result['Name'], variable_id=result['Id'], new_val=new_key[var], csp_id=account_id)

        return {
            "StatusCode": 200,
            "Body": json.dumps({"Message": "Initial setup done: New AWS credentials are set!"})
        }

    # III. Case: Check if an access is outdated ####
    else:
        result = False
        for k in all_access_keys:
            Logger().getlogger.info(f"Deleting {k['AccessKeyId']} if older than {RENEWAL_TIME}!")
            result = AWS.delete_access_key(accessKeyId=k['AccessKeyId'], createDate=k['CreateDate'],userName=TFC_DEPLOYER_NAME, age=RENEWAL_TIME)

        # Check if there were any old credentials:
        if result is True:
            # Create new credentials
            new_key = AWS.create_access_key(userName=TFC_DEPLOYER_NAME)

            for var in TFC_VARS:
                result = TFC.create_workspace_variable(variable_name=var, val=new_key[var], csp_id=account_id)
                if result is False:
                    # List variables in order to get the id of the specified one
                    result = TFC.get_workspace_variable(variable_name=var)

                    # Update variable
                    TFC.update_workspace_variable(variable_name=result['Name'], variable_id=result['Id'], new_val=new_key[var], csp_id=account_id)
            return {
                "StatusCode": 200,
                "Body": json.dumps({"Message": "New AWS credentials set!"})
            }

        else:
            return {
                "StatusCode": 200,
                "Body": json.dumps({"Message": "No need to rotate credentials!"})
            }



