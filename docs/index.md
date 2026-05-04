# Xolo

Xolo is a Python package that combines:

- a typed HTTP client for the Xolo IAM API,
- local authorization engines for ACL, ABAC, RBAC, NGAC, and policy evaluation,
- shared cryptographic and utility helpers used by the local engines.

This repository is primarily the **client and local-engine package**. The live API used by the integration tests comes from the local Docker stack in `docker-compose.yml`.

## What changed in the client surface

The current `XoloClient` is centered on **account-scoped APIs**:

```python
from xolo.client.client import XoloClient

client = XoloClient(
    account_id="my-account",
    api_key="xk_live_...",
    api_url="http://localhost:10000/api/v4",
    admin_token="admin-token-for-admin-only-operations",
)
```

Most operations now target `/api/v4/accounts/{account_id}/...`, while the global policy-engine endpoints still live under `/api/v4/policies`.

## Package areas

### `xolo.client`

`xolo.client.client.XoloClient` wraps the live HTTP API and returns typed `option.Result` values. Successful calls return DTOs from `xolo.client.models`; failures return `xolo.client.errors.XoloError` subclasses.

### `xolo.abac`

Local ABAC policy loading and evaluation utilities, including graph building and event matching.

### `xolo.acl`

Encrypted local ACL storage with an autosave daemon.

### `xolo.policies`

Policy parser and local policy-engine helpers, including the Xolo-CL DSL.

## Local development shortcuts

```bash
poetry install
poetry run ruff check .
poetry build
poetry run zensical build --clean
```

For the live API-backed test flow, start the local stack first:

```bash
mkdir -p "$PWD/xolo/log"
export XOLO_OUTPUT_PATH="$PWD/xolo"
export XOLO_LOG_PATH="$PWD/xolo/log"
chmod +x deploy.sh && ./deploy.sh
poetry run coverage run -m pytest -v -s
poetry run coverage report -m
```

Continue with the dedicated guides for authentication, entity coverage, and development details.
