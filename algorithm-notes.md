# Algorithm status and proved boundaries

Updated 2026-10-29. No main-conference-quality new algorithm has been established.

## Strict contract and E007–E009 follow-up

The user has now explicitly confirmed strict answer correctness and question
relevance within declared alternatives, with execution cost the primary target.
The implementation formalizes relevance as a pair differing only in the queried
coordinate and yielding unequal answers, both already observed. This makes the
earlier arbitrary-pair gate in E006 insufficient. It also distinguishes relevance
from one-step mutual information: a relevant XOR input has zero marginal answer
information under uniform independent inputs. A nuisance input can tie with it
under EC2; relevance filtering must therefore be a baseline, not a novelty claim.

E008 audited all E001 episodes: EC2, optimal and answer-entropy asked no irrelevant
questions there, but fixed/random/repair-first did. Thus the constructed nuisance
XOR failure is a boundary example, not evidence of an EC2 failure rate on E001.

E007 shows why structure-aware prior art matters. Classical forward/reverse
score messages recover exact EC2 sufficient statistics without world expansion;
the 16-repair development cases match enumeration exactly and the 256-repair
cases finish in under one second each. This is not a new policy or a general SQL
compiler. Large score ranges or multidimensional scores may remain intractable.

For E008's Boolean uniform cube, let a,b,c,d be positive-label counts for the
four (q,r) response cells 00,01,10,11. Expanding standard EC2 edge mass gives
unnormalized gain(q)-gain(r)=(a-d)(b-c). Each unknown label contributes to one
count interval. Since the two differences use disjoint cells, all endpoints are
attainable independently; min/max products at the four box corners are the exact
extrema over binary completions. Normalized gains divide this expression by n².
Tests exhaust all 3^8 partial answer maps and 256 complete maps. This does not
prove that an acquisition policy minimizes executions or is original.

E009 confirms the limitation: fixed acquisition with exact bounds uses 13.7546
executions versus 14.8746 with the partition relaxation, but immediate witnessed
questioning uses 13.0117 and also wins total cost at weights 0.1, 1 and 10. These
are Boolean transformations of the same development tasks. Exact EC2 action
certification is therefore **not accepted as the main method** for the user's
execution objective. A tighter bound is useful implementation evidence, not
sufficient algorithmic success.

Termination detail for the exact Boolean policy: on a completely labeled
nonconstant cube, a coordinate's EC2 gain is a common term plus one quarter of
the squared positive-label imbalance between its halves. An irrelevant
coordinate has zero imbalance. If any imbalance is nonzero, a maximal one is
relevant. If all imbalances are zero, every coordinate ties, and cube
connectivity supplies a relevant one. The policy explicitly searches witnessed
maximizers instead of gating a single preselected tie winner. Thus either an
unexecuted world is executed, a coordinate is observed, or a constant surviving
answer is returned. The limit is N distinct executions and at most m questions.
This establishes safety and termination under the stated assumptions, not an
execution-complexity improvement over the trivial worst-case bound.

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
