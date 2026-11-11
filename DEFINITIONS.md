# Definitions

Every choice, assumption, and inference behind these definitions is logged with an ID in `DECISIONS_AND_INFERENCES.md`. If the two files disagree, fix both.

Status: **Define step, revised Nov. 9, 2026 after reading the S-275 handbook (2026-27).** Duty-title definitions below are from the handbook's duty code list (section V). Compared with the 2018-19 handbook: every duty title in Olympia's data is defined identically. 2015-16 to 2017-18 are not covered by a handbook on hand (log entry S5). The mapping tables are files, so the viewer and the checks read the same definitions:

- `clean_data_OSD/f196_code_map.csv`: every F-196 program, activity, and object code found in Olympia's data, with OSPI's description and the viewer group.
- `clean_data_OSD/s275_title_map.csv`: every S-275 duty title found in Olympia's data (33), with viewer category and subcategory.
- `clean_data_OSD/benchmarks.csv`: pay and inflation benchmarks, school-year aligned.

Rule: the same mapping is applied to every year. Raw codes stay in the data; groups are a layer on top, so a reader can regroup.

## Staff categories (S-275)

The public S-275 file gives a duty **title** (a rolled-up label), not a duty code. All 33 titles appear with identical wording in all 11 years (2015-16 to 2025-26), so no cross-year renaming was needed. Each title corresponds to a handbook duty code family (shown below). The public file does not say how it splits some families.

| Category | Duty titles | Notes |
|---|---|---|
| District administration (certificated) | Superintendent (11x); Deputy/Assist. Supt. (12x); Other District Admin. (13x) | 13x covers anyone who "directs staff members or manages a function, a program, or a supporting service in a district," including administrative assistants, directors, supervisors and coordinators of districtwide programs. In Olympia's data these rows are certificated. Shown as separate lines. |
| Classified directors/supervisors | Director/Supervisor (99y) | **Not district administration in OSPI's scheme.** 99y is a classified director or supervisor of a support service (food service, maintenance, transportation, data processing). 95% sit at the district location (2022-23 on). Shown as its own line, because the community's concern about administration may include these roles. |
| Building administration | Elementary and Secondary Principal (21x, 23x); Elem. and Secondary Vice Principal (22x, 24x); Other School Admin. (25x) | |
| Teachers | Elem. Homeroom (31x); Secondary (32x); Other Teacher (33x); Elem. Specialist (34x); Substitute (52x) | 33x is ungraded, special education, gifted, disadvantaged, early childhood, home or hospital, and adult education. Substitute is under 1 FTE in any year. |
| Other certificated | Counselor (42x); Library Media Specialist (41x); Nurse (47x); Psychologist (46x); Social Worker (44x); Occupational Therapist (43x); Physical Therapist (48x); Speech-Language Path./Audiology (45x); **Other Support Personnel (40x)** | 40x is in the certificated educational-staff-associate range: attendance officers, educational specialists, department heads, mentors. (My first pass wrongly put it in classified support.) |
| Paraeducators | Aide (91y) | The code also covers bus monitors, lunchroom aides, and community service aides, not only classroom aides. |
| Classified support | Office/Clerical (94y); Technical (98y); Professional (96y); Operator (95y); Service Worker (97y); Crafts/Trades (92y); Laborer (93y) | Operator = bus drivers, vehicle operators, dispatchers. Service Worker = custodians, food service, security, warehouse. Professional = baccalaureate-level classified staff and non-certificated coaches (about 120 small-FTE rows a year). |
| On leave | Certificated on Leave (610); Classified on Leave (900) | In totals only. |

Decisions
- **Contract type is invisible.** The handbook's third digit separates base contracts from supplemental ones (extra duty, coaching), but the public file gives only the title, so supplemental rows cannot be separated from base rows.
- **FTE is primary.** Headcount is secondary and must de-duplicate people: one person can have several rows (2024-25: 1,443 rows, 1,440 distinct names, 1,100.4 FTE). Certificated staff have a certificate number; classified staff do not, so de-duplication is by name, which can merge two people with the same name.
- **Salary and total compensation (salary + insurance + mandatory benefits) are both kept.**
- **COVID relief positions are not identifiable in S-275.** Flag years 2020-21 to 2023-24 on the finance side (F-196 programs 11-14, 18, 19), and say that staffing cannot be split by funding source.
- **Building (location) exists only from 2022-23.** Files for 2015-16 to 2021-22 have no building column, so per-school staffing and anything by "district office location" can only be shown for 2022-23 onward.
- **The public viewer shows aggregates only.** No named individual's pay. The person-level extract holds names and stays local.

## Finance categories (F-196, general fund only)

Groups are in `f196_code_map.csv`. All codes in Olympia's data are mapped. One exception: object code 6 is not in OSPI's list and is $0 in every year.

- **Program groups:** basic education (01, 02, 03, 09); special education (21-26, 29); career and technical (31, 34, 38, 39, 45-47); learning assistance and Title (51-57, 59, 62, 69, 76); English learners and bilingual (64, 65); highly capable (74); other instructional (58, 61, 67, 68, 71, 73, 75, 78, 79); community and early learning (81, 86, 88, 89); COVID relief and stabilization (11-14, 18, 19); districtwide support (97); food service (98); transportation (99).
- **Activity groups:** general administration (11-15); building administration (23); teaching (27); instructional support and other student services (21, 22, 24, 25, 26, 28, 29, 31-35); food service (41, 42, 44, 49); transportation (51-53, 56, 58, 59); maintenance and operations (61-69); district support services (72-75); debt service (83-85); public activities (91).
- **Object groups:** certificated salaries (2), classified salaries (3), benefits and payroll taxes (4), supplies (5), purchased services (7), travel (8), capital outlay (9), transfers (0, 1; net to about zero each year).
- Totals tie to the 2014-15 to 2024-25 check totals in `clean_data_OSD/README.md`.

## Central administration: four definitions, shown side by side

None of these is "the" answer. They measure different things, and the viewer should say so. The district's own figure goes next to them.

| # | Definition | Source | 2019-20 | 2023-24 | 2024-25 |
|---|---|---|---|---|---|
| A | **Spending on general administration activities**: F-196 activities 11-15 (board, superintendent's office, business office, human resources, public relations), all programs | F-196 | $4.23M (2.99% of general fund) | $4.56M (2.75%) | $4.00M (2.28%) |
| B | **Staff with district administrator titles**: Superintendent, Deputy/Assist. Supt., Other District Admin. (11x-13x) | S-275 | 11.0 FTE, $2.20M total comp | 11.0 FTE, $2.42M | 10.7 FTE, $2.53M |
| B2 | B plus **classified Director/Supervisor (99y)** | S-275 | 29.8 FTE, $4.82M | 32.1 FTE, $5.92M | 30.6 FTE, $5.85M |
| C | **Everyone listed at the district office (Knox) building** in the community group's staff-directory match | Community spreadsheets | about $11.43M total comp | $14.3M, 110 people | $14.8M, at least 102 people (2025-26) |
| D | **Everyone with the district-level location code in S-275** (code 1035 "Olympia School District 111"; 2022-23 on) | S-275 | not available | 224 people, 179 FTE, $22.0M | 199 people, 156 FTE, $20.4M |
| | District's stated figure | Oct. 22 FAQ | | | 4.88% (year and base not stated) |

What each one includes
- **A** is spending in general administration activities, no matter which program or job title. It is the narrowest.
- **B** is by job title, the narrowest staff measure. B2 adds the classified managers of support services. Both exclude clerical, technical, and other support staff who work for those offices.
- **C** adds everyone in the Knox directory: social workers, occupational therapists, technology, nutrition services, and office staff. It is a building-based definition, not a function-based one.
- **D** is wider than C. The district location code also holds bus operators (54 rows in 2023-24), maintenance trades, aides, and others who are assigned to the district rather than to a school.

Open item: **4.88% is not reproduced by any grouping tried so far.** 4.88% of 2024-25 general fund spending ($175.3M) is $8.6M. Activities 11-15 give $4.0M; adding information systems (72) gives $6.2M. The district's year, base (general fund, total budget, or something else), and activity list are not stated, so the viewer should show 4.88% as "the district's stated figure" with its source, not as a number we computed. A question to put to the district's finance office: which F-196 activities, which year, and which base.

Also note: the community group's sheet says some names "could not be found" in S-275, so C is a subset-match, not a count from the state file.

## Inflation, pay benchmarks, and base years

- **Deflator:** Seattle-area CPI (the "Seattle CPI" column is the Seattle-Tacoma-Bremerton index in Table A4.1, "Selected Inflation Indicators," in `PCE Sept 2026.pdf`; the publisher is not named on the page). School-year value = mean of the two calendar-year annual averages (2015-16 = mean of 2015 and 2016). **2025-26 uses calendar 2026, which is a forecast in the source**; the viewer must label it.
- **IPD (`IPD.csv`) is general inflation used for the property-tax levy limit, not a school pay series.** The source is the Dept. of Revenue page on levy limits ("percentage change in the implicit price deflator"), labeled by the "property taxes due" year. I had called it the state K-12 salary inflation factor; that was wrong. The page does not state the measurement period, but each labeled value matches the PCE change for the *previous* calendar year in Table A4.1 (label 2023 = 6.457% vs. PCE 2022 = 6.5%; label 2024 = 3.67% vs. 3.8%; label 2016 = 0.25% vs. 0.2%). So label Y is placed on school year (Y-1)-Y, series name `levy_ipd_inflation`, status `aligned_by_comparison`. Context only.
- **State employee general increase (non-represented)** from OFM's "Legislative Approved General Wage Adjustments," assigned to the school year containing the effective date (July 1 = start). Two increases in one school year are compounded (2018-19: July 2018 2.0% plus Jan 2019 2.0% = 4.04%). July 2020 and July 2021 (3.0% each) were set by Governor's Directive 20-08 and not all non-represented employees received them; some got neither. Marked `partial`. Union-specific rows are not averaged in.
- **Correction to the Nov. 9 handoff:** the handoff list of non-represented raises left out **July 2019 (3.0%)**. It is in the OFM table and is now in `benchmarks.csv`.
- **L&I statewide average wage growth** (the L&I page defines it as the annual change in the Statewide Average Annual Wage, from the Employment Security Department; it does not say calendar or rate year, so I assumed calendar and mapped it to the school year starting that year). I read the L&I page itself on Nov. 9 and it matches the spreadsheet; values exist only for 2015 through 2022 (2.6, 4.8, 5.0, 5.5, 6.7, 10.1, 7.5, 2.0 percent). **Correction to the handoff:** the 4.8, 4.9, 3.8 percent it lists for 2023-2025 are the workers' compensation hourly *rate changes*, not wage growth; wage growth is blank for 2023 on. The 2020 and 2021 values are inflated by the loss of low-wage jobs.
- **Thurston County employee raises:** no table found. Show the two-year raise freeze as a note citing the web notice.
- Show 2015-16 onward. Index charts use a stated base year with a control to change it. Proposed: no single default; two periods split at the enrollment peak (see `DECISIONS_AND_INFERENCES.md`, V1).

## Position changes (staff flows between years), no names

The question: which kinds of positions are shrinking, which are growing, and which people appear to move between kinds of positions. S-275 has no position IDs, so this is inferred from people linked across years. It is an estimate and says so on the page.

- **Linking (done locally, never published):** certificate number for certificated staff; last and first name for everyone else. Names appear only in a local working file. Outputs are counts and FTE.
- **Person-year category:** the category with the most FTE for that person that year (ties broken by pay).
- **Flows between consecutive years, by category and title:** *stayed* (same category), *moved* (different category), *left the district's S-275 list*, *new to the list*. Net FTE change by title is the primary figure; flows explain it.
- **What it can and cannot say.** A title's FTE falling by 5 can be five people leaving, one person's hours cut, or people retitled. "Left" and "new" include name changes, name collisions, returns after a gap, and staff on a different payroll. In 2024-25 to 2025-26, 1,222 people stayed in their category, 29 moved, 189 left the list, 206 were new (preliminary). Moves are rare; most change is entry and exit.
- **Suppression:** any cell with fewer than 5 people is shown as "fewer than 5" or merged into its category, so single-person offices are not identifiable. Superintendent and similar one-person titles appear only as an FTE line.
- **Not a count of budgeted positions.** Cuts as positions (e.g. "eliminated a 1.0 FTE director job") need the district's position control or budget documents, which are outside S-275.
- The community Knox directories could help match fractional rows to people. Use them only to check our linking, locally, and never publish what they show.
