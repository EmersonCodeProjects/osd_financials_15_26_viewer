# Sources

Status: `have` = obtained and used; `cleaned` = in `clean_data_OSD/`. Raw files are not stored in this repository (see README).

| Data | Source | Years | Gives us | Status |
|---|---|---|---|---|
| Staff by position, FTE, salary, benefits | OSPI S-275 person-level personnel data files https://ospi.k12.wa.us/safs-data-files  | 2015-16 to 2025-26 | Headcount/FTE and pay by duty title; all 11 years downloaded (Olympia rows extracted) | cleaned
| Duty code definitions | OSPI https://ospi.k12.wa.us/sites/default/files/2026-09/s-275_handbook_2026-27.pdf; [duty code appendix](https://ospi.k12.wa.us/sites/default/files/2025-02/appendix_2024-25.docx); https://ospi.k12.wa.us/sites/default/files/2022-12/b113-18attach1.pdf | 2026-27 (applied to all years) and 2018-19 (compared) | Duty title definitions used to map titles to categories (S4, S5) | have
| Actual spending and revenue (F-196) | OSPI statewide Access databases and CSV exports https://ospi.k12.wa.us/safs-data-files | 2014-15 to 2024-25 | General fund expenditures by program, activity, object; revenues by source | have; Olympia extracted 
| Enrollment | District enrollment dashboard (annual average headcount; see clean_data_OSD/enrollment.csv) https://osd.wednet.edu/index.php?pageID=smartSiteFeed&psqFeed=true&articleID=82704166 | 2009-10 to 2026-27 | Annual average headcount | have
| State employee general wage increases | Office of Financial Management https://ofm.wa.gov/wp-content/uploads/2026/05/Legislative_GenWageAdjustments_History.pdf | 2015 to 2026 | Benchmark | cleaned
| Seattle-area CPI-U | Washington State Economic and Revenue Forecast https://erfc.wa.gov/sites/default/files/2026-10/sep26pub.pdf | 2015 to 2026 | Inflation adjustment | cleaned (2026 is a forecast)
| District's stated central administration figure (4.88%) | OSD Long-Term Planning FAQs (Oct. 22 FAQ) https://www.osd.wednet.edu/long-term-planning-faqs | year and base not stated | Shown beside our own measures of central administration | have |
| Community group spreadsheets | Provided by community members. Available upon request - contains staff names | varies | Their prior pulls; check against OSPI | have

## Pay benchmarks (Nov. 10, 2026)
- Governor and State Superintendent of Public Instruction salary schedules: https://lawfilesext.leg.wa.gov/biennium/2019-20/Htm/Bills/Session%20Laws/House/2019SALARYSCHEDULE.SL.htm ; https://lawfilesext.leg.wa.gov/biennium/2021-22/Pdf/Bills/Session%20Laws/House/2021SALARYSCHEDULE.SL.pdf ; https://lawfilesext.leg.wa.gov/biennium/2023-24/Pdf/Bills/Session%20Laws/House/SALAR.SL.pdf ; https://salaries.wa.gov/sites/default/files/public/2025%202026%20Final%20Salary%20Schedule.pdf
- OFM agency head tables: https://salaries.wa.gov/sites/default/files/public/2020%20Agency%20Heads%20vs%20Elected%20Officials%20Salaries.pdf ; https://salaries.wa.gov/sites/default/files/public/2024%20Agency%20Heads%20vs%20Elected%20Officials%20Salaries.pdf
- Commission vote to recommend no governor raise, Oct. 15, 2026 (not final): https://www.opb.org/article/2026/10/16/citizen-panel-rejects-pay-hike-for-washington-governor/
- Statewide S-275 personnel files 2015-16 to 2025-26 (OSPI), used without names for peer comparisons.

## State employee pay and community workbook (Nov. 10, 2026)
- WFSE General Government collective bargaining agreements 2015-17, 2017-19, 2019-21, 2021-23, 2023-25: general wage increases are in the compensation article (s.42.1) and step rules in s.42.9; salary schedules in the appendices.
- 2025-26 and 2026-27 represented raises (3% July 2025, 2% July 2026): OFM, Summary of Major Elements of 2025-27 Collective Bargaining Agreements, https://ofm.wa.gov/sites/default/files/public/legacy/agencycommunications/FY2025/Summary%20of%20Major%20Elements%20of%202025-27%20Collective%20Bargaining%20Agreements.pdf (agreement text itself not in the folder). Available: https://wfse.org/all-contracts/General-Government-Contracts ; https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/labor/agreements/23-25/wfse_gg.pdf ; https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/labor/agreements/21-23/wfse_gg.pdf ; https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/labor/agreements/19-21/wfse_gg.pdf ; https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/legacy/labor/agreements/17-19/wfse_gg.pdf ; https://ofm.wa.gov/wp-content/uploads/sites/default/files/public/legacy/labor/agreements/15-17/wfse_gg.pdf 
- Community workbook "OSD Admin Data-For Sharing.xlsx", compiled by Janel Bistrika (2026); credited with the compiler's permission (updated; names removed; compiler contact details in the file are not reproduced here). Decision C6.
