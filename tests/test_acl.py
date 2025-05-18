import os
import pytest
import time as T
from xolo.acl.acl import Acl


def test_init_acl(self):
    output_path = "/mictlanx/xolo"
    filename = "xolotest.enc"
    fullpath = "{}/{}".format(output_path,filename)
    acl = Acl.load_or_create(
        output_path = output_path,
        key         = "ceb2d1e79b1edefa82ffa54b94b5bf911b534a8e6e60d0ce6bdeac72192c7d9b",
        filename    = filename,
        heartbeat   ="5sec"
    )
    print(acl.show())
    acl.add({
        "jcastillo":{
            "bucket-0":set(["write"])
        }
    })
    T.sleep(5)
    print(acl.show())
    self.assertTrue(os.path.exists(fullpath))