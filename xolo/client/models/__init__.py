from commonx.dto.xolo import *
# # xolo/client/interfaces/auth.py
# from typing import Dict
# # from dataclasses import dataclass
# from pydantic import BaseModel,Field
# from typing import List, Set,TypeVar,Generic,Optional

# class AuthenticatedDTO(BaseModel):
#     username:str
#     first_name:str
#     last_name:str
#     email:str
#     profile_photo:str 
#     access_token:str 
#     metadata:Dict[str,str]
#     temporal_secret:str 
#     user_id: Optional[str] = Field(default=None)
#     # role:str
# class AssignLicenseResponseDTO(BaseModel):
#     expires_at: str
#     ok:bool
# class DeletedLicenseResponseDTO(BaseModel):
#     ok:bool
# class SelfDeletedLicenseResponseDTO(BaseModel):
#     ok:bool

# class AssignedScopeResponseDTO(BaseModel):
#     name:str
#     username:str
#     ok:bool

# class GroupDetailDTO(BaseModel):
#     id:str
#     name:str
#     my_role:str

# class ResourceDetailDTO(BaseModel):
#     resource_id:str
#     access_source:str
#     permissions:Set[str]
#     # Dict[str,Set[str]]  # principal_id -> set of permissions

# T = TypeVar("T")
# class PaginatedResponseDTO(BaseModel, Generic[T]):
#     items: List[T]
#     total_count: int
#     page: int
#     page_size: int
#     total_pages: int

# class UserDashboardViewDTO(BaseModel):
#     user_id: str
#     groups: List[GroupDetailDTO]
#     owned_resources: PaginatedResponseDTO[ResourceDetailDTO] # Updated type
#     shared_resources: PaginatedResponseDTO[ResourceDetailDTO] # Updated type
# from typing import Dict,Optional
# from pydantic import BaseModel

# class LogoutDTO(BaseModel):
#     access_token:str
#     username:str


# class CreateUserDTO(BaseModel):
#     username:str
#     first_name:str
#     last_name:str
#     email:str
#     password:str
#     profile_photo:str=""

# class DeleteLicenseDTO(BaseModel):
#     username:str
#     scope:str
#     force: Optional[bool] = True
# class SelfDeleteLicenseDTO(BaseModel):
#     token: str
#     tmp_secret_key:str
#     username:str
#     scope:str
#     force: Optional[bool] = True
# class DeletedLicenseResponseDTO(BaseModel):
#     ok:bool

# class AssignLicenseDTO(BaseModel):
#     username: str
#     scope:str
#     expires_in:str
#     force: Optional[bool] = True

# class AssignLicenseResponseDTO(BaseModel):
#     expires_at: str
#     ok:bool
    
# class UpdateUserPasswordDTO(BaseModel):
#     username:str
#     password: str
# class UpdateUserPasswordResponseDTO(BaseModel):
#     ok:bool

# class CreateScopeDTO(BaseModel):
#     name:str
# class CreatedScopeResponseDTO(BaseModel):
#     name:str

# class AssignScopeDTO(BaseModel):
#     name:str
#     username:str
# class AssignedScopeResponseDTO(BaseModel):
#     name:str
#     username:str
#     ok:bool

# class CreatedUserResponseDTO(BaseModel):
#     key: str

# class AuthDTO(BaseModel):
#     username:str
#     password:str
#     scope: Optional[str] = "Xolo"
#     expiration: Optional[str] = "15min",
#     renew_token: Optional[bool] = False


    
# class VerifyDTO(BaseModel):
#     access_token:str
#     username:str
#     secret:str
    


# class UserDTO(BaseModel):
#     key:str 
#     username:str
#     first_name:str
#     last_name:str
#     email:str
#     profile_photo:str
#     disabled:Optional[bool]=False

# class CreateGroupDTO(BaseModel):
#     name:str
#     description:Optional[str]=""