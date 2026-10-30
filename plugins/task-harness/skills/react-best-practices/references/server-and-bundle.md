# React Server Boundaries And Bundle Reference

Condensed and adapted for Task Harness on 2026-10-30. See [NOTICE](../NOTICE) for source, license and selected rule groups. Examples are focused fragments, not a new application scaffold.

Use the server sections only for an application with a server framework, especially Next.js App Router and React Server Components. A plain React SPA does not need Server Actions, RSC or a Next.js migration. Bundle guidance applies through the project's existing bundler and supported public package APIs.

## Treat Every Server Entry As An Access Boundary

### Authenticate And Authorize Mutations

```tsx
'use server';

// BAD: a client can supply someone else's owner ID.
export async function deleteRecordBad(id: string, ownerId: string) {
  await db.record.deleteMany({ where: { id, ownerId } });
}

// GOOD fragment: actor comes from a trusted session, not the payload.
export async function deleteRecord(rawId: unknown) {
  const actor = await requireUser();
  const id = parseRecordId(rawId);
  const result = await db.record.deleteMany({
    where: { id, ownerId: actor.id },
  });
  return { deleted: result.count > 0 };
}
```

The example returns the same false outcome for absent and inaccessible records; choose the actual response contract deliberately. `parseRecordId` is runtime validation, not a TypeScript assertion. `requireUser` verifies the current session. The mutation itself includes the permission predicate so a separate earlier check cannot drift from the write. More complex permissions may need a transaction or the project's established authorized data layer.

A `'use server'` directive, hidden button or authenticated layout does not protect the action by itself. Recheck access at each action, route handler or equivalent public entry. Test direct invocation, expired sessions, forged IDs and cross-user access. Preserve the framework's supported CSRF and origin protections. Do not turn a client-supplied role or owner ID into proof of permission.

### Keep Request Identity Out Of Shared Mutable State

```tsx
// BAD: requests can interleave across await while sharing this module.
let currentUser: User | null = null;
async function handler() {
  currentUser = await requireUser();
  await prepareResponse();
  return loadPrivateData(currentUser.id);
}

// GOOD: identity belongs to this invocation.
async function handlerScoped() {
  const actor = await requireUser();
  await prepareResponse();
  return loadPrivateData(actor.id);
}
```

Do not assume serverless or a single process means one request at a time. A module may survive and serve overlapping requests. Pass request-specific values explicitly or use the framework's documented request context. Globals are acceptable for intentionally shared immutable configuration or properly managed client pools, not a mutable “current user”.

## Cache With An Explicit Scope

### Deduplicate Within An RSC Request

```tsx
import { cache } from 'react';

// Server Components only. Call the same exported memoized function.
export const getUserForRender = cache(async (userId: string) => {
  return db.user.findUnique({ where: { id: userId } });
});
```

React `cache` here memoizes work in the supported Server Component render context, with cache invalidation per server request. It is not a generic process cache for route handlers or a client cache. Use a stable shared function and primitive arguments where practical; fresh object arguments do not share identity. Errors may also be cached for the same arguments. Access control still applies before returning private data.

### Treat Cross-Request Caching As A Separate Decision

A process-level Map, LRU cache or framework data cache can outlive the request. Specify key inputs, TTL, size bound, invalidation after writes and what happens on permission/session changes. Personalized responses require correct user/tenant and permission scope, or should not be shared at all. A TTL alone does not prevent cross-user leakage.

Do not add a global cache just to make repeated calls fast. First check whether request deduplication solves the actual problem. Long-lived caches consume memory, can become stale and behave differently across workers or instances. Confirm the installed framework's caching defaults rather than copying defaults from a different release.

## Minimize The Server-To-Client Contract

```tsx
// BAD: every serializable database field can cross the boundary.
return <ProfileEditor user={databaseUser} />;

// GOOD: an explicit allowlist for this UI.
const profile = {
  id: databaseUser.id,
  displayName: databaseUser.displayName,
};
return <ProfileEditor profile={profile} />;
```

Only pass fields the client needs, using types supported by the installed framework's serialization contract. Do not spread the full object into the DTO. Check actual response/RSC payloads for representative private fields, not only what the page visibly renders. Avoid passing redundant large arrays or repeatedly derived copies across the boundary.

Keep credentials, privileged database clients and server-only modules out of client imports. In a Next project use its server-only boundary convention where appropriate. Put `'use client'` at the smallest useful interactive boundary; do not mark the entire route client-side just to host a button. Conversely, keep browser-only APIs out of server render paths. A static type check does not prove that secrets are absent from a bundle.

## Reduce Initial Code At Real Loading Boundaries

### Load Rare Heavy UI On Demand

```tsx
import { lazy, Suspense, useState } from 'react';

const Editor = lazy(() => import('./Editor')); // Module exports default component.

function EditorLauncher() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>Open editor</button>
      {open && (
        <EditorErrorBoundary>
          <Suspense fallback={<p role="status">Loading editor…</p>}>
            <Editor onClose={() => setOpen(false)} />
          </Suspense>
        </EditorErrorBoundary>
      )}
    </>
  );
}
```

`EditorErrorBoundary` is the application's error boundary, including a usable recovery path for a failed chunk load. The editor must preserve dialog labeling, keyboard behavior and focus return. Declare `lazy` at module scope to keep component identity stable. Confirm no other eager import pulls the same heavy module back into the entry chunk.

Resetting an error boundary alone may encounter the same cached rejected lazy import. Verify recovery using the framework's supported mechanism or an explicit reload that preserves unsaved work; do not promise that a generic Retry button re-downloads the chunk.

In Next.js, use its supported dynamic import integration when SSR/loading requirements call for it. Do not disable SSR globally or use `ssr: false` as a default fix for browser-only code; check where that option is supported and isolate the actual browser dependency. Preload on likely user intent only when it benefits measured latency without imposing the download on everyone.

### Avoid Unnecessary Package Work

Import from a documented public entry or subpath that lets the bundler exclude unused code. Inspect the production build before replacing every barrel import: package export maps, tree shaking, side-effect flags and framework optimizations affect the result. An undocumented internal `dist/` path can break on upgrade and is not a stable optimization.

```tsx
// Choose only if the package documents this public subpath.
import SearchIcon from 'icon-library/SearchIcon';
```

This illustrative package name is not an installation instruction. Use the actual installed package's API and build output. Do not sacrifice types or add unsafe casts to make a private import compile.

### Delay Nonessential Third-Party Work

Load optional analytics, feedback widgets or a rare heavy library after the critical interaction when product and consent requirements permit. Use the framework's supported script strategy rather than ad hoc DOM injection. “Nonessential” depends on the flow: delaying required error capture, authentication or integrity checks can remove needed evidence or break behavior.

A dynamically imported module still needs failure handling and a lifecycle. Prevent duplicated initialization, clean up subscriptions, and decide whether repeated opening should reuse the instance or recreate it. Do not promise a bundle reduction from source syntax alone; verify the emitted chunks and network requests.

## Verification Checklist

- Direct server mutations authenticate, validate and enforce permissions at the write boundary.
- Interleaved users cannot exchange request identity or private cached data.
- Cache lifetime, keys, bounds and invalidation are explicit.
- Client payloads and bundles contain only intended public fields and modules.
- Rare heavy UI actually loads on demand and handles chunk failure accessibly.
- Imports use supported package APIs and existing build configuration.
- Bundle/request measurements use comparable production builds and inputs.

## Sources

- [Vercel React best practices at the adapted revision](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices)
- [React cache](https://react.dev/reference/react/cache)
- [Next.js authentication and authorization](https://nextjs.org/docs/app/guides/authentication)
