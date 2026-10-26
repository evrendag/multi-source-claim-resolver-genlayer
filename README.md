# MultiSourceClaimResolver

`MultiSourceClaimResolver` is a standalone GenLayer oracle primitive for
resolving natural-language factual claims from three explicit web sources. It
is useful where a deterministic oracle feed does not exist: governance
outcomes, public announcements, competition results, delivery events,
insurance triggers, and cross-platform status claims.

## Why this is an Intelligent Contract

The hard part is not downloading a page. It is determining whether each page
actually supports the same precise claim while respecting dates, units, scope,
contradictions, missing evidence, and source ambiguity. This contract combines
deterministic invariants with GenLayer's non-deterministic consensus.

The final output is intentionally narrow and composable:

- verdict: `SUPPORTED`, `REFUTED`, or `UNRESOLVED`;
- confidence: `LOW`, `MEDIUM`, or `HIGH`;
- one stance per source: `SUPPORT`, `REFUTE`, or `NO_SIGNAL`;
- support/refute counts and a short rationale.

## State and lifecycle

Each claim stores its creator, immutable statement, three immutable source
URLs, status, and the complete accepted resolution. The lifecycle is one-way:

```text
PENDING -> RESOLVED
```

Resolution is permissionless because the caller does not control the result.
The consensus process does. A resolved claim cannot be overwritten.

## Consensus and equivalence design

The leader renders all three source pages and proposes structured JSON. Before
using another model, every validator deterministically checks:

- exact output keys and enum values;
- exactly three source stances in source order;
- counts equal the stance list;
- a supported/refuted verdict has a two-source majority;
- `HIGH` means three aligned sources, `MEDIUM` means exactly two;
- an unresolved claim always has `LOW` confidence;
- rationale length is bounded.

A validator then independently re-fetches the same three sources and audits
whether every stance and the combined result are evidence-backed. Validators
vote on semantic correctness rather than reproducing identical prose. This is
the contract's custom Equivalence Principle.

## Reliability boundaries

- Source text is explicitly treated as untrusted and embedded instructions are
  ignored in leader and validator prompts.
- Browsing is limited to the three committed URLs.
- Each rendered page is capped at 8,000 characters.
- Three distinct URLs are required.
- Contradiction or insufficient corroboration resolves to `UNRESOLVED`, not a
  forced binary answer.
- The contract reports evidence consensus; it does not guarantee publisher
  independence or make legal claims. Integrators should curate source policies
  appropriate to their risk level.

## Public methods

### `create_claim(statement, source_a, source_b, source_c)`

Commits a claim and three distinct HTTP(S) evidence URLs.

### `resolve(claim_id)`

Permissionlessly runs leader/validator consensus and permanently stores the
accepted structured result.

### `get_claim(claim_id)` and `count()`

Expose the full resolution for other contracts, applications, and reviewers.

## Example integration

An insurance application needs to know whether an event organizer officially
cancelled a conference. It creates a claim using the organizer's status page,
the venue notice, and an industry publication. Once resolved, the application
can consume `verdict`, `confidence`, and per-source stances under its own
payout policy.

## Tests

The test suite covers input constraints, storage pickling, a three-source
supported resolution, independent validator agreement, rejection of an
evidence-inflated leader proposal, and deterministic rejection of mismatched
stance counts.

```bash
pip install genlayer-test
pytest tests/ -v
```

Run a final Studio Mode integration test with multiple validators before a
production deployment.
