# NEUROSPINE Literature Index

Literature notes use a note-format spec with structured frontmatter. Each note
is a single .md file indexed by its seed-paper slug.

## Frontmatter fields

- **slug**: Unique identifier (kebab-case, e.g., `meicoder-sobotka-2510-20762`).
- **authors**: Paper authors (e.g., "Sobotka et al.").
- **venue**: Conference, journal, or repository (e.g., "NeurIPS 2025", "Nature").
- **year**: Publication year (e.g., 2025). Use `TBD` if unknown.
- **identifier**: DOI, arXiv id, eLife article number, or OpenReview id.
- **projects**: List of portfolio slugs this paper plausibly touches (e.g.,
  `[tribe-neuroprint, anesthesia-bridge]`).
- **gates**: List of gate numbers this paper might inform (e.g., `[G6, G8]`).
- **verdict**: One of `subsumes`, `sharpens`, `invalidates`, `adjacent`.

## Note body

Each note has three sections:

1. **Paragraph 1**: Mechanism summary, one paragraph. If abstract not yet fetched,
   use exactly one line: `TBD (unindexed; queued for WebFetch)`.
2. **Paragraph 2**: Preliminary relevance mapping. Every sentence prefixed with
   "Provisional:". Explain which portfolio slugs the topic plausibly touches and
   which gates it might inform, based on title/abstract alone.
3. **Action items**: Bulleted list of at least two items linking to specific
   `../portfolio/<slug>/evaluation.md` files, phrased "Re-score G<n> after
   WebFetch of abstract."

For tracking hubs (e.g., Engram, Mineault), replace paragraph 1 with a bulleted
list of labs/people to monitor, with URLs (or `TBD` if uncertain).
