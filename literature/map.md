# Closest work and provisional contribution boundary

Search date: 2026-10-29. Targeted primary-source review, not a systematic review.

| Work | Verified mechanism | Implication for A2 |
|---|---|---|
| Cleaning Uncertain Data for Top-k Queries, ICDE 2013, DOI 10.1109/ICDE.2013.6544820 | Query-answer uncertainty guides cleaning | Query-driven cleaning is prior art |
| EC2, Golovin, Krause, Ray, NeurIPS 2010 | Active tests determine a hypothesis equivalence class | Joint finite worlds plus EC2 is an application, not a new objective |
| AmbiQT, EMNLP 2023, 2023.emnlp-main.436 | Alternative SQL interpretations under schema ambiguity | Native interpretation recovery differs from current-answer recovery |
| Disambiguate First, Parse Later, ACL Findings 2025, 2025.findings-acl.863 | Generate interpretations and infill missing interpretations; discusses duplicated AmbiQT columns | Missing-support generation and duplicate-column observation are established |
| AmbiSQL, arXiv:2508.15276 | Detect ambiguity and request multiple-choice clarification | Interactive clarification alone is insufficient novelty |
| AIR, arXiv:2610.24248, §3.2 | Executes candidate SQL; prunes identical results on current database | Directly overlaps naive "ask only when answers differ" |
| CircleClar, arXiv:2610.20052, §4–5 | Estimates model-realizable answer support through clarification cycles | Candidate support is a separate axis; model agreement does not certify global coverage |
| PRACTIQ, NAACL 2025, 2025.naacl-long.13 | Ambiguous/unanswerable conversations and helpful direct SQL | Need unknown/abstain cases and genuine interaction evaluation |
| Sphinteract, PVLDB 18, p1145 | User interaction resolving several ambiguity types | Must inspect full algorithm and human-study assumptions before final novelty judgment |
| ABISS, arXiv:2607.23340 | Interaction simulation across problematic NLQs | Simulated users and ambiguous-category benchmarks are established |

Provisional decision: **narrow / insufficient evidence for a new algorithm**. Repair-stable answer classes are a useful correctness requirement, but enumerating repair worlds is straightforward. E001 does not justify a new selector. E002 is a controlled stress extension, not a prevalence study. E003 tests where real candidate generation loses support. A main-conference paper needs either a substantive efficient mechanism, a convincing new benchmark/empirical finding, or a well-supported negative result beyond these pilot observations.

Access limitations: official AMBROSIA download failed via configured proxy and direct connection (2026-10-29); no data copied from unofficial mirrors. PRACTIQ official repository supplies generation code, not the published fixed 2,800-conversation artifact in its top-level structure. Do not count either as a completed benchmark.
