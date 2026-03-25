# xolo/client/client.py
import requests as R
import json as J
import sys
from typing import Dict,List
import xolo.client.models as M
from option import Result,Ok,Err,Some
from xolo.policies.parser import build_parser
from xolo.policies.parser.models import Command
import xolo.client.errors as E
import pyparsing as pp


class XoloClient(object):
    def __init__(self,hostname:str,  port:int=-1,version:int=4,secret:str=""):
        self.hostname = hostname
        self.port     = port
        self.version  = version
        self.secret   = secret
        self.parser  = build_parser()
        # self.executor = XoloExecutor(client=self,secret=secret)

    def execute_script(self,script_text:str)->List:
        """Parses a full script and returns a list of command objects."""
        try:
            command_list:List[Command] = self.parser.parseString(script_text, parseAll=True)
        except pp.ParseException as e:
            print(f"--- PARSING FAILED ---", file=sys.stderr)
            print(f"Error on line {e.lineno}, col {e.col}:", file=sys.stderr)
            print(e.line, file=sys.stderr)
            print(" " * (e.col - 1) + "^", file=sys.stderr)
            print(e, file=sys.stderr)
            raise Exception("Parsing Failed")
            # return []
        results = []
        for cmd in command_list:
            try:
                result = cmd.execute(self)
                results.append(result)
            except Exception as e:
                print(f"[FATAL] Unhandled error executing command {cmd}: {e}", file=sys.stderr)
        return results
        # commands = self.executor.parse_script(script_text)
        # results  = self.executor.execute_commands(commands)
        # return results

    def base_url(self):
        if self.port == -1:
            return "https://{}".format(self.hostname)
        else:
            return "http://{}:{}".format(self.hostname,self.port)

    def __process_exception(self,e:R.HTTPError)->E.XError:
        status_code = e.response.status_code
        error_detail = e.response.json().get("detail","")
        if isinstance(error_detail,Dict):
            x = E.ErrorDetail.model_validate(error_detail)
            return E.XError.from_code(
                code       = x.code,
                raw_detail = x.raw_error,
                headers    = e.response.headers,
                metadata   = x.metadata
            )
        return E.XError.from_code(code=status_code,raw_detail=str(error_detail),headers=e.response.headers,metadata={})
    
    def create_user(self,
                    username:str,
                    first_name:str,
                    last_name:str,
                    email:str,
                    password:str,
                    profile_photo:str="",
    )->Result[M.CreatedUserResponseDTO,E.XError]:
        try:
            url  = "{}/api/v{}/users".format(self.base_url(),self.version)
            data = {
                "username":username,
                "first_name":first_name,
                "last_name":last_name,
                "email":email,
                "password":password,
                "profile_photo":profile_photo,
            }
            
            response = R.post(url=url,json=data)
            response.raise_for_status()
            data = M.CreatedUserResponseDTO.model_validate(response.json())

            return Ok(data)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def enable_user(self,username:str,token:str,temporal_secret:str)->Result[bool,E.XError]:
        try:
            url  = f"{self.base_url()}/api/v{self.version}/users/{username}/enable"

            data = {
                "username":username,
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            response = R.post(url=url,json=data,headers=headers)
            response.raise_for_status()
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    def disable_user(self,username:str,token:str,temporal_secret:str)->Result[bool,E.XError]:
        try:
            url  = f"{self.base_url()}/api/v{self.version}/users/{username}/disable"

            data ={
                "username":username,
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            response = R.post(url=url,json=data,headers=headers)
            response.raise_for_status()
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
        
        
    def verify_token(self,access_token:str,username:str,secret:str="")->Result[bool,E.XError]:
        try:
            url  = "{}/api/v{}/users/verify".format(self.base_url(),self.version)
            data = {
                "access_token":access_token,
                "username":username,
                "secret":secret
            }
            response = R.post(url=url,json=data)
            response.raise_for_status()
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))


    def auth(self,
             username:str,
             password:str,
             scope:str,
             expiration:str="1h",
             renew_token:bool=False
    )->Result[M.AuthenticatedDTO,E.XError]:
        try:
            url = "{}/api/v{}/users/auth".format(self.base_url(),self.version)
            data = {
                "username":username,
                "password":password,
                "scope":scope,
                "expiration":expiration,
                "renew_token":renew_token
            }
            response = R.post(url=url, json=data)
            response.raise_for_status()
            data_json = response.json()
            return Ok(
                M.AuthenticatedDTO.model_validate(data_json)
            )
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    def create_license(
        self,
        username: str,
        scope: str,
        secret: str,
        expires_in: str = "1h",
        force:bool = True,
    )->Result[M.AssignLicenseResponseDTO, E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/licenses"
            data = {
                "username":username,
                "scope":scope,
                "expires_in":expires_in,
                "force":force
            }
            response = R.post(url=url, json = data, headers={"Secret": secret})
            response.raise_for_status()
            json_data = response.json()
            return Ok(M.AssignLicenseResponseDTO(
                **json_data
            ))
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    def create_scope(self,scope:str,secret:str="")->Result[bool, E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/scopes"
            data ={
                "name":scope
            }
            response = R.post(url =url, json=data, headers={"Secret": secret})
            response.raise_for_status()
            json_data = response.json()
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    def assign_scope(self,
        username:str, 
        scope:str,
        secret:str
    )->Result[M.AssignedScopeResponseDTO, E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/scopes/assign"
            data = {
                "username":username,
                "name":scope
            }
            response = R.post(url =url, json=data, headers={"Secret": secret})
            response.raise_for_status()
            json_data = response.json()
            return Ok(
                M.AssignedScopeResponseDTO(**json_data)
            )
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    
    def get_current_user(self,token:str,temporal_secret:str)->Result[M.UserDTO,E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/users"
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            response = R.get(url=url, headers=headers)
            response.raise_for_status()
            data_json = response.json()
            return Ok(
                M.UserDTO.model_validate(data_json)
            )
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    # ACL
    
    # ==========================================
    # NEW ACL METHODS (Groups & Permissions)
    # ==========================================
    def get_users_resources(
        self,
        token: str,
        temporal_secret: str,
        owned_page: int = 1,
        owned_page_size: int = 10,
        shared_page: int = 1,
        shared_page_size: int = 10,
    ) -> Result[M.UsersResourcesDTO, E.XError]:
        """
        Retrieves the resources information for the authenticated user.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/acl/resources?owned_page={owned_page}&owned_page_size={owned_page_size}&shared_page={shared_page}&shared_page_size={shared_page_size}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.get(url=url, headers=headers)
            response.raise_for_status()
            
            return Ok(M.UsersResourcesDTO(**response.json()))
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    def create_group(self, name: str, description: str, token: str,temporal_secret: str) -> Result[str, E.XError]:
        """
        Creates a new Security Group.
        Returns: The new group_id.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/groups"
            data = {
                "name": name,
                "description": description
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(response.json().get("group_id"))
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def delete_group(self, group_id: str, token: str, temporal_secret: str) -> Result[bool, E.XError]:
        """
        Deletes a Security Group.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/groups/{group_id}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.delete(url=url, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def add_members_to_group(self, group_id: str, members: List[str], token: str, temporal_secret: str) -> Result[bool, E.XError]:
        """
        Adds a list of user IDs to a group.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/groups/{group_id}/members"
            data = {
                "members": members
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def remove_members_from_group(self, group_id: str, members: List[str], token: str, temporal_secret: str) -> Result[bool, E.XError]:
        """
        Removes a list of user IDs from a group.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/groups/{group_id}/members"
            data = {
                "members": members
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            # Note: We send a body with DELETE
            response = R.delete(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def grant_permission(self, 
                         resource_id: str, 
                         principal_id: str, 
                         permissions: List[str], 
                         token: str,
                         temporal_secret: str,
                         principal_type: str = "USER",
    ) -> Result[bool, E.XError]:
        """
        Grants permissions to a User or Group.
        principal_type: "USER" or "GROUP"
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/grant"
            data = {
                "resource_id": resource_id,
                "principal_id": principal_id,
                "principal_type": principal_type,
                "permissions": permissions
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def revoke_permission(self, 
                          resource_id: str, 
                          principal_id: str, 
                          permissions: List[str], 
                          token: str,
                          temporal_secret: str,
    ) -> Result[bool, E.XError]:
        """
        Revokes specific permissions from a User or Group.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/revoke"
            # Note: The controller expects 'GrantOrRevokePermissionDTO' structure
            data = {
                "resource_id": resource_id,
                "principal_id": principal_id,
                "permissions": permissions,
                "principal_type": "USER" # Field required by DTO but ignored by revoke logic often
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            # Note: We send a body with DELETE
            response = R.delete(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def claim_resource(self, resource_id: str, token: str, temporal_secret: str) -> Result[bool, E.XError]:
        """
        Claims ownership of a new resource (Bucket/Folder).
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/claim"
            data = {
                "resource_id": resource_id
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(True)
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))

    def check_permission_auth(self, resource_id: str, permissions: List[str], token: str, temporal_secret: str) -> Result[bool, E.XError]:
        """
        Authenticated check. 
        Verifies if the token owner has the requested permissions.
        """
        try:
            url = f"{self.base_url()}/api/v{self.version}/users/check"
            data = {
                "resource_id": resource_id,
                "permissions": permissions,
                "role": "" # Unused by controller when 'me' is present, but DTO might require it
            }
            headers = {
                "Authorization": f"Bearer {token}",
                "Temporal-Secret-Key": temporal_secret
            }
            
            response = R.post(url=url, json=data, headers=headers)
            response.raise_for_status()
            
            return Ok(response.json().get("has_permission", False))
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
    
    def delete_license(self,username:str, scope:str,force:bool = True,secret:str="")->Result[M.DeletedLicenseResponseDTO, E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/licenses"
            data = {
                "username":username,
                "scope":scope,
                "force":force
            }
            response = R.delete(url=url, json=data, headers={"Secret": secret})
            response.raise_for_status()
            json_data = response.json()
            return Ok(M.DeletedLicenseResponseDTO(
                **json_data
            )) 
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
     
    def self_delete_license(self,username:str, scope:str,token:str,secret:str,force:bool = True)->Result[M.DeletedLicenseResponseDTO, E.XError]:
        try:
            url = f"{self.base_url()}/api/v{self.version}/licenses/self"
            data = {
                "token":token,
                "tmp_secret_key":secret,
                "username":username,
                "scope":scope,
                "force":force
            }
            response = R.delete(url=url, json=data) 
            response.raise_for_status()
            json_data = response.json()
            return Ok(M.DeletedLicenseResponseDTO(
                **json_data
            )) 
        except R.exceptions.HTTPError as http_err:
            return Err(self.__process_exception(http_err))
        except Exception as e:
            return Err(E.XError.from_exception(e))
