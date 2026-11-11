# Sources

Status: `have` = obtained and used; `cleaned` = in `clean_data_OSD/`; `todo` = not yet obtained. Raw files are not stored in this repository (see README).

| Data | Source | Years | Gives us | Status |
|---|---|---|---|---|
| Staff by position, FTE, salary, benefits | OSPI S-275 personnel data and summary reports ([Personnel Summary Reports](https://ospi.k12.wa.us/index.php/policy-funding/school-apportionment/school-publications/personnel-summary-reports); e.g. [2024-25 summary](https://ospi.k12.wa.us/sites/default/files/2025-02/allpersonnelsummaryreport2024-25.pdf)) | 2015-16 to 2025-26 | Headcount/FTE and pay by duty title; all 11 years downloaded (Olympia rows extracted) | have |
| Duty code definitions | OSPI [S-275 handbook 2026-27](https://ospi.k12.wa.us/sites/default/files/2026-09/s-275_handbook_2026-27.pdf); [duty code appendix](https://ospi.k12.wa.us/sites/default/files/2025-02/appendix_2024-25.docx) | current; check older handbooks for code changes | Category mapping | titles mapped (handbook not reachable; definitions marked verify) |
| Actual spending and revenue (F-196) | OSPI [Financial Reporting Summary](https://ospi.k12.wa.us/index.php/policy-funding/school-apportionment/school-publications/financial-reporting-summary), statewide Access databases and CSV exports | 2014-15 to 2024-25 | General fund expenditures by program, activity, object; revenues by source | have; Olympia extracted |
| 10-year F-196 history | Same page, Section One "F-196 Historical Data Detail" (Excel) | 10 years | Cross-check of district tables | todo |
| Budgets (F-195) | District budget documents (2020-21 to 2026-27) | budget years | Plans only; use for 2025-26 and later where actuals are not out | have |
| Enrollment | District enrollment dashboard (annual average headcount; see clean_data_OSD/enrollment.csv) | 2009-10 to 2026-27 | Annual average headcount | have |
| State salary inflation factor (IPD) | Legislature / OSPI budget documents | 2015 to 2026 | Benchmark for school pay growth | cleaned (year alignment to confirm) |
| State employee general wage increases | Office of Financial Management | 2015 to 2026 | Benchmark | cleaned |
| Thurston County employee wage increases | County salary schedules or bargaining agreements | 2015 to 2026 | Benchmark | todo |
| Seattle-area CPI-U | Bureau of Labor Statistics | 2015 to 2026 | Inflation adjustment | cleaned (2026 is a forecast) |
| Community group spreadsheets | Provided by community members | varies | Their prior pulls; check against OSPI | have; check in progress |

Notes
- Prefer actuals (F-196) over budgets (F-195) wherever both exist.
- 2019-20 and 2020-21 summary tables may be grouped by enrollment band or county; confirm district-level rows exist.
- S-275 is an October snapshot of the school year; record that on the page.


## Pay benchmarks (Nov. 10, 2026)
- Governor and State Superintendent of Public Instruction salary schedules: https://lawfilesext.leg.wa.gov/biennium/2019-20/Htm/Bills/Session%20Laws/House/2019SALARYSCHEDULE.SL.htm ; https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bills/Session%20Laws/House/2021SALARYSCHEDULE.SL.pdf ; https://lawfilesext.leg.wa.gov/biennium/2023-24/Pdf/Bills/Session%20Laws/House/SALAR.SL.pdf ; https://salaries.wa.gov/sites/default/files/public/2025%202026%20Final%20Salary%20Schedule.pdf
- OFM agency head tables: https://salaries.wa.gov/sites/default/files/public/2020%20Agency%20Heads%20vs%20Elected%20Officials%20Salaries.pdf ; https://salaries.wa.gov/sites/default/files/public/2024%20Agency%20Heads%20vs%20Elected%20Officials%20Salaries.pdf
- Commission vote to recommend no governor raise, Oct. 15, 2026 (not final): https://www.opb.org/article/2026/10/16/citizen-panel-rejects-pay-hike-for-washington-governor/
- Statewide S-275 personnel files 2015-16 to 2025-26 (OSPI), used without names for peer comparisons.

## State employee pay and community workbook (Nov. 10, 2026)
- WFSE General Government collective bargaining agreements 2015-17, 2017-19, 2019-21, 2021-23, 2023-25: general wage increases are in the compensation article (s.42.1) and step rules in s.42.9; salary schedules in the appendices.
- 2025-26 and 2026-27 represented raises (3% July 2025, 2% July 2026): OFM, Summary of Major Elements of 2025-27 Collective Bargaining Agreements, https://ofm.wa.gov/sites/default/files/public/legacy/agencycommunications/FY2025/Summary%20of%20Major%20Elements%20of%202025-27%20Collective%20Bargaining%20Agreements.pdf (agreement text itself not in the folder).
- WMS Inclusion & Job Value Assessment Evaluator's Handbook v1.6: points-to-band table only (Band 1 437-501, Band 2 560-724, Band 3 618-856, Band 4 995-1187); no dollar ranges.
- Community workbook "OSD Admin Data-For Sharing.xlsx", compiled by Janel Bistrika (2026); credited with the compiler's permission (updated; names removed; compiler contact details in the file are not reproduced here). Decision C6.
- Not yet obtained: the state's annual employee salary database (fiscal.wa.gov), which could be used to estimate WMS band pay ranges.
