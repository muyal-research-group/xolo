from xolo.client.client import XoloClient
from xolo.client import models as M


def _policy_component(attribute: str, value: str) -> M.PolicyAttributeComponentDTO:
    return M.PolicyAttributeComponentDTO(attribute=attribute, value=value)


def _policy_request(
    subject: str,
    asset: str,
    space: str,
    time_value: str,
    action: str,
) -> M.PolicyAccessRequestDTO:
    return M.PolicyAccessRequestDTO(
        subject=_policy_component("role", subject),
        asset=_policy_component("resource", asset),
        space=_policy_component("location", space),
        time=_policy_component("time", time_value),
        action=_policy_component("action", action),
    )


def _policy(policy_id: str, description: str) -> M.PolicyDTO:
    return M.PolicyDTO(
        policy_id=policy_id,
        description=description,
        effect="permit",
        events=[
            M.PolicyEventDTO(
                event_id=f"{policy_id}-event",
                subject=_policy_component("role", "Doctor"),
                asset=_policy_component("resource", "Chart"),
                space=_policy_component("location", "Hospital"),
                time=_policy_component("time", "08:00-20:00"),
                action=_policy_component("action", "read"),
            )
        ],
    )


def test_policy_methods_return_expected_dtos(
    protected_client: XoloClient,
    make_signed_up_user,
    rand_name,
    unwrap_ok,
    unwrap_ok_list,
):
    user = make_signed_up_user()
    policy_id = rand_name("policy")
    policy = _policy(policy_id=policy_id, description="integration policy")

    created_policies = unwrap_ok(
        protected_client.create_policies(
            policies=[policy],
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyCreateResponseDTO,
    )
    assert created_policies.n_added >= 1

    policies = unwrap_ok_list(
        protected_client.list_policies(
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyDTO,
    )
    assert any(item.policy_id == policy_id for item in policies)

    fetched_policy = unwrap_ok(
        protected_client.get_policy(
            policy_id=policy_id,
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyDTO,
    )
    assert fetched_policy.policy_id == policy_id
    assert fetched_policy.description == "integration policy"

    updated_policy = _policy(policy_id=policy_id, description="updated policy")
    updated = unwrap_ok(
        protected_client.update_policy(
            policy_id=policy_id,
            policy=updated_policy,
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyUpdateResponseDTO,
    )
    assert updated.detail == "Policy updated"

    prepared = unwrap_ok(
        protected_client.prepare_policy_communities(
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PoliciesPreparedResponseDTO,
    )
    assert isinstance(prepared.model_dump(), dict)

    request = _policy_request(
        subject="Doctor",
        asset="Chart",
        space="Hospital",
        time_value="10:00",
        action="read",
    )

    evaluated = unwrap_ok(
        protected_client.evaluate_policy_request(
            request=request,
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyEvaluationResponseDTO,
    )
    assert isinstance(evaluated.result, str)

    batch = unwrap_ok_list(
        protected_client.evaluate_policy_batch(
            requests=[request],
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyBatchEvaluationItemDTO,
    )
    assert len(batch) == 1
    assert isinstance(batch[0].model_dump(), dict)

    injected_policy = _policy(
        policy_id=rand_name("injected-policy"),
        description="injected policy",
    )
    injected = unwrap_ok(
        protected_client.inject_policy(
            policy=injected_policy,
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyInjectResponseDTO,
    )
    assert injected.detail == "Policy injected"

    deleted = unwrap_ok(
        protected_client.delete_policy(
            policy_id=policy_id,
            token=user.auth.access_token,
            temporal_secret=user.auth.temporal_secret,
        ),
        M.PolicyDeleteResponseDTO,
    )
    assert deleted.detail == "Policy deleted"
