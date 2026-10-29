# E007: structural inference baseline, not a new policy

Frozen 2026-10-29 before execution. Scope: integer affine score classification,
a categorical interpretation, independent binary repair variables, positive
integer prior weights. This is a declared DSL, not a general SQL compiler.

Compute all answer/clarification joint histograms with forward score-distribution
messages and reverse messages, then apply the **unchanged EC2** objective. This
uses established generating-function/differential-inference ideas. It is a strong
baseline for future algorithm claims, not claimed as original inference.

Correctness: compare exact integer histograms with explicit worlds; independently
compare rational EC2 scores with weighted unordered-pair cuts. Exhaust all partial
states of 12 seeded three-bit, two-intent problems. Include the two-bit AND
interaction and a 64-bit constant output, which defeats local flip checks.

Scaling development: seeds 71029..71031, repairs 8, 12, 16, 32, 64, 128, 256;
two score programs with coefficients independently sampled in [-3, 6], offsets 0
and 1; cuts at floor(expected uniform score) and +4. Uniform priors. Report root
decision time, state count, full world count, and exact agreement with explicit
enumeration for n<=16. Single timing per case is exploratory, not a stable speed
claim; larger cases do not execute the exponential reference. No question-count
improvement is possible over EC2 with identical score/tie rules.

No API requests, natural ambiguity claims, or independent confirmation endpoints.
CPU timeout 15 minutes. If standard structured inference already removes the
claimed computational barrier, future work must compare to it, not only to
enumeration. Complexity is pseudo-polynomial in score range, and may still be
exponential for large binary-encoded coefficients or multidimensional rankings.
