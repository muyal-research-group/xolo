# Xolo repository instructions

## Build, test, and lint commands

- Install dependencies with `poetry install`.
- Build the package with `poetry build`.
- Build docs with `poetry run zensical build --clean`.
- Lint with `ruff check .`. The GitHub Actions workflow runs Ruff as a non-blocking check today (`continue-on-error: true` in `.github/workflows/run_test.yml`).
- Run the non-integration pytest subset with:

  ```bash
  poetry run pytest tests/test_abac.py tests/test_evaluator.py tests/test_acl.py tests/test_xolo_acl.py tests/test_license.py tests/test_abac_ngac_client.py -q
  ```

- Run a single test with:

  ```bash
  poetry run pytest tests/test_acl.py::test_claim_ownership -q
  ```

- Run the CI-style test flow for the live client/integration coverage after starting the local stack:

  ```bash
  mkdir -p "$PWD/xolo/log"
  export XOLO_OUTPUT_PATH="$PWD/xolo"
  export XOLO_LOG_PATH="$PWD/xolo/log"
  chmod +x deploy.sh && ./deploy.sh
  poetry run coverage run -m pytest -v -s
  poetry run coverage report -m
  ```

`tests/test_xolo_client.py` is the main live API/integration file. It reads `XOLO_API_URL` from `tests/.env` and assumes the API is available at `http://localhost:10000/api/v4` unless overridden.

## High-level architecture

- This repository primarily contains the **Python package**, not the Xolo API server implementation. `docker-compose.yml` starts MongoDB, Redis, and an external `xolo:api-*` image so client integration tests can run against a live API.
- `xolo.client.client.XoloClient` is the main integration surface. It wraps HTTP endpoints, normalizes auth headers, and returns typed `option.Result` values containing DTOs from `xolo.client.models` instead of raw response dicts.
- `xolo.policies.parser` adds a DSL layer ("Xolo-CL"). `build_parser()` turns scripts into command objects from `xolo.policies.parser.models`, and those commands execute against a provided `XoloClient`.
- `xolo.abac` is a local evaluation pipeline: JSON fixtures load into Pydantic `Policy` / `AccessRequest` models, `GraphBuilder` creates an entropy-weighted event graph, `CommunityDetector` runs Louvain community detection, and `CommunityPolicyEvaluator` narrows evaluation before `EventMatcher` performs the final attribute match.
- `xolo.acl.acl.Acl` is a local encrypted ACL store. It persists grants as encrypted JSON via `xolo.utils.Utils`, and `AclDaemon` auto-saves in a background thread while logging through `xolo.log.Log`.
- `xolo.license` and `xolo.utils` provide the shared crypto/time/path helpers used across the local engines.

## Key conventions

- Prefer the repository's `option` types: public-facing methods commonly return `Result[...]` / `Ok` / `Err`, and ACL code also uses `Option` / `Some` / `NONE`. Tests assert on `is_ok` / `is_err` and then unwrap.
- Validate boundary payloads with Pydantic (`model_validate`, `model_validate_json`) instead of passing unchecked dicts deeper into the package.
- Client contract tests mock `requests.get`, `requests.post`, and `requests.delete` directly, then assert on URL, JSON payload, headers, and typed DTO conversion. Do not introduce live-service dependencies into those tests.
- The auth convention for client methods is `Authorization: Bearer <token>` plus `Temporal-Secret-Key`; ABAC and NGAC helpers reuse `_auth_headers()` for this.
- Creating an `Acl` instance has side effects: it starts an autosave daemon and writes encrypted state to the configured output path. In tests and scripts, use writable `XOLO_OUTPUT_PATH` / `XOLO_LOG_PATH` locations.
- ABAC examples and regression fixtures live in `tests/policies/*.json`. `GraphBuilder.build_event_graph()` writes `exports/event_graph.gexf`, so graph-related changes can update generated artifacts.
- Xolo-CL grammar expects quoted strings for operands and supports optional semicolons plus C++-style and Python-style comments. Keep parser changes aligned with the command classes in `xolo.policies.parser.models`.
