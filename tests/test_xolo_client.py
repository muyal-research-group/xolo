import os
from typing import  Generator
from xolo.client.client import XoloClient
import pytest
from dotenv import load_dotenv
from uuid import uuid4

ENV_PATH = os.environ.get("ENV_PATH","/home/nacho/Programming/Python/xolo/tests/.env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
# from xolo.log import Log


@pytest.fixture(scope="module")
def xolo_client() -> Generator[XoloClient,None,None]:
     client = XoloClient(
        hostname = os.environ.get("XOLO_API_HOSTNAME","localhost"),
        port     = int(os.environ.get("XOLO_API_PORT","10000")),
        version  = int(os.environ.get("XOLO_API_VERSION","4"))
    )
     yield client
@pytest.mark.skip("")
def test_execute_script(xolo_client:XoloClient):
    script = """
    CREATE USER 'test' WITH PASSWORD='testpassword'
    UPDATE USER 'test' SET email='test@example.com'
    DELETE USER 'test'
    CREATE SCOPE 'testscope'
    """
    # ASSIGN SCOPE 'testscope' TO USER 'test'
    # CREATE LICENSE FOR USER 'test' IN SCOPE 'testscope' EXPIRES IN '1h'
    # GRANT 'read' ON 'resource1' TO ROLE 'testrole'
    # REVOKE 'write' ON 'resource2' FROM ROLE 'testrole'
    # LOAD ABAC POLICY FROM FILE '/path/to/policy.json' AS 'policy1'
    # EVALUATE REQUEST 'request1' AGAINST POLICY 'policy1'
    # ENCRYPT FILE '/path/to/plain.txt' AS '/path/to/encrypted.enc' WITH KEY 'encryptionkey'
    # DECRYPT FILE '/path/to/encrypted.enc' AS '/path
    cmds = xolo_client.execute_script(script_text=script)


@pytest.mark.skip("")
def test_self_delete_license(xolo_client:XoloClient):
    # res =xolo_client.get_resources_by_role(role="test")
    username = "jcastillo"
    scope = "imss"
    password = "bc24a0412c775cb3ee62e881283100cfbf3744a4467035c46397ccb09f50862c"
    auth_result = xolo_client.auth(
        username=username,
        password=password,
        scope = scope
    )
    assert auth_result.is_ok
    auth = auth_result.unwrap()
        
    

    res = xolo_client.self_delete_license(
        username=username,
        scope=scope,
        token= auth.access_token,
        secret=auth.temporal_secret,
        force=True,
    )
    print(res)

    if res.is_err:
        print(res.unwrap_err())
    assert res.is_ok
@pytest.mark.skip("")
def test_delete_license(xolo_client:XoloClient):
    res = xolo_client.delete_license(
        username="jcastillo",
        scope="imss",
        force=True,
        secret=""
    )
    if res.is_err:
        print(res.unwrap_err())
    assert res.is_ok




def test_full_logic(xolo_client:XoloClient):
    username   = f"richi-{uuid4().hex[:8]}"
    password   = "secret"
    secret     = "ed448c7a5449e9603058ce630e26c9e3befb2b15e3692411c001e0b4256852d2"
    scope      = f"muyal-{uuid4().hex[:8]}"
    expires_in = "1d"
    # 
    response = xolo_client.create_user(
        username      = username,
        password      = password,
        email         = "user0@email.com",
        first_name    = "First Name",
        last_name     = "Last Name",
        profile_photo = "",
    )
    assert response.is_ok, "Failed to create user: {}".format(response.unwrap_err())
    response = xolo_client.create_scope(scope=scope)
    assert response.is_ok, "Failed to create scope: {}".format(response.unwrap_err())
    response = xolo_client.assign_scope(username=username, scope=scope,secret=secret)
    assert response.is_ok, "Failed to assign scope: {}".format(response.unwrap_err())
    response = xolo_client.create_license(username=username, scope=scope,secret=secret,expires_in=expires_in)
    assert response.is_ok, "Failed to create license: {}".format(response.unwrap_err())

    response = xolo_client.auth(username=username, password=password,scope=scope,expiration=expires_in,renew_token=True)
    assert response.is_ok, "Failed to authenticate user: {}".format(response.unwrap_err())
    auth = response.unwrap()
    
    response = xolo_client.get_users_resources(token=auth.access_token,temporal_secret=auth.temporal_secret)
    assert response.is_ok, "Failed to get user dashboard: {}".format(response.unwrap_err())
    dashboard = response.unwrap()
    print(dashboard)

    response = xolo_client.get_current_user(
        token           = auth.access_token,
        temporal_secret = auth.temporal_secret,
    )
    assert response.is_ok, "Failed to get user info: {}".format(response.unwrap_err())
    user_info = response.unwrap()
    print(user_info)