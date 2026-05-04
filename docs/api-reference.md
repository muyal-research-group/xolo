# API reference

This page summarizes the public `XoloClient` API with an emphasis on:

- **parameters** you need to provide,
- **return DTOs** wrapped in `Result[...]`,
- **route/auth expectations** for each method family.

Every method returns `Result[SuccessDTO, XoloError]`. On success, unwrap the DTO; on failure, unwrap the error.

## Constructor

### `XoloClient(account_id, api_key, api_url="http://localhost:10000/api/v4", secret="", admin_token="")`

| Parameter | Meaning |
| --- | --- |
| `account_id` | Required account scope for `/api/v4/accounts/{account_id}/...` routes. |
| `api_key` | Default key for API-key-protected operations and user-context authorization APIs. |
| `api_url` | Base API root. |
| `secret` | Legacy compatibility field retained for older callers. |
| `admin_token` | Admin token for account administration routes. |

**Returns:** a configured `XoloClient` instance.

API-key-backed public methods accept an optional trailing `api_key=""` parameter to override the constructor default for a single request.

## Core methods

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `execute_script()` | `script_text` | `list` | Parses and executes Xolo-CL commands. |
| `base_url()` | none | `str` | Returns the account-scoped base URL. |

## Accounts

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `list_accounts()` | `admin_token=""` | `list[AccountDTO]` | Uses `X-Admin-Token`. |
| `create_account()` | `account_id`, `name`, `admin_token=""` | `AccountDTO` | Creates a new account. |
| `delete_account()` | `account_id`, `admin_token=""` | `DeletedAccountResponseDTO` | Synthetic success DTO for delete. |

## Users

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `signup()` | `username`, `first_name`, `last_name`, `email`, `password`, `scope`, `profile_photo=""`, `expiration="1h"`, `api_key=""` | `CreatedUserResponseDTO` | Uses `X-API-Key`. |
| `create_user()` | `username`, `first_name`, `last_name`, `email`, `password`, `profile_photo=""`, `admin_token=""`, `role=None` | `CreatedUserResponseDTO` | Admin endpoint; `role` is compatibility-only. |
| `list_users()` | `admin_token=""` | `list[UserDTO]` | Admin endpoint. |
| `delete_user()` | `username`, `admin_token=""` | `DeletedUserResponseDTO` | Admin endpoint. |
| `block_user()` | `username`, `admin_token=""` | `BlockedUserResponseDTO` | Admin endpoint. |
| `unblock_user()` | `username`, `admin_token=""` | `UnblockedUserResponseDTO` | Admin endpoint. |
| `enable_user()` | `username`, `token`, `temporal_secret` | `UserEnabledResponseDTO` | Bearer + temporal secret. |
| `disable_user()` | `username`, `token`, `temporal_secret` | `UserDisabledResponseDTO` | Bearer + temporal secret. |
| `auth()` | `username`, `password`, `scope`, `expiration="1h"`, `renew_token=False`, `api_key=""` | `AuthenticatedDTO` | Uses `X-API-Key`; returns access token + temporal secret. |
| `verify_token()` | `access_token`, `username`, `secret=""` | `VerifyTokenResponseDTO` | Verification flow for issued tokens. |
| `get_current_user()` | `token`, `temporal_secret` | `UserDTO` | Bearer-authenticated profile lookup. |
| `logout()` | `username`, `access_token`, `token`, `temporal_secret` | `OperationResultDTO` | Revokes the session represented by the access token. |
| `request_password_recovery()` | `identifier` | `OperationResultDTO` | Starts password-reset flow. |
| `confirm_password_recovery()` | `token`, `password` | `OperationResultDTO` | Completes password-reset flow. |
| `update_user_password()` | `username`, `password`, `secret=""` | `UpdateUserPasswordResponseDTO` | Compatibility wrapper; `secret` now carries the recovery token. |

## Scopes

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_scope()` | `scope`, `secret=""`, `admin_token=""` | `CreatedScopeResponseDTO` | Admin endpoint. |
| `list_scopes()` | `admin_token=""` | `list[CreatedScopeResponseDTO]` | Admin endpoint. |
| `delete_scope()` | `scope`, `admin_token=""` | `DeletedScopeResponseDTO` | Admin endpoint. |
| `assign_scope()` | `username`, `scope`, `secret`, `admin_token=""` | `AssignedScopeResponseDTO` | Admin endpoint; `secret` retained for compatibility. |
| `unassign_scope()` | `username`, `scope`, `admin_token=""` | `UnassignedScopeResponseDTO` | Admin endpoint. |
| `list_scope_assignments()` | `admin_token=""` | `list[AssignedScopeResponseDTO]` | Admin endpoint. |

## Licenses

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_license()` | `username`, `scope`, `secret`, `expires_in="1h"`, `force=True`, `admin_token=""` | `AssignLicenseResponseDTO` | Admin endpoint; `secret` retained for compatibility. |
| `list_licenses()` | `admin_token=""` | `list[LicenseDTO]` | Admin endpoint. |
| `delete_license()` | `username`, `scope`, `force=True`, `secret=""`, `admin_token=""` | `DeletedLicenseResponseDTO` | Admin endpoint. |
| `self_delete_license()` | `username`, `scope`, `token`, `secret`, `force=True` | `DeletedLicenseResponseDTO` | Caller-driven self-service endpoint. |

## API keys

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_api_key()` | `name`, `scopes`, `expires_at=None`, `admin_token=""` | `CreatedAPIKeyResponseDTO` | Admin endpoint; raw key is returned only once. |
| `list_api_keys()` | `admin_token=""` | `list[APIKeyMetadataDTO]` | Admin endpoint. |
| `get_api_key()` | `key_id`, `admin_token=""` | `APIKeyMetadataDTO` | Admin endpoint. |
| `revoke_api_key()` | `key_id`, `admin_token=""` | `RevokedAPIKeyResponseDTO` | Synthetic success DTO for delete. |
| `rotate_api_key()` | `key_id`, `admin_token=""` | `RotatedAPIKeyResponseDTO` | New raw key is returned only once. |

## ACL

All methods in this section accept `api_key=""` and `admin_token=""`; at least one of them must be available for the request.

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `get_users_resources()` | `token`, `temporal_secret`, `owned_page=1`, `owned_page_size=10`, `shared_page=1`, `shared_page_size=10` | `UsersResourcesDTO` | Bearer + temporal secret + admin token or API key. |
| `create_group()` | `name`, `description`, `token`, `temporal_secret` | `CreatedGroupResponseDTO` | Creates an ACL group. |
| `delete_group()` | `group_id`, `token`, `temporal_secret` | `DeletedGroupResponseDTO` | Deletes a group. |
| `add_members_to_group()` | `group_id`, `members`, `token`, `temporal_secret` | `GroupMembersUpdateResponseDTO` | Adds user IDs to a group. |
| `remove_members_from_group()` | `group_id`, `members`, `token`, `temporal_secret` | `GroupMembersUpdateResponseDTO` | Removes user IDs from a group. |
| `grant_permission()` | `resource_id`, `principal_id`, `permissions`, `token`, `temporal_secret`, `principal_type="USER"` | `PermissionUpdateResponseDTO` | Grants ACL permissions. |
| `revoke_permission()` | `resource_id`, `principal_id`, `permissions`, `token`, `temporal_secret`, `principal_type="USER"` | `PermissionUpdateResponseDTO` | Revokes ACL permissions. |
| `claim_resource()` | `resource_id`, `token`, `temporal_secret` | `ClaimedResourceResponseDTO` | Claims resource ownership. |
| `check_permission_auth()` | `resource_id`, `permissions`, `token`, `temporal_secret` | `CheckPermissionResponseDTO` | Checks permissions for the authenticated caller. |

## ABAC

All methods in this section accept `api_key=""` and `admin_token=""`; at least one of them must be available for the request.

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_abac_policy()` | `name`, `effect`, `events`, `token`, `temporal_secret` | `CreatedABACPolicyResponseDTO` | Creates an account-scoped ABAC policy. |
| `list_abac_policies()` | `token`, `temporal_secret` | `list[ABACPolicyDTO]` | Lists ABAC policies. |
| `get_abac_policy()` | `policy_id`, `token`, `temporal_secret` | `ABACPolicyDTO` | Fetches a single ABAC policy. |
| `delete_abac_policy()` | `policy_id`, `token`, `temporal_secret` | `DeletedABACPolicyResponseDTO` | Deletes an ABAC policy. |
| `evaluate_abac()` | `subject`, `resource`, `action`, `token`, `temporal_secret`, `location="*"`, `time=None` | `ABACDecisionDTO` | Evaluates an ABAC request. |

## NGAC

All methods in this section accept `api_key=""` and `admin_token=""`; at least one of them must be available for the request.

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_ngac_node()` | `name`, `node_type`, `token`, `temporal_secret`, `properties=None` | `CreatedNGACNodeResponseDTO` | Creates an NGAC node. |
| `list_ngac_nodes()` | `token`, `temporal_secret`, `node_type=None` | `list[NGACNodeDTO]` | Optional filtering by node type. |
| `get_ngac_node()` | `node_id`, `token`, `temporal_secret` | `NGACNodeDTO` | Fetches one node. |
| `delete_ngac_node()` | `node_id`, `token`, `temporal_secret` | `DeletedNGACNodeResponseDTO` | Deletes a node. |
| `ngac_assign()` | `from_id`, `to_id`, `token`, `temporal_secret` | `NGACAssignmentMutationResponseDTO` | Creates a node assignment. |
| `ngac_remove_assignment()` | `from_id`, `to_id`, `token`, `temporal_secret` | `NGACAssignmentMutationResponseDTO` | Removes a node assignment. |
| `list_ngac_assignments()` | `token`, `temporal_secret` | `list[NGACAssignmentDTO]` | Lists assignments. |
| `ngac_associate()` | `user_attribute_id`, `object_attribute_id`, `operations`, `token`, `temporal_secret` | `NGACAssociationMutationResponseDTO` | Creates an association. |
| `ngac_remove_association()` | `association_id`, `token`, `temporal_secret` | `NGACAssociationDeletionResponseDTO` | Deletes an association. |
| `list_ngac_associations()` | `token`, `temporal_secret` | `list[NGACAssociationDTO]` | Lists associations. |
| `ngac_check()` | `user_id`, `object_id`, `operation`, `token`, `temporal_secret` | `NGACDecisionDTO` | Evaluates NGAC access. |

## RBAC

All methods in this section accept `api_key=""` and `admin_token=""`; at least one of them must be available for the request.

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_role()` | `name`, `token`, `temporal_secret`, `description=None`, `permissions=None`, `api_key=""` | `RoleDTO` | Creates a role. |
| `list_roles()` | `token`, `temporal_secret`, `api_key=""` | `list[RoleDTO]` | Lists roles. |
| `get_role()` | `role_id`, `token`, `temporal_secret`, `api_key=""` | `RoleDTO` | Fetches one role. |
| `update_role()` | `role_id`, `token`, `temporal_secret`, `name=None`, `description=None`, `api_key=""` | `RoleDTO` | Updates role metadata. |
| `delete_role()` | `role_id`, `token`, `temporal_secret`, `api_key=""` | `DeletedRoleResponseDTO` | Deletes a role. |
| `add_role_permission()` | `role_id`, `permission`, `token`, `temporal_secret`, `api_key=""` | `RoleDTO` | Adds a permission to a role. |
| `remove_role_permission()` | `role_id`, `permission`, `token`, `temporal_secret`, `api_key=""` | `RoleDTO` | Removes a permission from a role. |
| `add_role_parent()` | `role_id`, `parent_role_id`, `token`, `temporal_secret`, `api_key=""` | `RoleDTO` | Adds role inheritance. |
| `remove_role_parent()` | `role_id`, `parent_role_id`, `token`, `temporal_secret`, `api_key=""` | `RoleDTO` | Removes role inheritance. |
| `assign_role()` | `subject_id`, `role_id`, `token`, `temporal_secret`, `api_key=""` | `AssignmentDTO` | Assigns a role to a subject. |
| `unassign_role()` | `subject_id`, `role_id`, `token`, `temporal_secret`, `api_key=""` | `UnassignedRoleResponseDTO` | Removes a role assignment. |
| `get_subject_roles()` | `subject_id`, `token`, `temporal_secret`, `api_key=""` | `list[RoleDTO]` | Lists subject roles. |
| `check_rbac_permission()` | `subject_id`, `permission`, `token`, `temporal_secret`, `api_key=""` | `RBACCheckResultDTO` | Checks a permission. |
| `get_effective_permissions()` | `subject_id`, `token`, `temporal_secret`, `api_key=""` | `EffectivePermissionsDTO` | Lists inherited/effective permissions. |

## Global policy engine

These methods target global `/api/v4/policies` routes rather than account-scoped ones.

| Method | Parameters | Returns | Notes |
| --- | --- | --- | --- |
| `create_policies()` | `policies`, `token`, `temporal_secret`, `api_key=""` | `PolicyCreateResponseDTO` | Creates policy-engine policies in bulk. |
| `list_policies()` | `token`, `temporal_secret`, `api_key=""` | `list[PolicyDTO]` | Lists global policies. |
| `get_policy()` | `policy_id`, `token`, `temporal_secret`, `api_key=""` | `PolicyDTO` | Fetches one global policy. |
| `update_policy()` | `policy_id`, `policy`, `token`, `temporal_secret`, `api_key=""` | `PolicyUpdateResponseDTO` | Replaces a global policy. |
| `delete_policy()` | `policy_id`, `token`, `temporal_secret`, `api_key=""` | `PolicyDeleteResponseDTO` | Deletes a global policy. |
| `prepare_policy_communities()` | `token`, `temporal_secret`, `api_key=""` | `PoliciesPreparedResponseDTO` | Prepares policy communities before evaluation/injection workflows. |
| `evaluate_policy_request()` | `request`, `token`, `temporal_secret`, `api_key=""` | `PolicyEvaluationResponseDTO` | Evaluates one request. |
| `evaluate_policy_batch()` | `requests`, `token`, `temporal_secret`, `api_key=""` | `list[PolicyBatchEvaluationItemDTO]` | Evaluates multiple requests. |
| `inject_policy()` | `policy`, `token`, `temporal_secret`, `api_key=""` | `PolicyInjectResponseDTO` | Injects a policy into the prepared engine. |

## Return conventions

- **`Result[DTO, XoloError]`** is the default shape.
- Delete and mutation endpoints sometimes return **synthetic success DTOs** even when the HTTP response body is empty.
- List endpoints return plain Python lists of DTOs rather than pagination wrappers unless the server response itself is paginated.

## Error conventions

The client maps HTTP failures into typed `XoloError` subclasses, including:

- `UnauthorizedError`
- `AccessDeniedError`
- `ValidationError`
- `NotFoundError`
- `ConflictError`

That means callers can keep normal Python control flow while still handling structured API failures via `Result`.
