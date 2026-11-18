# Supplementary data: On-device facial expression recognition for mobile interactive systems — a systematic literature review

This dataset supports the systematic literature review (SLR) *"On-device facial expression classification for mobile interactive systems: a systematic literature review of lightweight models, real-time performance, and server load"* (submitted to the Journal of Systems Architecture). The review follows Kitchenham's guidelines, reports its selection in a PRISMA 2020 flow diagram, and complements the database search with forward and backward snowballing (Wohlin, 2014) until saturation.

## Contents

| Folder | File | Description |
|---|---|---|
| `01_search` | `search_protocol.md` | Research questions, the four ScienceDirect search strings, inclusion/exclusion criteria, and the IC3 protocol amendment |
| | `records_deduplicated.csv` | 84 unique records from ScienceDirect (102 before DOI-based de-duplication); bibliographic metadata only |
| `02_selection` | `database_selection.csv` | Decision and reason for each database record (title/abstract, full text, IC3 amendment) |
| `02_selection/snowballing` | `iterN_candidates.csv` | All candidates retrieved from OpenAlex in each iteration (backward = references, forward = citing works) and the automatic filter result |
| | `iterN_title_abstract.csv` | Title/abstract decisions for candidates that passed the automatic filter |
| | `iterN_full_text_IC3.csv` | Final decisions under the amended IC3 (device-level evidence), with the basis (full text or abstract) |
| `03_extraction_quality` | `extraction_and_quality.csv` | Data extracted from the 54 primary studies and their quality scores (QA1–QA6) |
| | `quality_assessment_guide.md` | Scoring rules for QA1–QA6 |
| `04_scripts` | `*.py` | Python scripts used for de-duplication, OpenAlex snowballing, filtering, and statistics/figures |

## Study IDs

- `P###`: records from the ScienceDirect database search (19 primary studies retained)
- `S###`, `T###`, `U###`: snowballing iterations 1, 2, and 3 (19, 13, and 3 primary studies). Iteration 4 (`V###`) yielded no new studies, so saturation was reached.

## Selection summary

- Database: 102 records → 84 unique → 33 passed title/abstract → 30 after full-text reading → 19 after the IC3 amendment.
- Snowballing: 3,417 candidates across four iterations → 35 included (new studies per iteration: 19 → 13 → 3 → 0).
- Final set: 54 primary studies (45 extracted from full text, 9 from abstracts because the full text was inaccessible).
- Second reviewer: independent full-text screening of the 33 database candidates; 90.9% initial agreement, Cohen's κ = 0.82. All disagreements were resolved by discussion.

## Notes

- Free-text notes in the decision files (`Keputusan`/Decision, `Alasan`/Reason, `IC3_note`) and some extracted values are written in Indonesian, the authors' working language. Criterion codes (IC1–IC3, EC1–EC3) follow `search_protocol.md`.
- Abstracts, full texts, and publisher RIS exports are **not** redistributed for copyright reasons. All records can be retrieved through their DOI or OpenAlex ID.
- The scripts expect the original folder layout and the (non-redistributed) RIS/PDF files, so they document the procedure rather than run out of the box.

## License

Data and documentation: CC BY 4.0. Scripts: MIT.
