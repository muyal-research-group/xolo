# Authentication

The Xolo API uses three main authentication mechanisms, and the client combines them depending on the route family.

## 1. `X-Admin-Token`

Used for account-administration endpoints such as:

- `GET/POST /api/v4/accounts`
- account API key management
- scopes
- licenses
- admin user lifecycle operations

Configure it once on the client when you need those methods:

```python
client = XoloClient(
    account_id="research-account",
    api_key="xk_live_...",
    admin_token="admin-token",
)
```

## 2. `X-API-Key`

Used for:

- signup and auth flows,
- account-scoped user-context authorization APIs,
- global `/api/v4/policies` operations.

This is why `api_key` is a first-class constructor argument.

## 3. Bearer token + temporal secret

User-context routes rely on a bearer token issued by `auth()` and frequently a `Temporal-Secret-Key` header:

```python
auth = client.auth(
    username="alice",
    password="secret",
    scope="research",
    renew_token=True,
).unwrap()

client.get_current_user(
    token=auth.access_token,
    temporal_secret=auth.temporal_secret,
)
```

## Typical flow

1. Create or obtain an API key for the target account.
2. Sign up or provision users in that account.
3. Authenticate with `auth()` to obtain a bearer token and temporal secret.
4. Use the bearer token plus temporal secret for ACL, ABAC, NGAC, RBAC, and policy-engine operations.

## Notes about password recovery

The live account API exposes a two-step password recovery flow:

1. `request_password_recovery(identifier=...)`
2. `confirm_password_recovery(token=..., password=...)`

The older `update_user_password()` method remains as a compatibility wrapper and now expects the recovery token in its `secret` argument.
