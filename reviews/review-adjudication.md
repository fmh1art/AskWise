# Adjudication of model suggestions

2026-10-29: Doubao design review received. Its recommendation to measure candidate coverage and execution costs is relevant. Its purported 10–100x latency ratio and 12–15% human error rate have no verified source and are rejected. It incorrectly calls EC2 a schema-based SQL equivalence checker; EC2 takes the partition as input and does not establish SQL equivalence. It calls our observed-data ablation AIR, although we explicitly did not reproduce AIR. Its phrase "statistically indistinguishable" is unsupported without an uncertainty analysis. None of these statements may enter the paper as facts.

The review is advisory evidence only. The retained decision is based on E001's computed costs, not model agreement.

Algorithm ideation: Doubao's claimed |intent classes| + |repair classes| execution bound is false: a 2×2 answer matrix with only its bottom-right entry differing defeats checks on one row and one column. It also assumes LLM-certified universal SQL equivalence without evidence, supplies unsupported redundancy percentages and expected speedups, and substitutes unrequested APIs. These are rejected. GPT's proposal labels the mass of separated disagreement pairs as an EC2 expected cut; the actual EC2 cut additionally includes same-outcome pairs removed when another response occurs. Neither proposal establishes algorithmic novelty. E004 instead derives exact EC2 coefficient-difference bounds and verifies action traces exhaustively. Its novelty and advantage remain open.
# E008/E009 strict-contract review (2026-10-29)

Both configured APIs received the explicit assumptions and measured development
results. Their raw advisory replies are retained as `strict-contract-*.json`.
They are not independent empirical replications or novelty evidence.

- GPT's expansion of the unordered EC2 edge objective and four-corner bound
  agrees with our independent exhaustive checks. Its tie-handling warning is
  valid: preselecting a nuisance coordinate and then applying the relevance gate
  can deadlock. `run_binary` instead searches all witnessed coordinates for a
  certified maximizer; the implementation already uses that rule.
- Doubao labels its algebra a pass but computes the wrong individual gains and
  reverses the difference. The sign cannot be dismissed as merely a convention
  after the direction q-minus-r was fixed. For a four-world map with a=b=1 and
  c=d=0, actual unnormalized gains are G(q)=4 and G(r)=3, so the difference is +1;
  Doubao's displayed formulas give 0 and 1. Reject that derivation.
- Doubao's termination explanation only addresses constant maps and omits the
  witnessed-maximizer existence case. Its suggestion that exact certified
  comparisons are non-transitive is also false: if q>=r and r>=s hold for every
  feasible completion, then q>=s holds for every feasible completion.
- The negative cost ordering follows from saved E009 measurements, not model
  agreement. The crossover E+cQ is approximately c=46.92 for fixed exact bounds
  versus immediate-witness on this development sample; no universal ordering or
  calibrated production price follows.
