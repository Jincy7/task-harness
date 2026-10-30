# React Rendering And State Reference

Condensed and adapted for Task Harness on 2026-10-30. See [NOTICE](../NOTICE) for source, license and selected rule groups. Examples are focused fragments, not a new application scaffold.

Use this reference for state ownership, Effects, list identity and measured rendering work. Correctness comes first: a memoized stale result is still wrong. Confirm the React version, Compiler configuration and existing lint rules before choosing an optimization.

## Keep State Minimal And Owned

### Derive Values During Render

```tsx
// BAD: two sources of truth and an extra render after every item change.
const [total, setTotal] = useState(0);
useEffect(() => {
  setTotal(items.reduce((sum, item) => sum + item.price, 0));
}, [items]);

// GOOD: a cheap derived value stays in sync with its source.
const total = items.reduce((sum, item) => sum + item.price, 0);
```

Store user choices and external results; derive filtered lists, counts and labels from them. Do not copy props into state without an explicit draft/reset contract. An editable draft legitimately differs from server data, so decide when it initializes, saves, cancels or resets. Refetching data should not automatically erase unsaved input.

Keep state near its consumers. Lift it to the smallest shared owner when multiple components must agree. A global store is useful for genuinely shared state, not a default home for every input. Subscribe to the value needed for rendering rather than an entire frequently changing store object when the existing library supports selectors.

### Use Functional Updates For Previous State

```tsx
// BAD: successive updates can use the same captured count.
setCount(count + 1);
setCount(count + 1);

// GOOD when each update depends on the previous value.
setCount(previous => previous + 1);
setCount(previous => previous + 1);
```

Updater functions must remain pure: no network calls, logs with business side effects, or mutations of previous state. Development checks may invoke them more than once. Use a lazy initializer for expensive initial state when useful, but do not put side-effecting work in it.

```tsx
const [selection, setSelection] = useState(() => buildInitialSelection(items));
setSelection(previous => ({ ...previous, [id]: true }));
```

This initializes once per mount. Later prop changes need a defined update/reset policy; an initializer is not ongoing synchronization. Keep SSR initial output deterministic when server rendering is in use.

### Do Not Mutate Inputs While Deriving

```tsx
// BAD: changes the array owned by props or a cache.
const sorted = rows.sort(compareRows);

// GOOD across environments without Array.prototype.toSorted support.
const sorted = [...rows].sort(compareRows);
```

Use immutable updates for the changed path without cloning the whole application state. Select `toSorted` only when the project's runtime and tooling support it. A copy preserves ownership; it does not solve the cost of repeatedly sorting a very large list. Measure before adding caching or changing the data model.

## Preserve Component Identity

### Stable Keys Belong To Entities

```tsx
// BAD for editable, reordered, inserted or filtered rows.
rows.map((row, index) => <EditableRow key={index} row={row} />);

// GOOD: identity survives a change in position.
rows.map(row => <EditableRow key={row.id} row={row} />);
```

Random keys force remounts and lose local state. Index keys are only suitable when positions truly are stable and identity is positional; do not use them for editable records. Keys need to be stable and unique among siblings, not globally unique.

### Define Components Outside Their Parent

```tsx
// BAD: a new component type is created on each Parent render.
function Parent() {
  function Editor() { return <input defaultValue="draft" />; }
  return <Editor />;
}

// GOOD: stable component type; data flows through props.
function Editor({ initialValue }: { initialValue: string }) {
  return <input defaultValue={initialValue} />;
}
function Parent() {
  return <Editor initialValue="draft" />;
}
```

A helper function that returns JSX is not automatically a component identity bug; inspect how it is invoked. Test focus, selection and draft preservation after a parent update, filtering and reordering. Do not add keys to force resets unless resetting is the intended product behavior.

## Effects Synchronize External Systems

Call ordinary Hooks at the top level of function components or custom Hooks, before conditional returns, so their order stays stable. Do not call them in branches, loops or event handlers. React's `use` API has different rules where the installed version supports it; that exception does not apply to arbitrary Hooks or functions whose names begin with `use`.

Effects are for subscriptions, timers, requests or imperative widgets. Calculations belong in render; actions caused by a user interaction usually belong in that event handler. Do not chain state-setting Effects to orchestrate a business workflow.

```tsx
// GOOD: a user action directly owns the mutation.
async function handleSave() {
  setSaveState('pending');
  try {
    await saveDraft(draft);
    setSaveState('saved');
  } catch {
    setSaveState('error');
  }
}
```

Do not trigger the save through an Effect watching `shouldSave`: remounts and dependency changes make the intent harder to establish. Preserve draft state on failure. Server-side uniqueness or idempotency is still required when repeating this operation could cause harm.

### Dependencies And Cleanup Match Ownership

```tsx
function useConnection(roomId: string) {
  useEffect(() => {
    const connection = connectToRoom(roomId);
    connection.open();
    return () => connection.close();
  }, [roomId]);
}
```

List every reactive dependency used by the Effect. If an object exists only to configure the resource, construct it inside the Effect instead of making a fresh object dependency on every render. Do not remove dependencies, put visible data in a ref, or use a deep comparison hook just to silence the linter. Use the least complicated design that expresses when the resource should change.

Cleanup must release the specific subscription, listener, timer or request owned by that Effect. Validate setup → cleanup → setup behavior, including development Strict Mode. A borrowed shared resource may require unsubscribing rather than closing it globally. See [data fetching](data-fetching.md) for request races.

## Optimize A Demonstrated Cost

### Profile Before Adding Memoization

Use a representative interaction and list size. Identify what re-renders, why, and which work is expensive using the project's React profiling tools or browser performance trace. An inexpensive extra render can be cheaper than a complex comparison or cache.

`memo`, `useMemo` and `useCallback` are performance tools, not correctness guarantees. Confirm whether React Compiler already handles the relevant case. Do not blanket-wrap every component or callback. Stable callbacks help only when identity is observed by a dependency or a memoized consumer.

```tsx
// Candidate only when filtering is measurably expensive.
const visibleRows = useMemo(
  () => rows.filter(row => matchesQuery(row, query)),
  [rows, query],
);
```

`matchesQuery` here is a stable module-level pure function. Keep every reactive input in the dependencies. Never rely on the memo cache for storing a draft, resource or business outcome. A custom `memo` comparison must consider every behavior-affecting prop, including callbacks and the state they capture; a missed function prop can preserve stale behavior. Deep equality over unbounded data can cost more than rendering.

### Separate Immediate Input From Expensive Display

```tsx
const [query, setQuery] = useState('');
const deferredQuery = useDeferredValue(query);
const isStale = query !== deferredQuery;
return (
  <>
    <label>Search <input value={query} onChange={e => setQuery(e.target.value)} /></label>
    <div aria-busy={isStale}><ExpensiveResults query={deferredQuery} /></div>
  </>
);
```

Keep the controlled input update immediate. Deferring a rendered value or using a transition for non-urgent view changes can help responsiveness when supported by the installed React version. It does not make computation faster or automatically debounce network requests. The expensive subtree may also need a measured memo boundary; test that it can skip unchanged work. Clearly signal stale results if users could act on them.

Use refs for transient values that do not determine visible output, such as a timer handle. If a value must update the screen, state or an external-store subscription is the appropriate mechanism. For huge lists, first reduce unnecessary work; consider pagination or the project's existing virtualization only when measured size and interaction justify it. Verify keyboard navigation and focus when rows unmount.

## Review Checklist

- Derived data is not duplicated in synchronized state.
- Draft ownership and reset rules are explicit.
- Updates are pure and use the previous value when required.
- Keys and component types preserve the right identity.
- Effects own external synchronization, dependencies and cleanup.
- Correctness does not depend on memoization.
- Expensive updates preserve responsive input and visible loading/stale states.
- Before/after evidence supports any claimed performance improvement.

## Sources

- [Vercel React best practices at the adapted revision](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices)
- [React useEffect](https://react.dev/reference/react/useEffect)
- [React memo](https://react.dev/reference/react/memo)
