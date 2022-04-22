from datetime import datetime
from terrasnek.api import TFC
from .common import Logger

timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def change_description(variable_name):
    """
    Change the description depending on the CSP
    :param variable_name: variable name for tfc
    :return str: target
    """
    if 'AWS' in variable_name:
        target = "account"
    elif 'AZURE' in variable_name:
        target = "subscription"
    else:
        target = None

    return target


class Terraform:

    def __init__(self, tfc_token, tfc_url, tfc_org, tfc_workspace_id, ssl_verify):
        self._api = TFC(tfc_token, url=tfc_url, verify=ssl_verify)
        self._api.set_org(tfc_org)
        self._tfc_workspace_id = tfc_workspace_id

    def create_workspace_variable(self, variable_name, val, csp_id):
        """
        Creates a workspace variable in tfc
        :param variable_name: name of the variable
        :param val: value of the variable
        :param csp_id: id of the csp
        :return bool: True or False
        """
        workspace_id = self._tfc_workspace_id
        Logger().getlogger.info(f"Create variable {variable_name} for workspace {workspace_id}")

        create_workspace_var_payload = {
          "data": {
            "type": "vars",
            "attributes": {
              "key": variable_name,
              "value": val,
              "description": f"Automated credential rotation for {change_description(variable_name)} {csp_id} (updated on {timestamp})",
              "category": "env",
              "hcl": False,
              "sensitive": True
            },
            "relationships": {
              "workspace": {
                "data": {
                  "id": workspace_id,
                  "type": "workspaces"
                }
              }
            }
          }
        }

        try:
            self._api.workspace_vars.create(workspace_id, create_workspace_var_payload)
            Logger().getlogger.info(f"{variable_name} created")
            return True
        except Exception as e:
            Logger().getlogger.error(e)
            return False

    def delete_workspace_variable(self, variable_name, variable_id):
        """
        Deletes a workspace variable
        :param variable_name: name of the workspace variable
        :param variable_id: id of the workspace variable
        :return bool: True
        """
        workspace_id = self._tfc_workspace_id
        Logger().getlogger.info(f"Delete ${variable_name} for workspace {workspace_id}")

        try:
            self._api.workspace_vars.destroy(workspace_id=workspace_id, variable_id=variable_id)
            Logger().getlogger.info(f"{variable_name} deleted!")
            return True
        except Exception as e:
            #Logger().getlogger.error(e)
            pass
            #return False

    def get_workspace_variable(self, variable_name):
        """
        Get a workspace variable
        :param variable_name: name of the workspace variable
        :return dic: name and id of the workspace variable
        """

        try:
            variables = self._api.workspace_vars.list(self._tfc_workspace_id)['data']
            for e in variables:
                Logger().getlogger.debug(e['attributes']['key'])
                if e['attributes']['key'] == variable_name:
                    return {"Name": e['attributes']['key'], "Id": e['id']}

        except Exception as e:
            Logger().getlogger.error(e)
            return False

    def update_workspace_variable(self, variable_name, variable_id, new_val, csp_id):
        """
        Updates a workspace variable in tfc
        :param variable_name: name of the workspace variable
        :param variable_id: id of the workspace variable
        :param new_val: new val for the workspace variable
        :param csp_id: id of the csp
        :return bool: True
        """
        workspace_id = self._tfc_workspace_id
        update_var_payload = {
          "data": {
            "id": variable_id,
            "attributes": {
                "value": new_val,
                "description": f"Automated credential rotation for {change_description(variable_name)} {csp_id} (updated on {timestamp})"
            },
            "type": "vars"
          }
        }
        try:
            self._api.workspace_vars.update(workspace_id, variable_id, update_var_payload)
            Logger().getlogger.info(f"Variable {variable_name} updated")
        except Exception as e:
            Logger().getlogger.error(e)
        return True



