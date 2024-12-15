import os
import unittest
import pandas as pd
from typing import  Generator
import secrets
from xolo.client.client import XoloClient
from xolo.utils import Utils
# from xolo.log import Log


class XoloTest(unittest.TestCase):
    xolo_client = XoloClient(
        # hostname = os.environ.get("XOLO_API_HOSTNAME","alpha.tamps.cinvestav.mx/xoloapi"),
        # port     = int(os.environ.get("XOLO_API_PORT","-1")),
        hostname = os.environ.get("XOLO_API_HOSTNAME","localhost"),
        port     = int(os.environ.get("XOLO_API_PORT","10001")),
        version  = int(os.environ.get("XOLO_API_VERSION","4"))
    )
    
    @unittest.skip("")
    def test_auth(self):
        XoloTest.xolo_client.create_user()
        XoloTest.xolo_client.grants({
            "jcastillo":{
                "bucket-0":["write","read"]
            }
        })

        response = XoloTest.xolo_client.auth(
            username="jcastillo",
            password="bc24a0412c775cb3ee62e881283100cfbf3744a4467035c46397ccb09f50862c"
        )
        print(response)
        return self.assertTrue(response.is_ok)
    
    @unittest.skip("")
    def test_grant(self):
        response = XoloTest.xolo_client.grants(
            grants={
                ""
            }
        )
        print(response)
        return self.assertTrue(response.is_ok)

    @unittest.skip("")
    def test_create_bulk_users(self):
        df = pd.read_csv("./data/user_prod.csv")
        for i, row in df.iterrows():
            username = row["USERNAME"]
            res = XoloTest.xolo_client.create_user(
                username= username,
                first_name=row["FIRSTNAME"],
                last_name=row["LASTNAME"],
                email=row["EMAIL"],
                password=row["PASSWORD"],
            )
            if res.is_ok:
                print("{} created successfully".format(username))
        
    @staticmethod
    def data_generator(num_chunks:int,n:int)->Generator[bytes,None,None]:
        for i in range(num_chunks):
            yield secrets.token_bytes(n)
    def test_sha256_stream(self):
        num_chunks = 5
        n = 1000

        data = XoloTest.data_generator(num_chunks=num_chunks,n = n)
        (checksum ,size)= Utils.sha256_stream(gen= data)
        print(checksum,size)
        return self.assertTrue((num_chunks*n) == size)





if __name__ =="__main__":
    unittest.main()