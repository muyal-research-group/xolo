from xolo.license import LicenseManager
import time as T
import pytest
lm = LicenseManager(secret_key=b"demontest")

@pytest.mark.skip("")
def test_generate_license():
    user_id        = "nacho"
    app_id         = "muyal"
    expires_in     = "1minutes"
    license_result = lm.generate_license(user_id=user_id, app_id= app_id,expires_in=expires_in)
    print(f"LICENSE GENERATE: {license_result}")
    # T.sleep(5)
    if license_result.is_ok:
        license = license_result.unwrap()
        T.sleep(2)
        result = lm.verify(user_id=user_id,app_id=app_id, license_key=license)
        print(f"LICENSE_VERIFY {result}")
        assert result.is_ok
# @pytest.mark.skip("")
def test_verify_license():
    user_id = "nacho"
    app_id  = "muyal"
    l = "KGB3NJWT4VTRFYLNJTVFN6RYP6KPKAQREBQ34U3OUSILSPDPDFNQAAAGPHR3FI"
    res = lm.verify(user_id=user_id,app_id=app_id, license_key=l)
    print("RESULT", res)
    
    assert True


    