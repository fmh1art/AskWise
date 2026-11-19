# E011. SQL error audit on AmbiQT Candidates

Use the 155 question IDs and both saved model runs from E003. Replay every generated SQL statement on the observed database and its prescribed swap. Count non-executable candidates separately. The semantic audit population comprises executable candidate occurrences whose pair of outputs matches neither reference, before either pruning rule. Two candidates with the same signature remain separate occurrences. The unit is a generated query, so a question may appear more than once.

Within each model, sort eligible occurrences by the SHA256 of `AskWise-E011-v1|model|item_id|position`, with one-based generation positions, and take the first 50. Present the pooled sample in a second hash order under opaque IDs. Omit model, generation position and generated natural-language interpretation from the annotation packet. Read the question, candidate SQL and both references, using the schema and source data when necessary.

For each occurrence record one or more substantive differences from the closest reference and a short SQL-specific rationale. Ignore harmless aliasing, SQL spelling and any ordering difference that cannot affect the multiset of typed rows. When one change has several syntactic consequences, label the underlying difference once. Use multiple labels for distinct deviations. A plausible alternative reading may still disagree with both benchmark references.

| Label | Decision rule |
| --- | --- |
| projection | Different returned field, extra or omitted field, output order of columns, or different scalar expression or representation in the projection. |
| relation | Different source population, missing or extra relation, incorrect join key or join type. Include an existence restriction caused by joining another table. |
| filter | Different selection predicate, including its operand, literal, comparison, logical scope or missing condition. |
| aggregation | Different aggregate, grouping granularity, count unit or duplicate handling. An extra grouping key matters when it changes the rows or their multiplicity. |
| ranking | Different ordering key or direction when selecting rows, limit, offset, or handling of ties at a cutoff. |
| other | A specific mismatch outside these categories. Explain it in the rationale. |
| unresolved | The SQL comparison does not establish a defensible label. Use alone. |

OpenAI Codex performed one blinded annotation pass. The packet had no model names or model-written descriptions. The annotator inspected SQL, schema and execution results for individual discrepancies, including ties and duplicate rows.

Report counts and percentages per 50 sampled failures for each model and per 100 for the balanced sample. A candidate counts at most once in each category. The pooled sample weights the two models equally. Use descriptive rates and identify the annotator. This audit does not provide independent human labels or inter-annotator agreement.

After completing the labels, we added an execution-based check for output column order. For each executable mismatch in the full population, test whether one fixed permutation of the output columns yields either reference signature on both states. Keep row multiplicities and SQLite value types. Record this flag separately from the discrepancy labels. A match under this check establishes agreement on the two tested states.

From the research repository run `.venv/bin/python scripts/audit_sql_errors.py prepare /tmp/askwise-e011` to rebuild the blinded packet and `results/E011/sample.json` from local E003 artifacts. After annotation, run `.venv/bin/python scripts/audit_sql_errors.py summarize` to check the annotation IDs and regenerate the counts. The manifest includes the sampled SQL, question, both references and the generation position for each case. The preserved notes in `results/E011/annotations.json` use the packet IDs.
