import json
from unittest.mock import patch

import requests

from xolo.client import errors as E
from xolo.client import models as M
from xolo.client.client import XoloClient


def _response(payload=None, status_code: int = 200) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.url = "http://localhost/test"
    response.headers = {}
    if payload is None:
        response._content = b""
    else:
        response._content = json.dumps(payload).encode()
        response.headers["Content-Type"] = "application/json"
    return response


def test_auth_uses_account_scoped_url_and_api_key_header():
    client = XoloClient(account_id="acct-1", api_key="test-api-key", api_url="http://localhost:10000/api/v4")

    with patch("xolo.client.client.R.request", return_value=_response(
        {
            "key": "user-1",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "profile_photo": "",
            "access_token": "token-1",
            "metadata": {},
            "temporal_secret": "temp-1",
        }
    )) as request:
        result = client.auth(username="alice", password="secret", scope="scope-1")

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["url"] == "http://localhost:10000/api/v4/accounts/acct-1/users/auth"
    assert kwargs["headers"] == {"X-API-Key": "test-api-key"}
    assert kwargs["json"]["scope"] == "scope-1"


def test_create_scope_uses_admin_token_and_account_scoped_url():
    client = XoloClient(
        account_id="acct-1",
        api_key="",
        api_url="http://localhost:10000/api/v4",
        admin_token="admin-1",
    )

    with patch("xolo.client.client.R.request", return_value=_response({"name": "SCOPE-1"})) as request:
        result = client.create_scope(scope="scope-1")

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["url"] == "http://localhost:10000/api/v4/accounts/acct-1/scopes"
    assert kwargs["headers"] == {"X-Admin-Token": "admin-1"}
    assert kwargs["json"] == {"name": "scope-1"}


def test_create_role_uses_bearer_temporal_secret_and_api_key():
    client = XoloClient(account_id="acct-1", api_key="api-key", api_url="http://localhost:10000/api/v4")

    with patch("xolo.client.client.R.request", return_value=_response(
        {
            "role_id": "role-1",
            "name": "Reader",
            "description": "Read only",
            "permissions": ["documents:read"],
            "parent_role_ids": [],
        }
    )) as request:
        result = client.create_role(
            name="Reader",
            description="Read only",
            permissions=["documents:read"],
            token="bearer-1",
            temporal_secret="temp-1",
        )

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["url"] == "http://localhost:10000/api/v4/accounts/acct-1/rbac/roles"
    assert kwargs["headers"] == {
        "Authorization": "Bearer bearer-1",
        "Temporal-Secret-Key": "temp-1",
        "X-API-Key": "api-key",
    }


def test_create_role_allows_api_key_override():
    client = XoloClient(account_id="acct-1", api_key="default-api-key", api_url="http://localhost:10000/api/v4")

    with patch("xolo.client.client.R.request", return_value=_response(
        {
            "role_id": "role-1",
            "name": "Reader",
            "description": "Read only",
            "permissions": ["documents:read"],
            "parent_role_ids": [],
        }
    )) as request:
        result = client.create_role(
            name="Reader",
            description="Read only",
            permissions=["documents:read"],
            token="bearer-1",
            temporal_secret="temp-1",
            api_key="override-api-key",
        )

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["headers"] == {
        "Authorization": "Bearer bearer-1",
        "Temporal-Secret-Key": "temp-1",
        "X-API-Key": "override-api-key",
    }


def test_create_role_allows_admin_token_without_api_key():
    client = XoloClient(account_id="acct-1", api_key="", api_url="http://localhost:10000/api/v4", admin_token="admin-1")

    with patch("xolo.client.client.R.request", return_value=_response(
        {
            "role_id": "role-1",
            "name": "Reader",
            "description": "Read only",
            "permissions": ["documents:read"],
            "parent_role_ids": [],
        }
    )) as request:
        result = client.create_role(
            name="Reader",
            description="Read only",
            permissions=["documents:read"],
            token="bearer-1",
            temporal_secret="temp-1",
        )

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["headers"] == {
        "Authorization": "Bearer bearer-1",
        "Temporal-Secret-Key": "temp-1",
        "X-Admin-Token": "admin-1",
    }


def test_create_role_requires_admin_token_or_api_key():
    client = XoloClient(account_id="acct-1", api_key="", api_url="http://localhost:10000/api/v4")

    with patch("xolo.client.client.R.request") as request:
        result = client.create_role(
            name="Reader",
            description="Read only",
            permissions=["documents:read"],
            token="bearer-1",
            temporal_secret="temp-1",
        )

    assert result.is_err
    assert not request.called


def test_get_current_user_does_not_send_api_key_header():
    client = XoloClient(account_id="acct-1", api_key="api-key", api_url="http://localhost:10000/api/v4")

    with patch("xolo.client.client.R.request", return_value=_response(
        {
            "key": "user-1",
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
            "profile_photo": "",
            "metadata": {},
        }
    )) as request:
        result = client.get_current_user(token="bearer-1", temporal_secret="temp-1")

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["headers"] == {
        "Authorization": "Bearer bearer-1",
        "Temporal-Secret-Key": "temp-1",
    }


def test_list_accounts_uses_global_accounts_endpoint():
    client = XoloClient(account_id="acct-1", api_key="", api_url="http://localhost:10000/api/v4", admin_token="admin-1")

    with patch("xolo.client.client.R.request", return_value=_response([{"account_id": "acct-1", "name": "Primary"}])) as request:
        result = client.list_accounts()

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["url"] == "http://localhost:10000/api/v4/accounts"
    assert kwargs["headers"] == {"X-Admin-Token": "admin-1"}


def test_create_policies_uses_global_policy_endpoint_and_api_key():
    client = XoloClient(account_id="acct-1", api_key="api-key", api_url="http://localhost:10000/api/v4")
    policy = M.PolicyDTO(
        policy_id="policy-1",
        description="Example policy",
        effect="permit",
        events=[],
    )

    with patch("xolo.client.client.R.request", return_value=_response({"n_added": 1})) as request:
        result = client.create_policies(
            policies=[policy],
            token="bearer-1",
            temporal_secret="temp-1",
        )

    assert result.is_ok
    kwargs = request.call_args.kwargs
    assert kwargs["method"] == "POST"
    assert kwargs["url"] == "http://localhost:10000/api/v4/policies"
    assert kwargs["headers"] == {
        "Authorization": "Bearer bearer-1",
        "Temporal-Secret-Key": "temp-1",
        "X-API-Key": "api-key",
    }
    assert kwargs["json"][0]["policy_id"] == "policy-1"


def test_update_user_password_requires_recovery_token():
    client = XoloClient(account_id="acct-1", api_key="api-key", api_url="http://localhost:10000/api/v4")

    result = client.update_user_password(username="alice", password="new-password")

    assert result.is_err
    error = result.unwrap_err()
    assert isinstance(error, E.ValidationError)
