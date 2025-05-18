import pytest
from xolo.abac.models import Policy,AccessRequest
from xolo.abac.loader import PolicyLoader,AccessRequestLoader
from xolo.abac.graph import GraphBuilder
from xolo.abac.communities import CommunityDetector

def test_from_json_policy():
    p = Policy.from_json("/home/nacho/Programming/Python/ABAC/data/p1.json")
    assert p.policy_id == "P1"

def test_from_file_policies():
    ps = PolicyLoader.from_file("/home/nacho/Programming/Python/ABAC/data/policies.json")
    assert len(ps)==10

def test_from_file_access_reqs():
    ps = AccessRequestLoader.from_file("/home/nacho/Programming/Python/ABAC/data/requests.json")
    assert len(ps) == 20

    
def test_from_json_access_request():
    p = AccessRequest.from_json("/home/nacho/Programming/Python/ABAC/data/r1.json")
    assert p.subject.value == "Medico"


def test_graph_builder():
    policies = PolicyLoader.from_file("/home/nacho/Programming/Python/ABAC/data/policies.json")
    gb       = GraphBuilder()
    res      = gb.build_event_graph(policies=policies)
    assert len(res.edges) == 25 and len(res.nodes) == 25


def test_communities_detector():
    # LEO POLITICAS
    policies = PolicyLoader.from_file("/home/nacho/Programming/Python/ABAC/data/policies.json")
    # Hago instancia de graph builder
    gb       = GraphBuilder()
    # Genero grafo
    graph      = gb.build_event_graph(policies=policies)
    # Instancia de cd
    cd = CommunityDetector()
    # Detectar las comunidades
    x = cd.detect_communities(graph=graph)
