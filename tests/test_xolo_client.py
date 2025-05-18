import os
import pandas as pd
from typing import  Generator
import secrets
from xolo.client.client import XoloClient
from xolo.utils import Utils
import pytest
from dotenv import load_dotenv

ENV_PATH = os.environ.get("ENV_PATH","/home/nacho/Programming/Python/xolo/tests/.env")
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
# from xolo.log import Log


xolo_client = XoloClient(
    hostname = os.environ.get("XOLO_API_HOSTNAME","localhost"),
    port     = int(os.environ.get("XOLO_API_PORT","10001")),
    version  = int(os.environ.get("XOLO_API_VERSION","4"))
)

    # hostname = os.environ.get("XOLO_API_HOSTNAME","alpha.tamps.cinvestav.mx/xoloapi"),
    # port     = int(os.environ.get("XOLO_API_PORT","-1")),

@pytest.mark.skip("")
def test_self_delete_license():
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
def test_delete_license():
    # res =xolo_client.get_resources_by_role(role="test")
    res = xolo_client.delete_license(
        username="jcastillo",
        scope="imss",
        force=True,
        secret=""
    )
    if res.is_err:
        print(res.unwrap_err())
    assert res.is_ok

@pytest.mark.skip("")
def test_get_resources():
    res =xolo_client.get_resources_by_role(role="test")
    print(res)
    assert res.is_ok

@pytest.mark.skip("")
def test_grantx():
    res =xolo_client.grantx(role="test",grants={"test":{"b1":["read"]}})
    print(res)
    assert res.is_ok

@pytest.mark.skip("")
def test_create_user():
    username="richi"
    password="secret"
    response = xolo_client.create_user(
        username=username,
        password=password,
        email="user0@email.com",
        first_name="First Name",
        last_name="Last Name",
        profile_photo="",
        role="user0",
    )
    print(response)
    assert response.is_ok

@pytest.mark.skip("")
def test_create_scope():
    scope    = "muyal"
    response = xolo_client.create_scope(scope=scope)
    assert response.is_ok

@pytest.mark.skip("")
def test_assign_scope():
    username = "richi"
    scope    = "muyal"
    secret   = "ed448c7a5449e9603058ce630e26c9e3befb2b15e3692411c001e0b4256852d2"
    response = xolo_client.assign_scope(username=username, scope=scope,secret=secret)
    print(response)
    assert response.is_ok

@pytest.mark.skip("")
def test_create_license():
    username   = "user0"
    scope      = "muyal"
    secret     = "ed448c7a5449e9603058ce630e26c9e3befb2b15e3692411c001e0b4256852d2"
    expires_in = "1h" # 1 Hours
    response = xolo_client.create_license(username=username, scope=scope,secret=secret,expires_in=expires_in)
    print(response)
    assert response.is_ok

@pytest.mark.skip("")
def test_auth():
    username = "richi"
    password = "secret"
    response = xolo_client.auth(username=username, password=password,scope="Muyal")
    print(response)
    assert response.is_ok

@pytest.mark.skip("")
def test_grant():
    response = xolo_client.grants(
        grants={
            ""
        }
    )
    print(response)
    assert response.is_ok

@pytest.mark.skip("")
def test_create_bulk_users():
    df = pd.read_csv("./data/user_prod.csv")
    for i, row in df.iterrows():
        username = row["USERNAME"]
        res = xolo_client.create_user(
            username= username,
            first_name=row["FIRSTNAME"],
            last_name=row["LASTNAME"],
            email=row["EMAIL"],
            password=row["PASSWORD"],
        )
        if res.is_ok:
            print("{} created successfully".format(username))
    
def data_generator(num_chunks:int,n:int)->Generator[bytes,None,None]:
    for i in range(num_chunks):
        yield secrets.token_bytes(n)

@pytest.mark.skip("")
def test_sha256_stream():
    num_chunks = 5
    n = 1000

    data = data_generator(num_chunks=num_chunks,n = n)
    (checksum ,size)= Utils.sha256_stream(gen= data)
    print(checksum,size)
    assert (num_chunks*n) == size




