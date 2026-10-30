# Python Anti-Patterns Reference

Adapted from Cisco and wshobson; modified for Task Harness on 2026-10-30. See [NOTICE](../NOTICE). Examples are focused fragments; use the project's existing versions, adapters, and test tools.

Use this reference when reviewing Python code for maintainability, architecture, reliability, and test-quality issues that are easy to miss during implementation.

## Infrastructure Anti-Patterns

### Scattered Timeout And Retry Logic

```python
# BAD: timeout and retry behavior duplicated at call sites
def fetch_user(user_id: str):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching user")
        return None


def fetch_orders(user_id: str):
    try:
        return requests.get(url, timeout=30)
    except Timeout:
        logger.warning("Timeout fetching orders")
        return None
```

Centralize this in one client wrapper, decorator, or service boundary so behavior is consistent and tunable.

```python
# GOOD: one place owns retry and timeout behavior
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential
import requests


# Optional Tenacity example for an idempotent read; three total attempts.
@retry(
    retry=retry_if_exception_type((requests.Timeout, requests.ConnectionError)),
    stop=stop_after_attempt(3),
    wait=wait_random_exponential(multiplier=0.5, max=4),
    reraise=True,
)
def http_get(url: str) -> requests.Response:
    response = requests.get(url, timeout=(3, 10))
    response.raise_for_status()
    return response
```

The timeout tuple bounds connect and read inactivity, not the full operation deadline. Bound the overall retry duration too when the caller has a deadline. Do not retry validation, authentication, programming errors, or cancellation. Retrying writes needs an idempotency contract and an outcome check. Tenacity is optional; reuse an existing client policy when it meets the contract.

### Double Retry

```python
# BAD: retries happen in more than one layer
@retry(stop=stop_after_attempt(3))
def call_service():
    return client.request()
```

Retry in one layer only. If the HTTP client, SDK, queue, or infrastructure already retries, avoid wrapping it in another retry loop unless there is a deliberate policy.

Check whether SDK settings mean total attempts or retries after the first attempt. Two layers of three total attempts can make nine transport calls; two layers of three retries can make sixteen. Test actual calls and total delay.

### Hard-Coded Configuration

```python
# BAD: config and secrets live in source code
DB_HOST = "prod-db.example.com"
API_KEY = "sk-12345"


def connect():
    return psycopg.connect(f"host={DB_HOST}...")
```

Move configuration to typed settings and keep secrets out of code.

```python
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    api_key: str = Field(alias="API_KEY")


# Instantiate at application startup, not as import-time I/O.
def load_settings() -> Settings:
    return Settings()
```

Typed settings are a choice, not a requirement to install Pydantic. Validate required environment values once at startup, keep errors free of secrets, and use the existing configuration mechanism.

## Architecture Smells

### Exposed Internal Types

```python
# BAD: API returns ORM types directly
@app.get("/users/{id}")
def get_user(id: str) -> UserModel:
    return db.query(UserModel).get(id)
```

Keep persistence models, protobufs, and other internal types behind explicit DTOs or response models.

```python
# GOOD
@app.get("/users/{id}")
def get_user(id: str) -> UserResponse:
    user = db.query(UserModel).get(id)
    return UserResponse(id=user.id, display_name=user.display_name)
```

### Mixed I/O And Business Logic

```python
# BAD: queries and rules are tangled together
def calculate_discount(user_id: str) -> float:
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.query("SELECT * FROM orders WHERE user_id = ?", user_id)
    if len(orders) > 10:
        return 0.15
    return 0.0
```

Push I/O to repositories or adapters. Keep business rules pure when possible.

```python
# GOOD
def calculate_discount(user: User, orders: list[Order]) -> float:
    if len(orders) > 10:
        return 0.15
    return 0.0
```

### Persistence Boundaries

Bind SQL parameters instead of formatting user input into SQL. Keep writes that form one business operation inside one transaction; verify rollback after a mid-operation failure. Do not replace missing, null, or zero values with one another. Use an explicit DTO allowlist when data crosses a public boundary.

Placeholders bind values, not table names, column names or sort directions. Choose dynamic identifiers and directions from a fixed mapping or allowlist. Reject unsupported sort keys; test a malicious key as well as a supported ordering.

Avoid mutable default arguments and accidental state shared between requests. Make timezone, monetary units, rounding, ordering and tie-breaking part of the business contract; do not change those values through convenient normalization.

Avoid filesystem access, network calls, and database initialization at module import. Put those actions in an entrypoint or an explicitly owned adapter. Small pure functions are sufficient; do not add repository layers that only forward calls.

## Error Handling Mistakes

### Bare Exception Handling

```python
# BAD: hides failures and destroys signal
try:
    process()
except Exception:
    pass
```

Catch specific exceptions and either translate them, log them with context, or re-raise them.

```python
# GOOD: translate only the known parsing failure, not all downstream ValueErrors.
try:
    payload = json.loads(raw_input)
except json.JSONDecodeError as exc:
    raise BadRequestError("Invalid JSON") from exc

result = process(payload)  # Domain and unexpected failures keep their own meaning.
```

### Ignored Partial Failures

```python
# UNSUITABLE when the product explicitly requires independent partial success
def process_batch(items):
    results = []
    for item in items:
        result = process(item)
        results.append(result)
    return results
```

Choose atomic or partial-success behavior from the product contract. For independent items, catch only classified recoverable item errors; unexpected defects must still surface. `RecoverableItemError` below is a project-defined domain exception.

```python
# GOOD
def process_batch(items) -> BatchResult:
    succeeded = {}
    failed = {}
    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process(item)
        except RecoverableItemError as exc:
            failed[idx] = exc
    return BatchResult(succeeded, failed)
```

### Missing Input Validation

```python
# BAD: invalid input fails somewhere deeper and less clearly
def create_user(data: dict):
    return User(**data)
```

Validate at the boundary and fail early with a clear error.

```python
# GOOD
def create_user(data: dict) -> User:
    validated = CreateUserInput.model_validate(data)
    return User.from_input(validated)
```

## Resource Leaks

### Unclosed Resources

```python
# BAD
def read_file(path):
    handle = open(path)
    return handle.read()
```

Use context managers so cleanup happens on both success and failure.

If cleanup also fails, preserve the original operation failure and report the cleanup failure with safe context. Do not let a `finally` return or a secondary close error silently replace the original outcome.

```python
# GOOD
def read_file(path):
    with open(path) as handle:
        return handle.read()
```

### Transaction Context Is Not Connection Lifetime

`with sqlite3.connect(path) as connection` commits or rolls back a transaction; it does not close the connection. Close resources you own and leave borrowed connections to their owner.

```python
import sqlite3
from contextlib import closing


def save_item(path: str, item_id: str) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("INSERT INTO items(id) VALUES (?)", (item_id,))
```

### Blocking In Async Code

```python
# BAD: blocks the event loop
async def fetch_data():
    time.sleep(1)
    response = requests.get(url)
```

Use async-native APIs in async code paths.

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

Reuse a long-lived client when its lifetime is owned by the service. Do not close an injected client inside a helper. Propagate cancellation and clean up resources in `finally` or context managers. See [performance](performance.md) for bounded concurrency and blocking-library adapters.

## Type Safety Gaps

### Missing Type Hints

```python
# BAD
def process(data):
    return data["value"] * 2
```

Annotate public functions and important internal boundaries. Hints do not validate runtime data: `bool` is an `int` subclass, so a strict integer input needs an explicit bool rejection. See [error handling](error-handling.md).

```python
# GOOD
def process(data: dict[str, int]) -> int:
    return data["value"] * 2
```

### Untyped Collections

```python
# BAD
def get_users() -> list:
    ...
```

Prefer explicit parameterized collection types.

```python
# GOOD
def get_users() -> list[User]:
    ...
```

## Testing Anti-Patterns

### Only Testing Happy Paths

```python
# BAD
def test_create_user():
    user = service.create_user(valid_data)
    assert user.id is not None
```

Cover invalid inputs, edge cases, and behavior under conflict or failure.

```python
# GOOD
def test_create_user_success():
    user = service.create_user(valid_data)
    assert user.id is not None


def test_create_user_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        service.create_user(invalid_email_data)


def test_create_user_duplicate_email():
    service.create_user(valid_data)
    with pytest.raises(ConflictError):
        service.create_user(valid_data)
```

### Over-Mocking

```python
# BAD: the test mostly verifies mocks, not behavior
def test_user_service():
    mock_repo = Mock()
    mock_cache = Mock()
    mock_logger = Mock()
    mock_metrics = Mock()
```

Mock external boundaries, not every collaborator by default. Prefer integration coverage for critical flows.

## Review Checklist

- No scattered retry and timeout logic
- No accidental double retry across layers
- No hard-coded configuration or secrets
- No exposed internal persistence or transport types
- No mixed I/O and business logic where separation would simplify testing
- No bare `except Exception: pass`
- No unmodeled partial failures in batch work
- No missing boundary validation
- No leaked files, sockets, or connections
- No blocking calls in async code paths
- Public functions and collections are typed clearly
- Tests cover error paths, not just happy paths


## Sources

- [Cisco source at the adapted revision](https://github.com/cisco-open/ai-harness-toolkit/blob/32be69856336795ecb03366820a34a361a9ea6a2/skills/python-best-practices/references/anti-patterns.md)
