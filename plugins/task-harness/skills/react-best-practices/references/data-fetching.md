# React Data Fetching Reference

Condensed and adapted for Task Harness on 2026-10-30. See [NOTICE](../NOTICE) for source, license and selected rule groups. Examples are focused fragments, not a new application scaffold.

Use this reference for request waterfalls, async loading, client request ownership, and stale responses. Start with the project's existing router or data layer. Framework loaders, Server Components, cache libraries and Effects have different lifetimes; choose the guidance that matches the application.

## Remove Independent Request Waterfalls

### Start Independent Work Together

```tsx
// BAD: catalog unnecessarily waits for profile.
const profile = await loadProfile();
const catalog = await loadCatalog();

// GOOD when both results are required and independent.
const [profile, catalog] = await Promise.all([
  loadProfile(),
  loadCatalog(),
]);
```

Independence includes authorization, rate limits and mutation order, not just separate function names. A request that needs the profile's account ID cannot start first. Do not parallelize two writes whose ordering is part of the business contract.

`Promise.all` rejects when one input rejects; it does not cancel other requests. Decide whether the operation is all-or-nothing, whether remaining work should be aborted, and who consumes any results. For independently useful panels, model separate error states or use `Promise.allSettled` with explicit handling of every rejected result. Do not silently render a failed result as an empty collection.

### Start Work When Its Inputs Are Available

```tsx
// Both profile and catalog need a trusted actor; prices also need catalog IDs.
async function loadPageData() {
  const actor = await requireUser();
  const profilePromise = loadProfile(actor.id);
  const catalogPromise = loadCatalog(actor.accountId);
  const pricedCatalogPromise = catalogPromise.then(async catalog => ({
    catalog,
    prices: await loadPrices(catalog.map(item => item.id)),
  }));
  const [profile, pricedCatalog] = await Promise.all([
    profilePromise,
    pricedCatalogPromise,
  ]);
  return { profile, ...pricedCatalog };
}
```

This fragment assumes authentication applies to every read and these reads may run concurrently. A `then` chain lets dependent work start without waiting for unrelated work. Keep error handling at the owning boundary and avoid creating promises that a later early return leaves unobserved.

### Defer Work Behind Cheap Branches

```tsx
async function getPreview(enabled: boolean) {
  if (!enabled) return { enabled: false as const };
  const actor = await requireUser();
  const preview = await loadPreviewFor(actor.id);
  return { enabled: true as const, preview };
}
```

Skip work only when the branch is valid without it. Preserve authentication and authorization before protected reads or mutations, and avoid leaking a private resource's existence through differently ordered errors. “Await late” does not authorize starting sensitive work before access checks.

## Assign One Owner To Client Data

Prefer the established router loader or cache when it already provides request deduplication, invalidation, cancellation and error handling. Do not add SWR or React Query solely because an example uses it; a small Effect can be sufficient for a local screen. Conversely, do not build a custom global cache to avoid a dependency when the project's chosen library already handles the needed lifecycle.

A request key must include every input that changes the response: query, filters, page, locale and relevant account context. Define how authentication changes invalidate cached data. UI deduplication is not a guarantee against duplicated server mutations. Cache freshness and permission correctness are separate concerns.

```tsx
// With an existing SWR setup; fetcher checks HTTP errors and payload shape.
function Catalog({ accountId, query }: { accountId: string; query: string }) {
  const key = `/api/catalog?${new URLSearchParams({ accountId, query })}`;
  const { data, error, isLoading } = useSWR(key, fetchCatalog);
  if (isLoading) return <p role="status">Loading catalog…</p>;
  if (error) return <p role="alert">Catalog could not be loaded.</p>;
  return <CatalogRows rows={data ?? []} />;
}
```

This example does not make the client-supplied account ID trusted. The server still authorizes access. Do not share personalized cache entries across users without an explicit, safe identity and invalidation design.

## Effects Must Reject Obsolete Results

Use an Effect for synchronization with an external system when the existing data layer does not own that request. Every reactive input read by the Effect belongs in its dependency list. Do not suppress the dependency lint rule to keep a request from running again.

```tsx
type Row = { id: string; label: string };
type SearchState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; rows: Row[] };

function useSearch(query: string) {
  const [state, setState] = useState<SearchState>({ status: 'loading' });
  useEffect(() => {
    const controller = new AbortController();
    let obsolete = false;
    setState({ status: 'loading' });

    async function load() {
      try {
        const params = new URLSearchParams({ q: query });
        const response = await fetch(`/api/search?${params}`, {
          signal: controller.signal,
        });
        if (!response.ok) throw new Error(`Search failed: ${response.status}`);
        const rows = parseRows(await response.json());
        if (!obsolete) setState({ status: 'ready', rows });
      } catch (error) {
        if (!obsolete) setState({ status: 'error', message: 'Search failed. Retry.' });
      }
    }
    void load();
    return () => {
      obsolete = true;
      controller.abort();
    };
  }, [query]);
  return state;
}
```

`parseRows` is the project's runtime payload validator; a TypeScript cast does not validate JSON. The example replaces old rows while loading. If the product retains previous results instead, label them as stale and associate them with their source query. Do not present old rows as the completed answer to a new query.

Cancellation reduces unnecessary work, while the obsolete flag prevents a resolved or non-abortable request from overwriting newer state. Test the exact race: start A, change to B, resolve B, then resolve A. Only B should remain. A network request being aborted does not prove that a server-side mutation was undone.

## Stream Only Where The Framework Supports It

In a React Server Components application, independent slow sections can have separate Suspense boundaries so the shell and fast content are not held behind the slowest fetch. Move the await into the component that needs the data rather than awaiting everything at the top before returning any UI.

```tsx
// Server Component fragment, not a plain client SPA recipe.
function Page() {
  return (
    <main>
      <h1>Overview</h1>
      <Suspense fallback={<SummarySkeleton />}><Summary /></Suspense>
      <Suspense fallback={<ActivitySkeleton />}><Activity /></Suspense>
    </main>
  );
}

async function Summary() {
  const summary = await loadAuthorizedSummary();
  return <SummaryView summary={summary} />;
}
```

Suspense does not turn an arbitrary Effect fetch into a suspending data source. Use the installed framework's supported integration. A fallback handles waiting; failures also need an error boundary or the framework's error route. Avoid blank or shifting placeholders, and consider whether streamed sections need a shared consistent snapshot. Preserve the user's draft when a neighboring section refreshes.

## Verification Checklist

- Independent requests start before either completes; dependencies keep their ordering.
- Protected work is still authenticated and authorized.
- Each failed request has an explicit outcome; all-or-nothing versus partial display is intentional.
- Rapid query changes cannot let an old response win, including after unmount.
- HTTP errors, malformed data, empty success and loading are distinct.
- Cache keys and invalidation reflect response inputs and user changes.
- Performance claims include a comparable trace or timing, not a fixed speedup estimate.

## Sources

- [Vercel React best practices at the adapted revision](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices)
