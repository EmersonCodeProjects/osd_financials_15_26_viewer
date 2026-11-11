# Clean data

Built from `raw_data_OSD/` by script only. One tidy (long) table per topic:

| Column | Meaning |
|---|---|
| district | District name (OSPI) |
| county_district_code | OSPI code |
| school_year | e.g. 2024-25 |
| topic | staffing / pay / expenditure / revenue / fund_balance / enrollment |
| category | e.g. classroom_teachers, central_admin, program_97 |
| measure | fte, headcount, salary_total, comp_total, dollars, per_student |
| value | number |
| dollars_basis | nominal / cpi_2025 / blank if not money |
| source_file | raw file it came from |

Stage 1 fills these tables for Olympia only; Stage 2 adds rows for other districts with no schema change.

## Built so far
| File | Contents | Years | Built by |
|---|---|---|---|
| `f196_gf_expenditures.csv` | General fund actual expenditures by program, activity, object (raw OSPI codes) | 2014-15 to 2024-25 | `tools/extract_f196.py` |
| `f196_gf_revenues.csv` | General fund actual revenues by revenue code; `level` = total / subtotal / detail. Sum only `total` rows. | same | same |

Check totals (Olympia general fund expenditures, $M): 97.6 (2014-15), 133.0 (2018-19), 141.7 (2019-20), 156.7 (2021-22), 175.3 (2024-25). The 2021-22 download also contains 2019-20 and 2020-21; its totals match the Access files exactly for both years.
These two tables use raw OSPI codes and are not yet in the tidy schema above; the Clean step converts them using the maps below.

### Definition and benchmark tables (Define step, Nov. 9, 2026)
| File | Contents | Built by |
|---|---|---|
| `f196_code_map.csv` | Every program, activity, and object code in Olympia's data, with OSPI description and viewer group | by hand from OSPI's `24-25f196codes.xlsx`; checked that all codes in the data are mapped |
| `s275_title_map.csv` | All 33 S-275 duty titles with viewer category, subcategory, and a district-level flag | by hand; checked that every title in 2015-16 to 2025-26 is mapped |
| `benchmarks.csv` | Seattle CPI, levy IPD (general inflation, context only), state non-represented raises, L&I wage growth; school-year aligned, with original period, status, and note | by hand from `raw_data_OSD/inflation_and_rates/`; see `DEFINITIONS.md` for open items |

### Aggregate tables for the viewer (Clean step, Nov. 9, 2026; built by `tools/build_clean.py`)
Every row carries `derivation` (RAW, REGROUPED, CALCULATED, INFERRED, EXTERNAL) and `decision_ids` pointing to `../DECISIONS_AND_INFERENCES.md`. No names; counts under 5 are hidden.

| File | Contents |
|---|---|
| `staffing.csv` | S-275 FTE, rows, headcount, salary, compensation by job title and by category, per school year (pay blank where fewer than 5 people) |
| `position_flows.csv` | For each year step and category: stayed, moved in/out, left the list, new to the list (inferred by linking people across years) |
| `position_moves_pooled.csv` | Moves between categories pooled over all years (cells under 5 hidden) |
| `enrollment.csv` | Average monthly headcount, October headcount, average funded FTE, 2009-10 to 2026-27 (2026-27 provisional) |
| `f196_expenditures.csv` | General fund expenditures by program, activity, and object group, plus total and measure A |
| `f196_revenues.csv` | General fund revenues by source, plus the federal COVID relief subset |
| `central_admin_measures.csv` | Measures A, B, B2, C, D by year, with source tags, and the district's stated figure |
| `ratios.csv` | FTE per 100 students, spending per pupil (as reported and 2024-25 dollars), average compensation per FTE |
| `deflator.csv` | Seattle CPI school-year index and factor to 2024-25 dollars |
| `CHECKS.md` | What was checked, results, and what is still unchecked |

`tools/extract_s275.py` pulls Olympia rows from the statewide S-275 files into a person-level table (includes names; keep local, never publish).
