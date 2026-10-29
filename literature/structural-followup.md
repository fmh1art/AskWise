# Structural-method novelty follow-up — 2026-10-29

Targeted primary-source triage, not an exhaustive review. New searches included
stochastic Boolean function evaluation, score classification, equivalence-class
determination with sampling/factorization, probabilistic aggregate generating
functions, differential inference, and SQL counterexample verification.

| Primary source | Verified overlap and consequence |
|---|---|
| [SpotIt](https://arxiv.org/abs/2510.26840), Klopfenstein et al. | Bounded verification seeks databases distinguishing two SQL queries. Counterexample generation alone is not new. |
| [SpotIt+ v3](https://arxiv.org/abs/2603.04334v3), Tremante et al. | Adds mined constraints to differentiating-database search. The current author order differs from the first-version search snippet; use the current arXiv record. |
| [SOMA-SQL](https://arxiv.org/abs/2606.11424), Somayajula et al. | Synthetic logs and execution probes address multiple ambiguity sources. Probing to resolve ambiguity has direct prior art. |
| [Stochastic Score Classification](https://arxiv.org/abs/1806.10660), Gkenosis et al. | Sequentially reveal costly bits until a score category is determined. Threshold-based stopping is established. |
| [Making Massive Probabilistic Databases Practical](https://arxiv.org/abs/1307.0844), Todor et al. | Generating functions avoid explicit possible-world enumeration for supported aggregates. Enumeration is an insufficient sole scalability baseline. |
| [A Differential Approach to Inference in Bayesian Networks](https://people.cs.pitt.edu/~milos/courses/cs3710/readings/differential-darwiche.pdf), Darwiche | Arithmetic-circuit differentiation computes inference queries. E007's forward/reverse marginal messages use this established inference pattern. |
| [BISECT](https://papers.nips.cc/paper_files/paper/2017/file/e139c454239bfde741e893edb46a06cc-Paper.pdf) | Exploits independent Bernoulli structure in decision-region determination. Factoring a hypothesis universe is not itself a contribution. |
| [Chen thesis, Chapter 4](https://yuxinchen.org/files/theses/chen17-phdthesis.pdf) | Sampled decision-region determination and premature stopping are already studied. Adding Monte Carlo to EC2 is not automatically new. |

E007 implements known inference ideas as a strong control. E008's four-cell
identity is derived from the standard EC2 objective and exhaustively checked;
the search has not established its originality. E009 tests whether its tighter
comparison certificate helps the user's execution-cost objective. The simple
immediate-witness control remains essential. No success claim follows from a
correct identity, a faster implementation of a known policy, or absent exact
phrase matches in literature search.
