# Python Error Handling Reference

Adapted from Cisco and wshobson; modified for Task Harness on 2026-10-30. See [NOTICE](../NOTICE). Examples are focused fragments; use the project's existing versions, adapters, and test tools.

Use this reference when reviewing or writing validation logic, exceptions, and failure-handling behavior in Python services, scripts, and libraries.

## Core Principles

- Validate early.
- Use specific exception types.
- Preserve error context.
- Model partial failures instead of hiding them.

## Early Input Validation

Validate inputs at the boundary, before expensive work begins.

```python
def process_order(
    order_id: str,
    quantity: int,
    discount_percent: float,
) -> OrderResult:
    if not isinstance(order_id, str) or not order_id:
        raise ValueError("'order_id' is required")

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(f"'quantity' must be positive, got {quantity}")

    if (isinstance(discount_percent, bool)
        or not isinstance(discount_percent, (int, float))
        or not 0 <= discount_percent <= 100):
        raise ValueError(
            f"'discount_percent' must be 0-100, got {discount_percent}"
        )

    return _process_validated_order(order_id, quantity, discount_percent)
```

Type annotations do not enforce runtime types. Validate before I/O, preserve missing versus null versus zero, and avoid silently coercing `true`, `"1"` or `1.0` into a strict integer. The bounded comparison rejects non-finite floats too.

## Convert To Domain Types At Boundaries

Parse raw strings and untrusted data into typed domain values early.

```python
from enum import Enum


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"


def parse_output_format(value: str) -> OutputFormat:
    if not isinstance(value, str):
        raise TypeError("Output format must be a string")
    try:
        return OutputFormat(value.lower())
    except ValueError as exc:
        valid_formats = [fmt.value for fmt in OutputFormat]
        raise ValueError(
            f"Invalid format '{value}'. Valid options: {', '.join(valid_formats)}"
        ) from exc
```

## Pydantic For Structured Validation

For complex request bodies or config, the existing validation library may simplify boundary checks. This example uses Pydantic v2; use the installed version and do not add or upgrade it just to follow the example. Normalize only when the product contract permits it; case folding an identifier or name can change its meaning.

```python
from pydantic import BaseModel, Field, ValidationError, field_validator


class CreateUserInput(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(strict=True, ge=0, le=150)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("Invalid email format")
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name must contain non-whitespace characters")
        return value
```

The email validator is deliberately simplified and does not establish standards compliance. Prefer the project's established email contract. Public error responses must omit credentials, raw request/response bodies and internal paths; preserve safe context and causes in the internal diagnostic path.

## Use Standard Exceptions Intentionally

Map common failures to familiar built-in exceptions where possible:

- `ValueError` for invalid values
- `TypeError` for wrong input types
- `KeyError` for missing keys
- `RuntimeError` for operational failures
- `TimeoutError` for timeouts
- `FileNotFoundError` for missing paths
- `PermissionError` for access failures

Avoid vague `Exception("something went wrong")` style errors.

## Custom Exception Hierarchies

Create domain-specific exceptions when the caller needs structured semantics.

```python
class ApiError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.request_id = request_id
        super().__init__(message)


class RateLimitError(ApiError):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Rate limit exceeded. Retry after {retry_after}s",
            status_code=429,
        )
```

## Exception Chaining

Preserve the original failure when translating exceptions across layers.

```python
import httpx


class ServiceError(Exception):
    pass


def upload_file(path: str) -> str:
    try:
        with open(path, "rb") as handle:
            response = httpx.post("https://upload.example.com", files={"file": handle}, timeout=10.0)
            response.raise_for_status()
            return response.json()["url"]
    except FileNotFoundError as exc:
        raise ServiceError(f"Upload failed: file not found at '{path}'") from exc
    except httpx.HTTPStatusError as exc:
        raise ServiceError(
            f"Upload failed: server returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ServiceError("Upload failed: network error") from exc
```

### Narrow Exception Boundaries

```python
import json


def parse_and_compute(raw: str):
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidInputError("Malformed JSON") from exc
    return compute(payload)
```

`InvalidInputError` is a domain exception. Keep `compute` outside the parsing catch so an internal `ValueError` does not become a false invalid-JSON diagnosis. Translate only errors the boundary understands; preserve unexpected failures for diagnosis. Log a failure at the responsible boundary with a correlation ID, operation and safe cause, avoiding duplicate stack traces at every layer. Never change a business failure into success because logging succeeded, or a committed success into failure because optional logging failed.

## Batch Processing With Partial Failures

Choose atomicity first. The following pattern applies only to independent items with an explicit partial-success contract. For all-or-nothing work, use a transaction and report the whole operation as failed. `RecoverableItemError` below is the project's classified per-item exception; unexpected programming errors still propagate.

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class BatchResult(Generic[T]):
    succeeded: dict[int, T]
    failed: dict[int, Exception]

    @property
    def success_count(self) -> int:
        return len(self.succeeded)

    @property
    def failure_count(self) -> int:
        return len(self.failed)


def process_batch(items: list[Item]) -> BatchResult[ProcessedItem]:
    succeeded: dict[int, ProcessedItem] = {}
    failed: dict[int, Exception] = {}

    for idx, item in enumerate(items):
        try:
            succeeded[idx] = process_single_item(item)
        except RecoverableItemError as exc:
            failed[idx] = exc

    return BatchResult(succeeded=succeeded, failed=failed)
```

If failures are user-visible or operationally meaningful, surface counts, identities, and reasons clearly.

## Progress Reporting For Long Operations

Long-running batch work often needs progress updates without coupling domain logic to UI code.

```python
from collections.abc import Callable


ProgressCallback = Callable[[int, int, str], None]


def process_large_batch(
    items: list[Item],
    on_progress: ProgressCallback | None = None,
) -> BatchResult:
    total = len(items)
    succeeded = {}
    failed = {}

    for idx, item in enumerate(items):
        if on_progress:
            on_progress(idx, total, f"Processing {item.id}")

        try:
            succeeded[idx] = process_single_item(item)
        except RecoverableItemError as exc:
            failed[idx] = exc

    if on_progress:
        on_progress(total, total, "Complete")

    return BatchResult(succeeded=succeeded, failed=failed)
```

“Complete” means all items were attempted, not that all succeeded. Return success/failure counts and preserve item identities. Define callback failure behavior: optional progress/logging failures should not erase committed outcomes, while required audit failures may have a stricter contract. Do not catch cancellation or unexpected defects as recoverable item failures.

## Error-Handling Checklist

- Inputs are validated at boundaries
- Raw data is converted to domain types early
- Pydantic or equivalent validation is used for structured payloads where helpful
- Exceptions are specific and include actionable context
- Lower-level exceptions are chained when translated
- Batch operations model partial success and failure explicitly
- Long operations can report progress without tangling UI with business logic
- Tests cover failure paths, not just successful execution


## Sources

- [Cisco source at the adapted revision](https://github.com/cisco-open/ai-harness-toolkit/blob/32be69856336795ecb03366820a34a361a9ea6a2/skills/python-best-practices/references/error-handling.md)
