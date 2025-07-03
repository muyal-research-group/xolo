import pytest
from xolo.abac.models import Policy,AccessRequest
from xolo.abac.loader import PolicyLoader,AccessRequestLoader
from xolo.abac.graph import GraphBuilder
from xolo.abac.communities import CommunityDetector
from xolo.abac.evaluator import CommunityPolicyEvaluator


ps = PolicyLoader.from_file("/home/nacho/Programming/Python/ABAC/data/policies.json")
ce = CommunityPolicyEvaluator(
    policies= ps
)
def test_remove_policy():
    r = ce.remove_policy(policy_id="P1")
    assert len(ce.policies) == 9

def test_add_policy():
    r = ce.add_policy(policy= ps[0])
    assert len(ce.policies) == 10

def test_update_policy():
    p = ps[0]
    p.policy_id = "P1"
    r = ce.update_policy(
        updated_policy=p
    )
    assert len(ce.policies) == 10
