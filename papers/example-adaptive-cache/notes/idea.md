# Idea

## Problem

Cache miss rates spike under bursty, non-stationary workloads, and static policies (LRU/LFU) adapt too slowly.

## Why it matters

Production systems with diurnal or event-driven traffic pay latency and backend-load costs when the working set shifts faster than the eviction policy can track.

## Proposed contribution

We present an adaptive cache policy that reduces miss rate under bursty workloads by estimating short-horizon reuse and switching eviction modes online.

## Claims

1. Under bursty synthetic and production-like traces, the adaptive policy reduces miss rate versus LRU and LFU.
2. Adaptation overhead remains small enough for inline request-path use.
3. A simple reuse-horizon estimator explains most of the gain (ablation).

## Non-goals

- Multi-tier or distributed cache coherence
- Hardware cache replacement
- Learned models requiring offline training for every deployment

## Evidence you already have

- Prototype simulator
- Two public traces + one anonymized production-like trace (TODO: confirm release constraints)

## Open risks

- Novelty vs existing adaptive/ARC/learning-cache literature
- Fair baseline tuning
- Whether gains survive write-heavy mixes
