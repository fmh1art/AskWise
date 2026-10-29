# Algorithm status and proved boundaries

Updated 2026-10-29. No main-conference-quality new algorithm has been established.

## Oracle model lower bound

Assume an arbitrary deterministic answer function over a finite declared universe and no structural certificates beyond executed labels. If a stopping algorithm leaves any surviving world unexecuted, construct a second function which matches every observed execution but differs at that surviving world. The execution and clarification transcript is identical, but the answer for that possible true world differs. Therefore exact answer certification requires every surviving world to be executed in this oracle model.

If questions additionally require a witnessed unequal-answer pair, a constant answer function permits no questions. All worlds must be executed. Thus there can be no uniform execution saving on all functions under those assumptions. This is an elementary indistinguishability argument, not asserted as a new theorem in the literature.

## E004/E005

Exact action certification can eliminate worlds before labeling them while matching full-map EC2's question sequence. Coefficient-difference bounds are sound; the partition-star relaxation is tighter than independent edge bounds. Exhaustive Boolean checks and same-development-data results support implementation correctness. Savings remain small. Neither adaptive-submodularity guarantees nor total-cost competitiveness are proved for the acquisition policy. Prior art on lazy greedy, active gain evaluation, partition learning, and verification-guided planning still requires deeper review.

## E006

The certificate potential includes complementary label-revelation actions. An execution may resolve many edges only after another endpoint was executed, so adaptive diminishing returns cannot be assumed. Greedy heuristic gains are small or absent against witness-split and can lose to exact tiny planning. Query-first is cheaper when questions are cheap, but can ask irrelevant questions and does not satisfy a hard witness gate.

## Next discriminating work

1. Finalize the relevance/correctness guarantee with the user. The existing topic suggests strict correctness within a declared finite universe; no universal natural-language coverage promise is possible from finite sampling alone.
2. Under a strict objective, study sound SQL/repair structural certificates or stronger joint planners. Compare against the same certificates given to lazy EC2 and query-driven cleaning controls. Generic caching or LLM-asserted semantic equivalence alone is insufficient.
3. Use E003 solely to diagnose model candidate generation and pruning. Its two-state signature refinement has monotone reference recall by construction; that monotonicity is not a new empirical discovery.
4. Freeze genuinely independent confirmation data only after a candidate survives the development and novelty gates. Do not relabel E001/E002 as unseen validation after iterating on them.
