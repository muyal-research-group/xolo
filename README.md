<div align = center>
<img src='assets/logo.png' width=200/>
</div>
<div align=center>
<a href="https://test.pypi.org/project/mictlanx/"><img src="https://img.shields.io/badge/version-0.0.9--alpha.7-green" alt="build - 0.0.9-alpha.7"></a>
</div>
<div align=center>
	<h1>Xolo: <span style="font-weight:normal;"> An extensible framework for security</span></h1>
</div>


**Xolo** is a secure, modular, and extensible framework for managing access control, licensing, and cryptographic operations in distributed environments. It provides core components for **Attribute-Based Access Control (ABAC)**, **Access Control Lists (ACL)**, **cryptographic license handling**, and **client-server API integration**.

## 📚 Prerequisites

Before using or developing Xolo, ensure the following tools are installed:

- **Python 3.10+**
- **[Poetry](https://python-poetry.org/)** — for dependency management and packaging
- **[Poetry Shell Plugin](https://github.com/python-poetry/poetry-plugin-shell)** (optional, but recommended)


To activate the development environment with Poetry:

```bash
poetry shell
```



## 📦 Installation

This project uses **[Poetry](https://python-poetry.org/)** as the official package manager.

### Install dependencies

```bash
poetry install
```

---

## 🧪 Running Tests

```bash
poetry run pytest tests/
```

---

## 🧰 Module Descriptions

### 🔐 `xolo.abac` – Attribute-Based Access Control

Implements a powerful ABAC engine based on attribute-matching over contextual events. Features include:

- `models`: Defines `Policy`, `Event`, `AccessRequest`, and `AttributeComponent` using Pydantic.
- `communities`: Uses NetworkX and the Louvain algorithm to group related events into communities, improving matching efficiency.
- `graph`: Scores access requests using entropy-weighted matching and selects the best-matching community for evaluation.
- `matcher`: Handles wildcard matching and time range validation.
- `loader`: Loads access requests and policies from JSON files for evaluation pipelines.

This engine allows scalable, expressive authorization logic based on five contextual dimensions: subject, asset, space, time, and action.

---

### 📋 `xolo.acl` – Access Control Lists with Encryption

Provides a persistent ACL engine with support for dynamic permission granting and revocation:

- Role-resource-permission maps
- Fine-grained authorization (`check`, `check_all`, `check_any`)
- `AclDaemon`: Background thread that autosaves encrypted ACLs at defined intervals
- AES-encrypted JSON persistence and secure loading via shared key

---

### 🌐 `xolo.client` – API Client

A typed Python HTTP client for interacting with Xolo-compatible services:

- Authentication (`auth`, `verify`)
- User and scope management (`create_user`, `create_scope`, `assign_scope`)
- License handling (`create_license`, `delete_license`, `self_delete_license`)
- ACL management (`check`, `grantx`, `grants`, `get_resources_by_role`)
- Error-safe `Result` wrapping and DTO-based interfaces for clarity

Includes `interfaces.auth` to model authentication and license responses.

---

### 🪪 `xolo.license` – License Management

Handles license generation and verification via HMAC and expiration timestamps:

- Generates Base32-encoded license keys using SHA256 and a secret key
- Validates expiration time and integrity using constant-time comparison
- Stateless, secure, and compact license format

---

### 📑 `xolo.log` – Structured Logging

Provides a JSON-formatted logger with configurable output:

- `JsonFormatter`: Outputs pretty-printed structured logs with timestamp, thread, and context
- Supports both console and file outputs
- Time-based log rotation
- Optional error logs

Useful for persistent daemons like ACL or production services.

---

### 🧩 `xolo.utils` – Crypto & File Utilities

Contains a broad collection of utility methods:

- Password hashing (PBKDF2) and validation
- AES encryption for raw bytes and file streams
- Streaming-compatible file encryption/decryption
- SHA256 for files, streams, and strings
- X25519 key generation, loading, and serialization
- Random string and password generation

This module underpins many security features in Xolo.

---

## 🏗️ Build & Publish Process (Poetry)

This package uses [Poetry](https://python-poetry.org/) to build and publish releases.

### 1. Bump the version in `pyproject.toml`

```toml
[tool.poetry]
version = "0.0.9-alpha-7"
```

### 2. Build the package

```bash
poetry build
```

This generates `.whl` and `.tar.gz` distributions in the `dist/` folder.

### 3. Publish the package

To PyPI:

```bash
poetry publish --build
```

To TestPyPI:

```bash
poetry publish --build --repository testpypi
```

To configure credentials:

```bash
poetry config pypi-token.pypi your-token-here
```

---

## 📥 Manual Installation from Dist

After building the package, you can manually install it using pip:

```bash
pip install dist/xolo-0.0.9_alpha_7-py3-none-any.whl
# or
pip install dist/xolo-0.0.9-alpha-7.tar.gz
```

---

## 👤 Author

- **Ignacio Castillo**  
  [jesus.castillo.b@cinvestav.mx](mailto:jesus.castillo.b@cinvestav.mx)

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request

Issues, suggestions, and improvements are highly encouraged.

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.


