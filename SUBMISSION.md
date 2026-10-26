# Portal submission copy

## Title

MultiSourceClaimResolver — Evidence-Backed Consensus Oracle Primitive

## One-line summary

A reusable GenLayer oracle that resolves natural-language claims from three committed web sources with per-source stances and independently validated consensus.

## Description

MultiSourceClaimResolver is designed for factual events that do not have a clean deterministic price feed: governance outcomes, official announcements, competition results, delivery events, insurance triggers, and cross-platform status claims.

A submitter commits one precise statement and three distinct evidence URLs. A leader renders each source, classifies it as SUPPORT, REFUTE, or NO_SIGNAL, and proposes a SUPPORTED, REFUTED, or UNRESOLVED verdict with bounded confidence and a concise rationale.

The custom equivalence logic is intentionally strict. Every validator first checks exact output keys, stance count, count-to-list consistency, majority rules, and confidence semantics. It then independently re-fetches all three sources and audits whether every source stance and the combined verdict are actually supported. This prevents consensus from collapsing into a thin “AI decides true or false” wrapper.

The contract preserves uncertainty instead of forcing a binary answer: fewer than two aligned sources or conflicting evidence produces UNRESOLVED with LOW confidence. Claims have a one-way PENDING → RESOLVED lifecycle, immutable source commitments, and a stored machine-readable resolution for downstream contracts and applications.

Both leader and validator prompts treat pages as untrusted evidence, ignore embedded instructions, forbid browsing beyond committed URLs, and cap fetched content. The repository includes architecture and risk documentation plus tests for input constraints, storage pickling, supported resolution, validator agreement, inflated-consensus rejection, and deterministic rejection of malformed stance counts.

## Evidence / repository

https://github.com/evrendag/multi-source-claim-resolver-genlayer

## GenLayer Explorer deployment

https://explorer-studio.genlayer.com/address/0x4b29233865c6c440DD6308628E2c87bAEdc789aa

Deployed on Studionet using Normal (Full Consensus). The deployment is
`FINALIZED`, with GenVM `SUCCESS` and consensus result `Accepted`.

## Test proof

`4 passed` with the official `genlayer-test` direct test runner.
