# Checks run on the clean tables (Nov. 9, 2026)

Each check says what was compared and the result. "Not yet checked" items are listed at the end; they are open, not passed.

| Check | Result |
|---|---|
| General fund expenditures: program-group, activity-group, and object-group totals each equal the all-codes total, every year | Max difference $0.00 |
| General fund expenditure totals vs. the extraction check totals ($M: 97.6, 108.0, 115.4, 123.5, 133.0, 141.7, 142.3, 156.7, 165.5, 165.4, 175.3) | Match |
| Revenue minus expenditures, by year | Between -$2.0M and +$2.9M (e.g. 2019-20 +$2.9M, 2022-23 -$2.0M); consistent with the handoff note ("within about $3M") |
| Federal COVID relief revenue (detail codes 6x11-6x14, 6x18, 6x19) vs. COVID program expenditures (programs 11-14, 18, 19) | $19.4M of revenue (2020-21 to 2023-24: 1.9, 8.5, 7.0, 1.9) vs. $18.3M of expenditure. A first version of the script returned $0 every year because of a code-filter error; found by this check and fixed |
| S-275 Olympia rows, FTE, distinct names per year | 2024-25: 1,443 rows, 1,100.43 FTE, 1,440 names (matches handoff). All 11 years extracted; no unmapped duty titles |
| S-275 duty-code definitions, 2018-19 handbook vs. 2026-27 handbook | Identical for every title in Olympia's data |
| Community Knox totals: recomputed from their listed rows vs. totals stated on their sheets | Exact match in 2020-21 ($11,431,533), 2023-24 ($14,300,783), 2025-26 ($14,475,281). A first version added the sheet's own total row and doubled the sum; found and fixed |
| Handoff figures for the community list | The $11.43M belongs to 2020-21, not 2019-20; 2025-26 is $14.48M, not $14.8M |
| Privacy audit of published tables | No name columns; no person keys; pay measures blank where fewer than 5 people (applies in some or all years to Superintendent, Deputy/Assist. Supt., elementary vice principal, other school admin., physical therapist, social worker, substitute teacher, and on-leave rows); flow counts of 1 to 4 shown as "<5" |
| Viewer renders without script errors, desktop and 390 px phone width, all toggles exercised | Pass |
| Community lists matched to S-275 by name (locally; counts only kept) | 2020-21: 91 of 95 found, 2023-24: 103 of 110, 2025-26: 92 of 102. Every found person's salary agreed with S-275 within 1%. Unmatched 4, 7 and 10 not chased |
| Conventional-group FTE sums equal all-staff FTE, every year | Passes by construction (every title maps to exactly one group); checked in viewer table |
| Location split: school + district office/clerical/technical/professional equals combined, 2022-23 on | 2024-25: 42.8+33.4 office, 1.0+11.0 technical, 9.2+10.9 professional; matches combined |
| Community list vs S-275 district location (2023-24, 2025-26) | 94 of 110 and 85 of 102 listed people are district-coded; 9 and 7 are coded to a school; 7 and 10 not found. District-coded rows not on their list: bus drivers, trades/laborers/custodial/food service, aides/therapists/teachers, and some managers/office/technical |
| Do 2022-23 district-coded staff stay district-coded? | Of 168 FTE (non-bus), 27 FTE are coded only to a school by 2025-26, 51 FTE not on the list, 89 FTE still district-coded. Part of the tier-1 decline is recoding |
| Could 2022-23 locations be carried back to earlier years? | No: 24 of 95 people on the 2020-21 community list were absent from 2022-23 S-275 and 65 were district-coded; carrying back would miss about a quarter |

## Not yet checked
- F-196 totals against OSPI's published 10-year historical detail.
- Whether October enrollment instead of the annual average changes the per-student figures (E1); expected change is about 0.5%.
- S-275 duty-code definitions for 2015-16 to 2017-18 (no handbook on hand; S5).
