# React UI Boundaries And Testing Reference

Condensed and adapted for Task Harness on 2026-10-30. See [NOTICE](../NOTICE) for source, license and selected rule groups. Examples are focused fragments, not a new application scaffold.

Use this reference when reviewing forms, asynchronous feedback, accessibility, hydration and user-visible behavior. Vercel's performance guidance is supplemented here with Task Harness's existing correctness and evidence requirements. A faster screen still needs to preserve the user's intent and show failures honestly.

## Model The Whole Interaction

### Distinguish Pending, Empty, Failed And Complete

```tsx
function SearchResults({ state }: { state: SearchState }) {
  if (state.status === 'loading') return <p role="status">Searching…</p>;
  if (state.status === 'error') return <p role="alert">{state.message}</p>;
  if (state.rows.length === 0) return <p>No matching records.</p>;
  return <ul>{state.rows.map(row => <li key={row.id}>{row.label}</li>)}</ul>;
}
```

An empty successful result is different from a rejected request or an invalid payload. Do not convert errors to `[]` merely to simplify rendering. If a screen displays old data while refreshing, label the stale state and preserve the query/version it belongs to. The data state type is illustrated in [data fetching](data-fetching.md).

Avoid `items.length && <List />` where zero can render as text. Use an explicit condition such as `items.length > 0 ? <List /> : <EmptyState />`. Keep useful surrounding controls available during loading unless their use would invalidate the operation. A spinner alone does not tell users whether their previous changes were saved.

### Preserve Drafts And Explain Save Outcomes

```tsx
function DraftForm() {
  const [draft, setDraft] = useState('');
  const [status, setStatus] = useState<'idle' | 'pending' | 'saved' | 'error'>('idle');
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (status === 'pending') return;
    const submitted = draft;
    setStatus('pending');
    try {
      await saveDraft(submitted);
      setStatus('saved');
    } catch {
      setStatus('error');
    }
  }
  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="draft">Draft</label>
      <textarea id="draft" value={draft} disabled={status === 'pending'}
        onChange={event => { setDraft(event.target.value); setStatus('idle'); }} />
      <button type="submit" disabled={status === 'pending'}>Save</button>
      {status === 'pending' && <p role="status">Saving…</p>}
      {status === 'saved' && <p role="status">Saved.</p>}
      {status === 'error' && <p role="alert">Save failed. Your draft is kept; retry.</p>}
    </form>
  );
}
```

This example deliberately freezes editing during a save, so “Saved” refers to the visible draft. If editing remains enabled, track the submitted revision separately and never mark newer unsent changes as saved. Use unique label/input IDs if multiple form instances can coexist. For multi-field forms, provide field-level errors associated with the correct input, while retaining entered values.

Disabling a button is a UX guard, not server idempotency or concurrency control. Duplicate submissions can come from another tab, transport retry or a direct API call. The server needs the appropriate uniqueness, idempotency key or version check. A lost response after a successful write is an unknown outcome, not proof of rollback; reconcile it without blindly duplicating the write.

## Keep Controls Accessible

Use semantic buttons, links, labels and form elements before building custom equivalents. A clickable `div` does not provide keyboard activation, focus behavior or disabled semantics. Give icon-only controls accessible names. Connect help/error text with inputs and choose status announcements that do not repeat excessively during typing.

For dialogs and menus, reuse the project's accessible primitive when available. Test initial focus, keyboard navigation, escape/close behavior, and focus return to the initiating control. A lazy-loaded dialog still needs those behaviors when its content arrives. Do not hide focus outlines without a visible replacement.

Accessibility checks need both semantics and interaction. A role query can show that a name exists in a DOM test; it does not establish the full keyboard or screen-reader experience. Automated checks help locate problems, but do not claim complete accessibility from a passing build or one audit score.

## Guard The Data And Rendering Boundaries

Client validation improves feedback; server validation and authorization enforce the contract. Validate fetched JSON at the boundary with the project's schema/parser rather than `as SomeType`. Treat numeric strings, zero, null and absent values according to the actual API rules. Do not silently normalize identifiers or units to make a response fit.

Render untrusted strings as text. If rich HTML is genuinely required, use the existing vetted sanitization path and test its allowlist. Avoid `dangerouslySetInnerHTML` with raw server or user text. Keep private keys, session secrets and privileged configuration out of client bundles, local debug output and user-visible error messages.

### Hydration Needs Consistent Initial Output

In an SSR application, server output and the first client render should agree. Current time, randomness, locale-sensitive formatting or `localStorage` reads can produce different markup. Prefer a stable server-provided value, deterministic placeholder, or the framework's supported boundary. Access browser APIs only in the appropriate client lifecycle.

```tsx
// SSR-safe initial display; read the optional browser preference after mount.
function DensityLabel() {
  const [density, setDensity] = useState('comfortable');
  useEffect(() => {
    try {
      const saved = localStorage.getItem('density');
      if (saved === 'compact' || saved === 'comfortable') setDensity(saved);
    } catch {
      // Optional local preference can be unavailable; keep the default.
    }
  }, []);
  return <span>{density}</span>;
}
```

This may visibly update after mount, so choose a better server-readable preference if that matters to the product. It is not a general theme-flash solution. Do not scatter `suppressHydrationWarning`, disable SSR for the whole page, or inject an inline script without understanding the framework, CSP and consistency requirements. Plain SPAs do not need an SSR workaround.

## Test Behavior At The Right Boundary

### Use Realistic User Actions

With an existing React Testing Library setup, query controls by accessible roles and names and use its supported user-event helpers. Adapt imports, runner and assertions to the repository; do not replace the test framework to match an example.

```tsx
it('keeps the draft after a failed save and lets the user retry', async () => {
  const user = userEvent.setup();
  saveDraftMock.mockRejectedValueOnce(new Error('offline'));
  saveDraftMock.mockResolvedValueOnce(undefined);
  render(<DraftForm />);

  await user.type(screen.getByRole('textbox', { name: 'Draft' }), 'keep this');
  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Save failed');
  expect(screen.getByRole('textbox', { name: 'Draft' })).toHaveValue('keep this');

  await user.click(screen.getByRole('button', { name: 'Save' }));
  expect(await screen.findByText('Saved.')).toBeVisible();
  expect(saveDraftMock).toHaveBeenLastCalledWith('keep this');
});
```

This component test uses a mocked save boundary and proves UI behavior only. Add API/integration coverage with real persistence when the change involves saved state, permissions or transactions. A mocked success toast does not prove that data survives reload. An end-to-end test should reload or requery the actual saved value when persistence is a requirement.

### Force The Race You Need To Verify

For search, use controlled deferred responses: begin A, begin B, resolve B, then resolve A. Assert the final visible rows belong to B. Include unmount and failure paths. Avoid fixed sleeps as a way of hoping that the race occurs. For concurrent requests, assert both started before allowing either to finish.

For list identity, type into one editable row, reorder or filter the collection, and confirm text and focus stay with the same entity. For subscriptions, mount, update the relevant prop, unmount, and check that exactly the owned resource was cleaned up. For server identity, use barriers to interleave two different authenticated users and inspect actual results or writes.

For rare lazy UI, verify initial chunk loading, first open, failed chunk recovery and repeated open/close. A DOM simulation cannot establish real layout, browser chunk loading or network timing; use a production build and browser when those are the acceptance conditions.

## Evidence And Reporting

Run the project's existing lint, type checks and relevant tests. A build confirms compilation and bundling within its environment; it does not prove a user flow. Report which boundaries were actually exercised: static inspection, component DOM, mocked network, real API/storage, or browser interaction.

Performance comparisons need the same build mode, representative data and device/network conditions. Record initial bundle bytes or request ordering for loading changes, and a profile for render changes. Do not assert that every direct import, memo or transition is faster. Preserve failed output and explain unverified conditions instead of replacing failures with a synthetic successful response.

## Review Checklist

- Loading, empty, error, stale and saved states match actual outcomes.
- Failed saves preserve input; saved feedback identifies the submitted version.
- Semantic controls, names, keyboard behavior and focus are checked.
- Runtime input validation and server permissions remain independent of the UI.
- SSR output is deterministic where SSR exists; exceptions have a specific reason.
- Race, cleanup, reorder and retry tests assert observable behavior.
- Persistence and authorization use real boundary tests when required.
- The report distinguishes executed evidence from proposed checks and assumptions.

## Sources

- [Vercel React best practices at the adapted revision](https://github.com/vercel-labs/agent-skills/tree/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62/skills/react-best-practices)
