# Olympia School District: staffing, pay, spending and revenue, 2015-16 to 2025-26

A neutral, self-contained data viewer. `index.html` is the page (data and methods are embedded; no server needed). It shows district-wide enrollment (headcount), staffing (FTE), pay, and general fund revenue and spending, with every grouping, calculation and assumption logged.

This viewer was generated with Claude and covers a decade of data drawn from thousands of pages of public documentation. We have tried to minimize errors, but it is presented as is, as an aid to understanding the district's financial history, points of departure and trends. Sources are in `SOURCES.md`; the cleaned data are in `clean_data_OSD/`.

## Contents
| Path | What it is |
|---|---|
| `index.html` | The viewer (host this with GitHub Pages). |
| `clean_data_OSD/` | Cleaned tables the viewer uses, with a schema (`README.md`) and checks (`CHECKS.md`). Aggregates only; no names; counts under 5 are suppressed. |
| `SOURCES.md` | Every source, URL, years and status. |
| `DECISIONS_AND_INFERENCES.md` | Every grouping, calculation, assumption and limit, with an ID. Charts cite these IDs. |
| `DEFINITIONS.md` | Staff categories, finance categories, inflation series. |
| `tools/` | Scripts that built the tables and the page. |

## Tags used on the page
`RAW` as reported; `REGROUPED` reported data placed in our groups; `CALCULATED` arithmetic on reported data; `INFERRED` an assumption was needed; `EXTERNAL` from a source outside OSPI or the district.

## Not included in this repository, and why
Raw inputs are left out for three reasons: **privacy** (several contain individuals' names), **no duplication** (the original publishers already host them, and copying them would only make the internet bigger), and **size**. Everything the page displays is in `clean_data_OSD/`, so the page works without them.

| Raw input | Why it is not here | Where to find it |
|---|---|---|
| OSPI S-275 personnel files, statewide, 2015-16 to 2025-26 | One row per person, with names. Only aggregates (no names, counts under 5 suppressed) are published here. | https://ospi.k12.wa.us/safs-data-files |
| OSPI F-196 actual revenues and expenditures, 2014-15 to 2024-25 | Large, and already public. | https://ospi.k12.wa.us/safs-data-files |
| District enrollment workbook (2009-10 to 2026-27) | Already public from the district. The cleaned headcounts are in `clean_data_OSD/enrollment.csv`. | Olympia School District enrollment dashboard. |
| State employee bargaining agreements (WFSE General Government, 2015-17 to 2023-25) and the OFM 2025-27 summary | Already public. The raise percentages and salary-schedule values used are typed into `clean_data_OSD/benchmarks.csv`, each with its source. | Washington Office of Financial Management, labor relations pages; the OFM summary URL is in `SOURCES.md`. |
| OSPI S-275 handbooks, legislative salary schedules, agency head tables | Already public. | URLs in `SOURCES.md`. |
| Community workbooks ("OSD Admin Data-For Sharing", Knox administration spreadsheets) | Contain individuals' details. Only totals and match counts are used (`community_*.csv`). | Available from their compilers by request. |

Consequence: the page and every cleaned table can be inspected here, and the scripts in `tools/` show exactly how each table was made. To rerun the scripts from scratch you would first download the OSPI, OFM and district files above. The community-workbook comparison tables cannot be rebuilt without the compilers' permission.

## Rebuilding the page from the cleaned tables
    python3 tools/build_viewer.py --clean clean_data_OSD --decisions DECISIONS_AND_INFERENCES.md --template tools/viewer_template.html --out index.html

`tools/extract_s275.py` and `tools/extract_state.py` read the OSPI S-275 spreadsheets; `tools/build_clean.py` and `tools/build_pay.py` build the cleaned tables.

## Corrections
Open an issue on GitHub. This viewer is presented as is, as an aid to understanding the district's financial history and trends.

## Credits
Community workbook "OSD Admin Data-For Sharing" compiled by Janel Bistrika (2026), used with credit where tagged EXTERNAL.
