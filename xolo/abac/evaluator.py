# core/evaluator_community.py

from typing import List, Dict
from xolo.abac.models import Policy,AccessRequest
from xolo.abac.matcher import EventMatcher
from xolo.abac.graph import GraphBuilder

class CommunityPolicyEvaluator:
    def __init__(self, policies: List[Policy]=[], policies_by_community: Dict[str, List[str]]={}):
        self.policies:Dict[str,Policy] = {p.policy_id: p for p in policies}
        self.policies_by_community = policies_by_community

  
    def set_policies(self,policies:List[Policy]=[]):
        self.policies = {p.policy_id: p for p in policies}
        # self.policies = policies
    def set_policies_by_community(self,policies_by_community: Dict[str, List[str]]={}):
        self.policies_by_community = policies_by_community
    def run(self, policies:List[Policy]=[],policies_by_community: Dict[str, List[str]]={} ):
        self.set_policies(policies=policies)
        self.set_policies_by_community(policies_by_community=policies_by_community)
        
      # Cargar pesos dinámicos de atributos basados en entropía
        self.attribute_weights = GraphBuilder.calculate_attribute_weights(policies)
        # Precalcular eventos agrupados por comunidad
        self.events_by_community = {}
        for community_id, policy_ids in policies_by_community.items():
            events = []
            for pid in policy_ids:
                policy = self.policies.get(pid)
                if policy:
                    events.extend(policy.events)
            self.events_by_community[community_id] = events


    def _weighted_match_score(self, event, request) -> float:
        score = 0.0
        def val(x): return x.value.strip().lower()

        if val(event.subject) == "*" or val(event.subject) == val(request.subject):
            score += self.attribute_weights.get("rol", 0)
        if val(event.asset) == "*" or val(event.asset) == val(request.asset):
            score += self.attribute_weights.get("recurso", 0)
        if val(event.space) == "*" or val(event.space) == val(request.space):
            score += self.attribute_weights.get("ubicacion", 0)
        if val(event.action) == "*" or val(event.action) == val(request.action):
            score += self.attribute_weights.get("accion", 0)

        if val(event.time) == "*":
            score += self.attribute_weights.get("rango_horario", 0)
        elif "-" in val(event.time):
            try:
                start, end = val(event.time).split("-")
                h, m = map(int, val(request.time).split(":"))
                req_minutes = h * 60 + m
                start_minutes = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
                end_minutes = int(end.split(":")[0]) * 60 + int(end.split(":")[1])
                if start_minutes <= req_minutes <= end_minutes:
                    score += self.attribute_weights.get("rango_horario", 0)
            except:
                pass

        return score

    def find_best_community(self, request: AccessRequest) -> str:
        best_community = None
        best_score = -1

        # print("\n Buscando mejor comunidad para la solicitud (ponderado por entropía):")
        # print(f"   {request}")

        for community_id, policy_ids in self.policies_by_community.items():
            max_score_in_community = 0.0

            for pid in policy_ids:
                policy = self.policies.get(pid)
                if not policy:
                    continue

                for event in policy.events:
                    score = self._weighted_match_score(event, request)
                    if score > max_score_in_community:
                        max_score_in_community = score

            # print(f"   - Comunidad {community_id}: mejor score {max_score_in_community:.4f}")

            if max_score_in_community > best_score:
                best_score = max_score_in_community
                best_community = community_id

        # print(f" Comunidad seleccionada: {best_community} (score: {best_score:.4f})")
        return best_community

    def order_policies_by_similarity(self, community_id: str, request: AccessRequest) -> List[str]:
        similarity_scores = {}

        for pid in self.policies_by_community.get(community_id, []):
            policy = self.policies.get(pid)
            if not policy:
                continue
            max_score = 0
            for event in policy.events:
                score = self._weighted_match_score(event, request)
                if score > max_score:
                    max_score = score
            similarity_scores[pid] = max_score

        sorted_policies = sorted(similarity_scores.keys(), key=lambda pid: similarity_scores[pid], reverse=True)

        # print("\n Orden de políticas en comunidad", community_id, "(ordenadas por similitud con solicitud)")
        # for idx, pid in enumerate(sorted_policies, 1):
        #     print(f"   {idx}. Política {pid} - Score {similarity_scores[pid]:.4f}")

        return sorted_policies

    def evaluate(self, request: AccessRequest) -> dict:
        best_community = self.find_best_community(request)

        if best_community is None:
            # print(" No se encontró comunidad para esta solicitud.\n")
            return {
                "result": "deny",
                "policy_id": None,
                "event_id": None
            }

        sorted_policies = self.order_policies_by_similarity(best_community, request)

        # print("\n Evaluando solicitud en comunidad", best_community)

        for idx, pid in enumerate(sorted_policies, 1):
            policy = self.policies.get(pid)
            if not policy:
                continue

            for event in policy.events:
                if EventMatcher.match_event(event, request):
                    # print(f" Coincidencia encontrada en política {policy.policy_id} (posición {idx}) evento {event.event_id}")
                    return {
                        "result": policy.effect,
                        "policy_id": policy.policy_id,
                        "event_id": event.event_id
                    }

        # print(" No se encontró coincidencia en comunidad.\n")
        return {
            "result": "deny",
            "policy_id": None,
            "event_id": None
        }
