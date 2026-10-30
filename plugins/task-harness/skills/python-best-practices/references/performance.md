# Python Performance Reference

Adapted from Cisco and wshobson; modified for Task Harness on 2026-10-30. See [NOTICE](../NOTICE). Examples are focused fragments; use the project's existing versions, adapters, and test tools.

Use this reference when Python code is slow, memory-heavy, async-sensitive, or likely to sit on a hot path. Profile first, then optimize the measured bottleneck.

## Profiling Tools

Use a representative input size and record Python version, hardware, warm/cold state, elapsed time and peak memory as relevant. Standard-library profiling is a starting point; the optional tools below are not installation requirements. Check tool/platform support and avoid recording sensitive inputs.

### `cProfile` For CPU Profiling

```python
import cProfile
import pstats
from pstats import SortKey


def slow_function():
    total = 0
    for i in range(1_000_000):
        total += i
    return total


def another_function():
    return [i**2 for i in range(100_000)]


def main():
    result1 = slow_function()
    result2 = another_function()
    return result1, result2


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(10)
    stats.dump_stats("profile_output.prof")
```

Command-line usage:

```bash
python -m cProfile -o output.prof script.py
python -m pstats output.prof
```

### `line_profiler` For Line-Level Hotspots

```python
@profile
def process_data(data):
    result = []
    for item in data:
        processed = item * 2
        result.append(processed)
    return result


if __name__ == "__main__":
    process_data(range(100_000))
```

Run with `kernprof -l -v script.py`.

### `memory_profiler` For Allocation Pressure

```python
from memory_profiler import profile


@profile
def memory_intensive():
    big_list = [i for i in range(1_000_000)]
    big_dict = {i: i**2 for i in range(100_000)}
    return sum(big_list)


if __name__ == "__main__":
    memory_intensive()
```

Run with `python -m memory_profiler script.py`.

### `py-spy` For Sampling

```bash
py-spy top --pid 12345
py-spy record -o profile.svg --pid 12345
py-spy record -o profile.svg -- python script.py
py-spy dump --pid 12345
```

Profiling a running process requires appropriate access and can affect latency or expose stack data. Start in a reproducible local environment; do not infer production safety from the sampling tool alone.

## Optimization Patterns

### Prefer Comprehensions Over Manual Append Loops

```python
def slow_squares(n):
    result = []
    for i in range(n):
        result.append(i**2)
    return result


def fast_squares(n):
    return [i**2 for i in range(n)]
```

### Prefer Generators For Large Streaming Work

```python
def list_approach():
    data = [i**2 for i in range(1_000_000)]
    return sum(data)


def generator_approach():
    data = (i**2 for i in range(1_000_000))
    return sum(data)
```

Generators reduce peak memory when you do not need the entire intermediate collection.

### Use `"".join(...)` For Repeated String Building

```python
def slow_concat(items):
    result = ""
    for item in items:
        result += str(item)
    return result


def fast_concat(items):
    return "".join(str(item) for item in items)
```

### Prefer Dict And Set Lookups Over Repeated Linear Searches

```python
items = list(range(10_000))
lookup_dict = {i: i for i in range(10_000)}


def list_search(target):
    return target in items


def dict_search(target):
    return target in lookup_dict
```

Use the right data structure before reaching for micro-optimizations.

### Keep Hot Values Local On Tight Loops

```python
GLOBAL_VALUE = 100


def use_global():
    total = 0
    for _ in range(10_000):
        total += GLOBAL_VALUE
    return total


def use_local():
    local_value = 100
    total = 0
    for _ in range(10_000):
        total += local_value
    return total
```

This is only a candidate for measured hot loops. Interpreter optimizations differ by version; keep readable code unless a repeatable workload shows a worthwhile gain. Names such as `fast_squares` describe the example, not a measured guarantee.

## Async Performance Trap

One of the highest-impact Python performance mistakes is putting blocking work inside `async def` code.

```python
# BAD: blocks the event loop and stalls unrelated work
async def fetch_data():
    time.sleep(1)
    response = requests.get(url)
    return response.json()
```

Use async-native clients, awaitable sleeps, or offload blocking work intentionally.

```python
# GOOD
async def fetch_data():
    await asyncio.sleep(1)
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

Also watch for hidden blockers inside async flows:

- synchronous ORM calls
- heavy CPU work in request handlers
- filesystem work in tight async request paths
- libraries that expose async wrappers but still block internally

### Bounded Concurrency And Cancellation

Do not create one task per item for an unbounded stream. A semaphore limits active I/O but does not limit the memory of millions of queued tasks. Use bounded chunks or a fixed worker pool and a bounded queue; choose concurrency from upstream limits and measured workload.

For a small bounded set, gather independent work together. For dependent operations, preserve order and transaction semantics. `asyncio.gather` does not automatically cancel sibling tasks on the first exception; explicitly await/clean them up when required. Python 3.11 `TaskGroup` is an option only when the project supports it, not a Python 3.10 default.

```python
import asyncio
import requests


def fetch_sync(url: str) -> dict:
    response = requests.get(url, timeout=(3, 10))
    response.raise_for_status()
    return response.json()


async def fetch_via_existing_sync_client(url: str) -> dict:
    return await asyncio.to_thread(fetch_sync, url)
```

`to_thread` can adapt blocking I/O when replacing the client is not justified. Cancelling the await does not stop a running thread, so underlying network timeouts and bounded workers remain essential. Threads are not a general CPU speedup for Python code; choose processes or another measured approach only when the workload justifies the overhead. Do not swallow cancellation as an ordinary retryable failure.

Background tasks need an owner that retains strong references, collects failures, and cancels or awaits them on shutdown. Do not fire and forget a task whose failure or unfinished write affects the operation's outcome.

### Streaming And Memory Contracts

A generator saves memory only if downstream code consumes it incrementally. Check for hidden `list(...)`, sorting, grouped accumulation, duplicate buffers, and database clients that fetch all rows. Preserve ordering and error reporting when streaming; a failure after partial output is a different contract from an atomic response.

## Review Guidance

- Measure before changing algorithms or structure.
- Focus on hot paths, large collections, repeated I/O, and repeated allocations.
- Prefer built-in operations and standard-library primitives before custom cleverness.
- Check algorithmic complexity before micro-tuning syntax.
- Treat memory pressure and latency as separate concerns; a fix for one can hurt the other.
- In async code, verify that the full path is non-blocking, not just the top-level function signature.

## Performance Checklist

- Profile with `cProfile`, `line_profiler`, `memory_profiler`, or `py-spy`
- Optimize the measured bottleneck, not guessed bottlenecks
- Prefer comprehensions, generators, and appropriate data structures
- Avoid repeated string concatenation in loops
- Reduce unnecessary copies and redundant work
- Avoid blocking calls inside `async def`
- Re-check performance after each meaningful change


## Sources

- [Cisco source at the adapted revision](https://github.com/cisco-open/ai-harness-toolkit/blob/32be69856336795ecb03366820a34a361a9ea6a2/skills/python-best-practices/references/performance.md)
