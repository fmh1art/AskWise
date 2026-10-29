# E002: AmbiQT column-synonym execution audit

Registered 2026-10-29 before execution. Audit all 1,240 validation items of official AmbiQT `col-synonyms`. Reconstruct renamed columns from the original SQLite data using the published extra_map. Compare both annotated SQLs using typed multiset results, preserving multiplicity. Also report ordered sequence equality where ORDER BY occurs. SQL execution errors are failures with recorded reasons, not equivalent answers.

This is a data-validity audit, not a claim to beat AmbiQT semantic parsing. The original benchmark measures recovery of distinct interpretations. Result equality on one finite database does not prove semantic equivalence, correctness of either interpretation, or safety under data changes.

For each successfully reconstructed case, create a deterministic, controlled alternative data state by swapping values in the second synonym of the first affected table at two rows with distinct non-null values, retaining original type. Choose rows by rowid and columns by lexical order. Do not select perturbations by whether they affect the query. Keep the first synonym unchanged. Evaluate both SQLs on both states. The four worlds are intent × candidate repair. This is a semi-synthetic stress extension, not naturally dirty data or four independent examples.

Report fraction equal before but unequal after perturbation, invariant fraction, all failures, database-cluster uncertainty, and exact method question costs. Golden candidate SQLs are an oracle control. Keep dataset and row contents outside Git; publish IDs, scripts, hashes, and aggregates. Separate future LLM-generated candidates from this oracle audit.
