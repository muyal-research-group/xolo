import pytest
from xolo.abac.models import Policy

def test_policy():
    p = Policy.from_json("/home/nacho/Programming/Python/ABAC/data/p1.json")
    # Policy.model_validate()
    assert p.policy_id == "P1"