"""Build aggregate clean tables for the OSD viewer (Stage 1).
Inputs  (paths given on the command line):
  --s275   person-level Olympia rows from extract_s275.py (LOCAL ONLY: has names)
  --f196   folder holding f196_gf_expenditures.csv and f196_gf_revenues.csv
  --maps   folder holding f196_code_map.csv, s275_title_map.csv, benchmarks.csv
  --enroll 2009_2026_OSD_Enrollment.xlsx
  --knox   Knox Adminstration Spreadsheets.xlsx   (community file, EXTERNAL; only totals are used)
  --out    output folder
Outputs hold NO names. Decision IDs refer to DECISIONS_AND_INFERENCES.md.
"""
import argparse, os, re
import pandas as pd, openpyxl

DIST, CODE = 'Olympia', '34111'
MIN_N = 5   # P4: cells with fewer than 5 people are suppressed

def tidy(rows, cols):
    return pd.DataFrame(rows, columns=cols)

def staffing(s275, tmap, out):
    d = pd.read_csv(s275)
    d['fte'] = d.cert_fte.fillna(0) + d.clas_fte.fillna(0)                      # S2
    d['comp'] = d.total_salary + d.insurance_benefits + d.mandatory_benefits    # S3
    d['person'] = d.last_name.str.upper().str.strip() + '|' + d.first_name.str.upper().str.strip()  # S10
    d = d.merge(tmap[['duty_title', 'viewer_category', 'subcategory', 'flow_group']], on='duty_title', how='left')
    assert d.viewer_category.notna().all(), 'unmapped duty title'               # S4
    recs = []
    def add(level, key, g):
        for sy, x in g.groupby('school_year'):
            n = x.person.nunique()
            sup = n < MIN_N                                                      # P4
            base = dict(district=DIST, county_district_code=CODE, school_year=sy, topic='staffing', level=level, category=key)
            recs.append({**base, 'measure': 'fte', 'value': round(x.fte.sum(), 3), 'derivation': 'REGROUPED' if level != 'title' else 'RAW', 'decision_ids': 'S2,S4', 'suppressed': ''})
            recs.append({**base, 'measure': 'rows', 'value': len(x), 'derivation': 'RAW', 'decision_ids': 'S8', 'suppressed': ''})
            recs.append({**base, 'measure': 'headcount', 'value': n, 'derivation': 'INFERRED', 'decision_ids': 'S10', 'suppressed': ''})
            for m, c, dec, der in [('salary_total', 'total_salary', 'S4', 'REGROUPED' if level != 'title' else 'RAW'), ('comp_total', 'comp', 'S3', 'CALCULATED')]:
                recs.append({**base, 'measure': m, 'value': '' if sup else round(x[c].sum(), 0), 'derivation': der, 'decision_ids': dec + ',P4', 'suppressed': 'Y' if sup else ''})
    for t, g in d.groupby('duty_title'): add('title', t, g)
    for c, g in d.groupby('viewer_category'): add('category', c, g)
    add('category', 'all_staff', d)
    t = tidy(recs, list(recs[0].keys())); t.to_csv(f'{out}/staffing.csv', index=False)
    return d

def enrollment(path, out):
    wb = openpyxl.load_workbook(path, data_only=True)
    rows = []; cur = None
    for r in list(wb.active.iter_rows(values_only=True))[1:]:
        if r[0]: cur = r[0]
        rows.append((cur, r[1], r[2], r[4]))
    e = pd.DataFrame(rows, columns=['yr', 'mon', 'count', 'fte'])
    e['school_year'] = e.yr.str[:4] + '-' + e.yr.str[-2:]
    recs = []
    for sy, x in e.groupby('school_year'):
        full = len(x) >= 10   # E2: 2026-27 is September only
        base = dict(district=DIST, county_district_code=CODE, school_year=sy, topic='enrollment')
        recs.append({**base, 'measure': 'headcount_annual_avg', 'value': round(x['count'].mean(), 1), 'derivation': 'CALCULATED', 'decision_ids': 'E1,E3', 'note': '' if full else 'provisional: September only (E2)'})
        o = x[x.mon == 'October']['count']
        recs.append({**base, 'measure': 'headcount_october', 'value': float(o.iloc[0]) if len(o) else '', 'derivation': 'RAW', 'decision_ids': 'E1', 'note': ''})
        recs.append({**base, 'measure': 'fte_annual_avg', 'value': round(x['fte'].mean(), 1), 'derivation': 'CALCULATED', 'decision_ids': 'E3', 'note': '' if full else 'provisional: September only (E2)'})
    pd.DataFrame(recs).to_csv(f'{out}/enrollment.csv', index=False)
    return pd.DataFrame(recs)

def finance(f196, cmap, out):
    ex = pd.read_csv(f'{f196}/f196_gf_expenditures.csv', dtype={'program': str, 'activity': str, 'object': str})
    rv = pd.read_csv(f'{f196}/f196_gf_revenues.csv', dtype={'revenue_code': str})
    m = {t: dict(zip(g.code.astype(str), g.viewer_group)) for t, g in cmap.groupby('code_type')}
    ex['program_group'] = ex.program.map(m['program']); ex['activity_group'] = ex.activity.map(m['activity']); ex['object_group'] = ex.object.map(m['object'])
    assert ex[['program_group', 'activity_group', 'object_group']].notna().all().all()   # F4
    recs = []
    for gt, col in [('program_group', 'program_group'), ('activity_group', 'activity_group'), ('object_group', 'object_group')]:
        for (sy, g), x in ex.groupby(['school_year', col]):
            recs.append(dict(district=DIST, county_district_code=CODE, school_year=sy, topic='expenditure', group_type=gt, group=g, dollars=round(x.amount.sum(), 2), dollars_basis='nominal', derivation='REGROUPED', decision_ids='F1,F2,F4'))
    for sy, x in ex.groupby('school_year'):
        recs.append(dict(district=DIST, county_district_code=CODE, school_year=sy, topic='expenditure', group_type='total', group='general_fund_total', dollars=round(x.amount.sum(), 2), dollars_basis='nominal', derivation='RAW', decision_ids='F1,F2,F6'))
        a = x[x.activity.isin(['11', '12', '13', '14', '15'])]
        recs.append(dict(district=DIST, county_district_code=CODE, school_year=sy, topic='expenditure', group_type='central_admin_measure', group='A_general_administration_activities_11_15', dollars=round(a.amount.sum(), 2), dollars_basis='nominal', derivation='REGROUPED', decision_ids='F7,C1'))
    pd.DataFrame(recs).to_csv(f'{out}/f196_expenditures.csv', index=False)
    names = {'1000': 'local_taxes', '2000': 'local_non_tax', '3000': 'state_general_purpose', '4000': 'state_special_purpose', '5000': 'federal_general_purpose', '6000': 'federal_special_purpose', '7000': 'other_school_districts', '8000': 'other_entities', '9000': 'other_financing_sources'}
    tot = rv[rv.level == 'total'].copy(); tot['group'] = tot.revenue_code.map(names); assert tot.group.notna().all()   # F3
    r = [dict(district=DIST, county_district_code=CODE, school_year=a.school_year, topic='revenue', group=a.group, revenue_code=a.revenue_code, dollars=round(a.amount, 2), dollars_basis='nominal', derivation='RAW', decision_ids='F1,F2,F3') for a in tot.itertuples()]
    covid = {f'6{k}1{d}' for k in (1, 2, 3) for d in (1, 2, 3, 4, 8, 9)}   # F8: 6x11-6x14, 6x18, 6x19 (SLFRF, ESSER II/III, learning loss, reserved, CARES other)
    cv = rv[(rv.level == 'detail') & rv.revenue_code.isin(covid)].groupby('school_year').amount.sum()
    for sy in sorted(tot.school_year.unique()):
        r.append(dict(district=DIST, county_district_code=CODE, school_year=sy, topic='revenue', group='of_which_covid_relief_federal', revenue_code='6x11-6x19', dollars=round(float(cv.get(sy, 0)), 2), dollars_basis='nominal', derivation='REGROUPED', decision_ids='F8'))
    pd.DataFrame(r).to_csv(f'{out}/f196_revenues.csv', index=False)
    return ex, tot

def central_admin(d, ex, knox, out):
    recs = []
    def rec(sy, mid, label, fte, people, dollars, basis, src, der, dec, note=''):
        recs.append(dict(school_year=sy, measure_id=mid, label=label, fte=fte, people=people, dollars=dollars, dollars_basis=basis, source=src, derivation=der, decision_ids=dec, note=note))
    for sy, x in d.groupby('school_year'):
        b = x[x.viewer_category == 'district_administration']
        rec(sy, 'B', 'District administrator titles (11x-13x)', round(b.fte.sum(), 2), b.person.nunique(), '' if b.person.nunique() < MIN_N else round(b.comp.sum(), 0), 'total_compensation', 'S-275', 'REGROUPED', 'S4,S6,C1', 'pay blank when fewer than 5 people (P4)' if b.person.nunique() < MIN_N else '')
        b2 = x[x.viewer_category.isin(['district_administration', 'classified_director_supervisor'])]
        rec(sy, 'B2', 'B plus classified Director/Supervisor (99y)', round(b2.fte.sum(), 2), b2.person.nunique(), round(b2.comp.sum(), 0), 'total_compensation', 'S-275', 'REGROUPED', 'S4,S6,C1')
        if sy >= '2022-23':
            dl = x[x.location_code == 1035]
            rec(sy, 'D', 'Everyone at district location code 1035', round(dl.fte.sum(), 2), dl.person.nunique(), round(dl.comp.sum(), 0), 'total_compensation', 'S-275', 'REGROUPED', 'S9,C1', 'location column exists from 2022-23 only')
    tot = ex.groupby('school_year').amount.sum()
    for sy, v in ex[ex.activity.isin(['11', '12', '13', '14', '15'])].groupby('school_year').amount.sum().items():
        rec(sy, 'A', 'General administration activities 11-15 (spending)', '', '', round(v, 2), 'expenditure', 'F-196', 'REGROUPED', 'F7,C1', f'{v / tot[sy] * 100:.2f}% of general fund')
    # C: community Knox lists (EXTERNAL, C2). Use the totals the community sheets state; recompute from listed rows as a check.
    wb = openpyxl.load_workbook(knox, data_only=True)
    def stated(sh, sy):
        rows = list(wb[sh].iter_rows(values_only=True))
        hdr = next(i for i, r in enumerate(rows) if r and any(isinstance(c, str) and c.strip().upper() == 'NAME' for c in r))
        h = [str(c).strip().upper() if c else '' for c in rows[hdr]]
        ni = h.index('NAME'); ic = next(i for i, c in enumerate(h) if c.startswith('TOTAL COMPENSATION'))
        listed = [r for r in rows[hdr + 1:] if r and isinstance(r[ni], str) and not r[ni].strip().upper().startswith(('TOTAL', 'TBD', '#', 'MISSING'))]
        with_pay = [r for r in listed if isinstance(r[ic], (int, float))]
        recomputed = round(sum(r[ic] for r in with_pay), 0)
        n_stated = tot_stated = None
        fr = list(wb[sh.replace('Unformatted', 'Formatted')].iter_rows(values_only=True)) if sh.replace('Unformatted', 'Formatted') in wb.sheetnames else []
        for r in rows + fr:
            cells = [c for c in (r or []) if c is not None]
            txt = ' '.join(str(c) for c in cells)
            m = re.search(r'Total # of Knox Employees \(not including vacancies: (\d+)', txt) or re.search(r'# Employees: (\d+)', txt)
            if m and n_stated is None: n_stated = int(m.group(1))
            if 'TOTAL BY ALL DEPARTMENTS' in txt.upper() or txt.startswith('# Employees'):
                nums = [float(c) for c in cells if re.fullmatch(r'\d{6,}', str(c))]
                if nums: tot_stated = int(nums[-1])
            if r and r[0] is None and len(cells) == 2 and all(re.fullmatch(r'\d{6,}', str(c)) for c in cells): tot_stated = int(cells[-1])
        return n_stated, tot_stated, recomputed, len(with_pay), len(listed)
    for sh, sy in [('2020-21 Data (Unformatted)', '2020-21'), ('2023-24 Data (Unformatted)', '2023-24'), ('2025-26 Data (Unformatted)', '2025-26')]:
        n, t, rc, nwp, nl = stated(sh, sy)
        t = UPD_TOT.get(sy, t)   # C6
        rec(sy, 'C', 'Community Knox directory match', '', n, t, 'total_compensation', 'community spreadsheet (stated totals)', 'EXTERNAL', 'C1,C2', f'recomputed from listed rows (earlier workbook version, before C6 update) with S-275 pay: ${rc:,.0f} for {nwp} of {nl} listed; rest had no S-275 data or are vacancies')
    rec('2025-26', 'district_stated', "District's stated central administration share", '', '', '', 'share_of_budget', 'Oct. 22 FAQ', 'EXTERNAL', 'C3', '4.88%; year and base not stated; basis requested')
    pd.DataFrame(recs).to_csv(f'{out}/central_admin_measures.csv', index=False)


# C6: the community workbook was updated (file 'OSD Admin Data-For Sharing.xlsx', names removed, 2023-24 sheet dropped). Changes found by comparing row by row:
# three rows now count only part of a person's pay as administrative. Matching still uses the earlier file (it has names); stated totals are replaced by the new file's totals.
UPD_TOT = {'2025-26': 14215213, '2020-21': 11333072}
UPD_DELTA = {'2025-26': 215736*2 - 75699.6 - 95704.8, '2020-21': 176102 - 77640.8}

DISTRICT_LOC = 1035   # S9: S-275 location code for the district office; column exists from 2022-23
PARENT = {'front_office': ('student_facing', 'front_office'), 'classroom_teachers': ('student_facing', 'teachers'), 'paraeducators': ('student_facing', 'teachers'),
          'student_services': ('student_facing', 'teachers'), 'support_staffing': ('student_facing', 'support_staffing'), 'super': ('district', 'super'),
          'managers': ('district', 'managers'), 'office_tech_prof': ('unplaced', 'office_tech_prof'), 'on_leave': ('on_leave', 'on_leave')}
PARENT_LOC = {'front_office': ('student_facing', 'front_office'), 'school_clerical': ('student_facing', 'front_office'), 'classroom_teachers': ('student_facing', 'teachers'),
              'paraeducators': ('student_facing', 'teachers'), 'student_services': ('student_facing', 'teachers'), 'support_staffing': ('student_facing', 'support_staffing'),
              'school_tech_prof': ('student_facing', 'support_staffing'), 'super': ('district', 'super'), 'managers': ('district', 'managers'),
              'district_office_staff': ('district', 'staff'), 'district_other_coded': ('district', 'staff'), 'on_leave': ('on_leave', 'on_leave')}

ITIN = ['Spch.-Lang. Path./Audio.', 'Occupational Therapist', 'Physical Therapist', 'Psychologist', 'Nurse', 'Social Worker', 'Counselor']  # G11: itinerant student services stay student-facing at the district location

def add_building_group(d):
    """G8: building-based group for each row (meaningful from 2022-23). Rule: super and manager TITLES stay district. Otherwise a row coded to the
    district location is district, except Operators (bus drivers), which are student-facing support staffing. A row coded to a school keeps its
    title group; school-coded Office/Clerical is school office (front office), school-coded Technical/Professional is school technical."""
    d = d.copy(); atd = d.location_code == DISTRICT_LOC; fg = d.flow_group
    bg = fg.copy()
    bg[atd & (fg == 'office_tech_prof')] = 'district_office_staff'
    bg[atd & ~fg.isin(['super', 'managers', 'office_tech_prof', 'on_leave']) & (d.duty_title != 'Operator')] = 'district_other_coded'
    bg[atd & (d.duty_title == 'Operator')] = 'support_staffing'
    bg[atd & d.duty_title.isin(ITIN)] = 'student_services'
    bg[~atd & (fg == 'office_tech_prof') & (d.duty_title == 'Office/Clerical')] = 'school_clerical'
    bg[~atd & (fg == 'office_tech_prof') & (d.duty_title != 'Office/Clerical')] = 'school_tech_prof'
    d['bgroup'] = bg
    return d

def grouped(d, out):
    """G1-G5, G8, G9: view=all_years is by job title only; view=located is building-based (2022-23 on)."""
    d = add_building_group(d); recs = []
    def emit(view, sub, side, grp, x, sy, dec):
        n = x.person.nunique(); sup = n < MIN_N
        base = dict(school_year=sy, view=view, side=side, group=grp, subgroup=sub)
        recs.append({**base, 'measure': 'fte', 'value': round(x.fte.sum(), 3), 'suppressed': '', 'derivation': 'REGROUPED', 'decision_ids': dec})
        recs.append({**base, 'measure': 'headcount', 'value': n, 'suppressed': '', 'derivation': 'INFERRED', 'decision_ids': dec + ',S10'})
        recs.append({**base, 'measure': 'comp_total', 'value': '' if sup else round(x.comp.sum(), 0), 'suppressed': 'Y' if sup else '', 'derivation': 'CALCULATED', 'decision_ids': dec + ',P4'})
    for (sy, fg), x in d.groupby(['school_year', 'flow_group']):
        side, grp = PARENT[fg]; emit('all_years', fg, side, grp, x, sy, 'G1,G2,G3,G5')
    for (sy, bg), x in d[d.school_year >= '2022-23'].groupby(['school_year', 'bgroup']):
        side, grp = PARENT_LOC[bg]; emit('located', bg, side, grp, x, sy, 'G8,S9')
    pd.DataFrame(recs).to_csv(f'{out}/staffing_grouped.csv', index=False)
    # nested non-student-facing tiers (G9)
    tr = []
    def tier(tid, label, x, sy, dec, der='REGROUPED'):
        n = x.person.nunique(); sup = n < MIN_N
        tr.append(dict(school_year=sy, tier=tid, label=label, fte=round(x.fte.sum(), 2), people=n, comp_total='' if sup else round(x.comp.sum(), 0), suppressed='Y' if sup else '', derivation=der, decision_ids=dec))
    for sy, x in d.groupby('school_year'):
        t3 = x[x.flow_group.isin(['super', 'managers'])]
        tier('3_managers_super', 'Superintendent, deputy/assistant, directors and supervisors (by job title)', t3, sy, 'G9,G2')
        if sy >= '2022-23':
            t2 = x[x.flow_group.isin(['super', 'managers']) | (x.bgroup == 'district_office_staff')]
            tier('2_office_staff_plus_managers_super', 'District office staff plus managers and superintendent', t2, sy, 'G9,G8,S9')
            tier('1_non_student_facing', 'Total non-student-facing: coded to the district location, excluding bus drivers and itinerant student services', x[(x.location_code == DISTRICT_LOC) & (x.duty_title != 'Operator') & ~x.duty_title.isin(ITIN)], sy, 'G9,G8,G11,S9')
            tier('0_district_location_incl_bus', 'Everyone coded to the district location, including bus drivers', x[x.location_code == DISTRICT_LOC], sy, 'G9,S9')
    pd.DataFrame(tr).to_csv(f'{out}/district_tiers.csv', index=False)
    lt = []
    for (sy, t), x in d[(d.location_code == DISTRICT_LOC)].groupby(['school_year', 'duty_title']):
        n = x.person.nunique(); lt.append(dict(school_year=sy, duty_title=t, flow_group=x.flow_group.iloc[0], fte=round(x.fte.sum(), 2), people='<5' if n < MIN_N else n, derivation='REGROUPED', decision_ids='G9,S9'))
    pd.DataFrame(lt).to_csv(f'{out}/district_location_titles.csv', index=False)
    # G10: where did the 2022-23 district-coded staff (excluding bus drivers) show up in later years?
    a = d[(d.school_year == '2022-23') & (d.location_code == DISTRICT_LOC) & (d.duty_title != 'Operator') & ~d.duty_title.isin(ITIN)]; pa = a.groupby('person').fte.sum(); fl = []
    for y in sorted(d.school_year.unique()):
        if y <= '2022-23': continue
        b = d[d.school_year == y]; bd = set(b[b.location_code == DISTRICT_LOC].person); bs = set(b[b.location_code != DISTRICT_LOC].person) - bd; ba = set(b.person)
        for st, ss in [('still_coded_to_district', bd), ('now_coded_to_a_school_only', bs), ('not_on_s275_list_that_year', set(pa.index) - ba)]:
            ks = [p for p in pa.index if p in ss]
            fl.append(dict(from_year='2022-23', to_year=y, status=st, people='<5' if len(ks) < MIN_N else len(ks), fte_in_2022_23='' if len(ks) < MIN_N else round(pa[ks].sum(), 1), derivation='INFERRED', decision_ids='G10,G11,P1,S10'))
    pd.DataFrame(fl).to_csv(f'{out}/district_location_flow.csv', index=False)
    return d

def community_match(d, knox, out):
    """C4, C5: compare the community's listed people with S-275 (names used LOCALLY for matching; only counts and dollars are written)."""
    norm = lambda s: re.sub(r'[^a-z ]', '', str(s).lower()).strip()
    dd = d.copy(); dd['ln'] = dd.last_name.map(norm); dd['fn'] = dd.first_name.map(norm); dd['k'] = dd.ln + '|' + dd.fn.str[:3]
    wb = openpyxl.load_workbook(knox, data_only=True); recs = []; comp = []; rec5 = []; extra = []
    _m = pd.read_csv(MAPFILE); fgmap = dict(zip(_m.duty_title, _m.flow_group))
    alias = {'Other District Admin': 'managers', 'Elementary Teacher': 'classroom_teachers', 'Deputy/Assistant Superintendent': 'super', 'Elementary Specialist Teacher': 'classroom_teachers', 'Speech Language Path/Audio.': 'student_services'}
    def fg_of(t):
        p = t.split(' (')[0].strip()
        if p in fgmap: return fgmap[p]
        if p in alias: return alias[p]
        if p.startswith(('Elementary Principal', 'Secondary Principal', 'Vice Principal')): return 'front_office'
        return 'unknown'
    def sup(n, v): return '' if n < MIN_N else round(v)
    for sh, sy in [('2020-21 Data (Unformatted)', '2020-21'), ('2023-24 Data (Unformatted)', '2023-24'), ('2025-26 Data (Unformatted)', '2025-26')]:
        rows = [[c for c in r if c is not None] for r in wb[sh].iter_rows(values_only=True) if r and any(isinstance(c, int) for c in r)]
        rows = [r for r in rows if len(r) >= 6 and isinstance(r[0], str)]
        x = dd[dd.school_year == sy]
        P = x.groupby(['ln', 'fn']).agg(sal=('total_salary', 'sum'), comp=('comp', 'sum'), fte=('fte', 'sum')).reset_index()
        n_m = n_pay = 0; lc = mc = sc = uc = 0.0; fte_lt = 0; keys = []; notfound_comp = 0.0
        for r in rows:
            nm = r[0]
            l, f = nm.split(',', 1) if ',' in nm else (' '.join(nm.split()[1:]), nm.split()[0])
            l, f = norm(l), norm(f); sal, tot = r[-4], r[-1]; lc += tot
            m = P[(P.ln == l) & (P.fn.str[:3] == f[:3])]
            if len(m) == 0 and l: m = P[(P.ln.str.split().str[-1] == l.split()[-1]) & (P.fn.str[:3] == f[:3])]
            g = fg_of(r[1]); comp.append((sy, g, tot))
            if len(m):
                n_m += 1; mc += tot; sc += m.comp.sum(); keys.append((m.iloc[0].ln + '|' + m.iloc[0].fn[:3], tot))
                n_pay += int(abs(sal - m.sal.sum()) <= 0.01 * max(sal, 1)); fte_lt += int(m.fte.sum() < 0.95)
            else: uc += tot
        lc -= UPD_DELTA.get(sy, 0)   # C6
        recs.append(dict(school_year=sy, listed_rows=len(rows), listed_total_compensation=round(lc), matched_to_s275=n_m, share_matched=round(n_m / len(rows), 3), pay_within_1pct_of_s275=n_pay,
                         matched_listed_compensation=round(mc), matched_s275_compensation=round(sc), unmatched_rows=len(rows) - n_m, unmatched_compensation=round(uc), matched_people_under_0_95_fte=fte_lt,
                         derivation='CALCULATED', decision_ids='C1,C2,C4'))
        if sy < '2022-23': continue
        # C5: reconcile the community list with the S-275 district location
        kd = set(x[x.location_code == DISTRICT_LOC].k); lk = {k for k, _ in keys}
        at_d = [(k, t) for k, t in keys if k in kd]; at_s = [(k, t) for k, t in keys if k not in kd]
        def R(line, side, n, fte, c): rec5.append(dict(school_year=sy, side=side, line=line, people=n, fte=round(fte, 2) if fte != '' else '', comp=sup(n, c) if c != '' else '', derivation='CALCULATED', decision_ids='C5,S9'))
        R('Community list: total', 'community', len(rows), '', lc)
        R('Community list: not found in S-275', 'community', len(rows) - n_m, '', uc)
        R('Community list: found, coded to a school', 'community', len(at_s), '', sum(t for _, t in at_s))
        R('Community list: found, coded to the district location', 'community', len(at_d), '', sum(t for _, t in at_d))
        xd = x[x.location_code == DISTRICT_LOC]; onl = xd[xd.k.isin(lk)]; offl = xd[~xd.k.isin(lk)]
        R('District-coded rows in S-275: total', 'ours', xd.person.nunique(), xd.fte.sum(), xd.comp.sum())
        R('District-coded rows: on the community list', 'ours', onl.person.nunique(), onl.fte.sum(), onl.comp.sum())
        grp = lambda r: ('Bus drivers (operators)' if r.duty_title == 'Operator' else 'Trades, laborers, custodial/food service' if r.duty_title in ('Crafts/Trades', 'Laborer', 'Service Worker') else
                         'Aides, therapists, speech-language, teachers' if r.flow_group in ('paraeducators', 'student_services', 'classroom_teachers') else 'Managers, office, technical, professional, other')
        offl = offl.copy(); offl['g'] = offl.apply(grp, axis=1)
        for g, y in offl.groupby('g'): R('District-coded rows not on the community list: ' + g, 'ours', y.person.nunique(), y.fte.sum(), y.comp.sum())
        # tier 2 plus community-listed people coded to a school (EXTERNAL overlay)
        t2p = set(x[x.flow_group.isin(['super', 'managers']) | (x.bgroup == 'district_office_staff')].k)
        add = x[x.k.isin({k for k, _ in at_s} - t2p)]
        base2 = x[x.flow_group.isin(['super', 'managers']) | (x.bgroup == 'district_office_staff')]
        both = pd.concat([base2, add]); n = both.person.nunique()
        extra.append(dict(school_year=sy, tier='2b_plus_community_listed_coded_to_school', label='Tier 2 plus people the community list places in the district building but S-275 codes to a school', fte=round(both.fte.sum(), 2), people=n,
                          comp_total=round(both.comp.sum()), suppressed='', derivation='EXTERNAL', decision_ids='G9,C5,S9'))
    pd.DataFrame(recs).to_csv(f'{out}/community_match.csv', index=False)
    pd.DataFrame(rec5).to_csv(f'{out}/community_recon.csv', index=False)
    t = pd.read_csv(f'{out}/district_tiers.csv'); pd.concat([t, pd.DataFrame(extra)]).to_csv(f'{out}/district_tiers.csv', index=False)
    cc = pd.DataFrame(comp, columns=['school_year', 'flow_group', 'comp']).groupby(['school_year', 'flow_group']).agg(rows=('comp', 'size'), compensation=('comp', 'sum')).reset_index()
    cc['compensation'] = cc.compensation.astype(object); cc.loc[cc.rows < MIN_N, 'compensation'] = ''
    cc['derivation'] = 'CALCULATED'; cc['decision_ids'] = 'C1,C4,G1'
    cc.to_csv(f'{out}/community_list_composition.csv', index=False)

def deflator(bench, out):
    cpi = bench[(bench.series == 'seattle_cpi') & (bench.measure == 'index_1982_84=1')].set_index('school_year').value.astype(float)
    ref = '2024-25'   # V4: latest year with actual spending and actual CPI
    # V4 / B1: price-level factor to reference-year dollars (multiply nominal dollars by factor)
    dfl = pd.DataFrame([dict(school_year=sy, seattle_cpi_index=round(v, 4), factor_to_ref_year_dollars=round(cpi[ref] / v, 5), ref_year=ref, derivation='CALCULATED', decision_ids='B1,B2,V4') for sy, v in cpi.items()])
    dfl.to_csv(f'{out}/deflator.csv', index=False)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for a in ['s275', 'f196', 'maps', 'enroll', 'knox', 'out']: ap.add_argument('--' + a, required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    tmap = pd.read_csv(f'{a.maps}/s275_title_map.csv'); cmap = pd.read_csv(f'{a.maps}/f196_code_map.csv', dtype=str)
    bench = pd.read_csv(f'{a.maps}/benchmarks.csv')
    d = staffing(a.s275, tmap, a.out)
    enr = enrollment(a.enroll, a.out)
    ex, tot = finance(a.f196, cmap, a.out)
    central_admin(d, ex, a.knox, a.out)
    d = grouped(d, a.out)
    MAPFILE = f'{a.maps}/s275_title_map.csv'
    community_match(d, a.knox, a.out)
    deflator(bench, a.out)
    print('done')
